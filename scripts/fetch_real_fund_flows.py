from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

EASTMONEY_CLIST_URL = "https://push2.eastmoney.com/api/qt/clist/get"
EASTMONEY_ULIST_URL = "https://push2.eastmoney.com/api/qt/ulist.np/get"
EASTMONEY_SUGGEST_URL = "https://searchapi.eastmoney.com/api/suggest/get"
EASTMONEY_REFERER = "https://data.eastmoney.com/bkzj/hy.html"
EASTMONEY_SUGGEST_TOKEN = "D43BF722C8E33BDC906FB84D85E326E8"
FIELDS = "f12,f14,f20,f21,f62,f184,f124"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Referer": EASTMONEY_REFERER,
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "close",
}


def _request_json(url: str, timeout: int = 20) -> dict:
    last_error: Exception | None = None
    curl_errors: list[str] = []
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.load(response)
        except Exception as exc:  # pragma: no cover - network retries.
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    curl = shutil.which("curl.exe") or shutil.which("curl")
    if curl:
        command = [
            curl,
            "--http1.1",
            "--compressed",
            "-sS",
            "-L",
            "-A",
            HEADERS["User-Agent"],
            "-e",
            HEADERS["Referer"],
            url,
        ]
        result = subprocess.run(command, capture_output=True, timeout=timeout, check=False)
        if result.returncode == 0 and result.stdout:
            try:
                return json.loads(result.stdout.decode("utf-8-sig"))
            except json.JSONDecodeError as exc:
                curl_errors.append(f"curl JSON decode failed: {exc}")
        else:
            stderr = result.stderr.decode("utf-8", errors="ignore").strip()
            curl_errors.append(f"curl exit {result.returncode}: {stderr}")
    detail = f" Last error: {last_error}." if last_error else ""
    if curl_errors:
        detail += " " + " ".join(curl_errors)
    raise RuntimeError(f"Failed to fetch Eastmoney fund flow data: {url}.{detail}") from last_error


def _normalise_board_frame(rows: list[dict]) -> pd.DataFrame:
    frame = pd.DataFrame(rows).rename(
        columns={
            "f12": "board_code",
            "f14": "board_name",
            "f20": "total_market_cap",
            "f21": "free_float_market_cap",
            "f62": "main_net_inflow",
            "f184": "main_net_inflow_ratio",
            "f124": "update_timestamp",
        }
    )
    expected_columns = [
        "board_code",
        "board_name",
        "total_market_cap",
        "free_float_market_cap",
        "main_net_inflow",
        "main_net_inflow_ratio",
        "update_timestamp",
    ]
    for column in expected_columns:
        if column not in frame.columns:
            frame[column] = pd.NA
    numeric_columns = ["total_market_cap", "free_float_market_cap", "main_net_inflow", "main_net_inflow_ratio", "update_timestamp"]
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["board_code"] = frame["board_code"].astype(str).str.strip().str.upper()
    frame["board_name"] = frame["board_name"].astype(str).str.strip()
    return frame[expected_columns]


def _chunks(values: list[str], size: int) -> list[list[str]]:
    return [values[index : index + size] for index in range(0, len(values), size)]


def _split_field(value) -> list[str]:
    if value is None or pd.isna(value):
        return []
    return [item.strip() for item in str(value).replace("，", ";").split(";") if item.strip()]


def _split_board_codes(value) -> list[str]:
    codes = []
    for item in _split_field(value):
        code = item.upper().replace("90.", "").strip()
        if code:
            codes.append(code)
    return list(dict.fromkeys(codes))


def fetch_eastmoney_boards(page_size: int = 50, strict: bool = False) -> tuple[pd.DataFrame, list[str]]:
    rows: list[dict] = []
    warnings: list[str] = []
    page = 1
    total: int | None = None
    while total is None or len(rows) < total:
        url = (
            f"{EASTMONEY_CLIST_URL}?pn={page}&pz={page_size}&po=1&np=1"
            "&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2"
            f"&fid=f62&fs=m:90+t:2&fields={FIELDS}"
        )
        try:
            payload = _request_json(url)
        except RuntimeError as exc:
            if strict or not rows:
                raise
            warnings.append(str(exc))
            break
        data = payload.get("data") or {}
        total = int(data.get("total") or 0)
        diff = data.get("diff") or []
        rows.extend(diff)
        if not diff:
            break
        page += 1

    return _normalise_board_frame(rows), warnings


def fetch_eastmoney_boards_by_code(codes: list[str], strict: bool = True) -> tuple[pd.DataFrame, list[str]]:
    rows: list[dict] = []
    warnings: list[str] = []
    clean_codes = list(dict.fromkeys(code for code in codes if code))
    for chunk in _chunks(clean_codes, 80):
        secids = ",".join(f"90.{code}" for code in chunk)
        url = f"{EASTMONEY_ULIST_URL}?fltt=2&invt=2&fields={FIELDS}&secids={secids}"
        try:
            payload = _request_json(url)
        except RuntimeError as exc:
            if strict:
                raise
            warnings.append(str(exc))
            continue
        diff = (payload.get("data") or {}).get("diff") or []
        rows.extend(diff)
    return _normalise_board_frame(rows), warnings


def resolve_eastmoney_board_code(name: str) -> tuple[str | None, str | None]:
    if not name:
        return None, None
    url = f"{EASTMONEY_SUGGEST_URL}?input={quote(name)}&type=14&token={EASTMONEY_SUGGEST_TOKEN}"
    payload = _request_json(url)
    rows = ((payload.get("QuotationCodeTable") or {}).get("Data")) or []
    board_rows = [
        row
        for row in rows
        if row.get("Classify") == "BK" or str(row.get("QuoteID") or "").startswith("90.")
    ]
    exact = [row for row in board_rows if str(row.get("Name") or "").strip() == name]
    candidate = exact[0] if exact else (board_rows[0] if board_rows else None)
    if not candidate:
        return None, None
    return str(candidate.get("Code") or "").upper(), str(candidate.get("Name") or "").strip()


def _timestamp_date(value: float | int | None) -> str:
    if pd.isna(value):
        return datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
    return datetime.fromtimestamp(float(value), tz=ZoneInfo("Asia/Shanghai")).date().isoformat()


def _mapping_value(row, name: str, default: str = ""):
    return getattr(row, name, default) if hasattr(row, name) else default


def build_real_flow_files(boards: pd.DataFrame, mapping: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    board_code_set = set(boards["board_code"].dropna().astype(str))
    board_name_set = set(boards["board_name"].dropna().astype(str))
    flow_rows: list[dict] = []
    size_rows: list[dict] = []
    source_rows: list[dict] = []
    missing_rows: list[dict] = []

    for row in mapping.itertuples(index=False):
        asset_id = str(row.id)
        codes = _split_board_codes(_mapping_value(row, "board_codes"))
        names = _split_field(_mapping_value(row, "board_names"))
        if codes:
            matched = boards[boards["board_code"].isin(codes)].copy()
            order = {code: index for index, code in enumerate(codes)}
            matched["_order"] = matched["board_code"].map(order)
            matched = matched.sort_values("_order").drop(columns=["_order"])
        else:
            matched = boards[boards["board_name"].isin(names)].copy() if names else pd.DataFrame()
        missing_codes = [code for code in codes if code not in board_code_set]
        missing_names = [name for name in names if name not in board_name_set]
        if matched.empty:
            missing_rows.append(
                {
                    "id": asset_id,
                    "missing_board_codes": ";".join(codes),
                    "missing_board_names": ";".join(names),
                }
            )
            continue

        date_value = _timestamp_date(matched["update_timestamp"].dropna().max())
        flow_amount = float(matched["main_net_inflow"].sum())
        total_size = float(matched["total_market_cap"].sum())
        board_codes = ";".join(matched["board_code"].astype(str).tolist())
        board_names = ";".join(matched["board_name"].astype(str).tolist())

        flow_rows.append({"date": date_value, "id": asset_id, "flow_amount": flow_amount})
        size_rows.append({"date": date_value, "id": asset_id, "total_size": total_size})
        notes = str(_mapping_value(row, "notes")).strip()
        missing_note_parts = []
        if missing_codes:
            missing_note_parts.append(f"缺失代码：{';'.join(missing_codes)}")
        if missing_names:
            missing_note_parts.append(f"名称未完全匹配：{';'.join(missing_names)}")
        if missing_note_parts:
            notes = f"{notes}；{';'.join(missing_note_parts)}" if notes else "；".join(missing_note_parts)
        source_rows.append(
            {
                "id": asset_id,
                "flow_source": "东方财富数据中心-板块资金流向公开网页接口 f62：主力净流入",
                "total_size_source": "东方财富行情公开网页接口 f20：总市值",
                "source_url": EASTMONEY_REFERER,
                "currency": "CNY",
                "board_codes": board_codes,
                "board_names": board_names,
                "notes": notes or "自动抓取东方财富公开网页接口",
            }
        )

    return pd.DataFrame(flow_rows), pd.DataFrame(size_rows), pd.DataFrame(source_rows), pd.DataFrame(missing_rows)


def _resolve_codes_from_mapping(mapping: pd.DataFrame) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    codes: list[str] = []
    for row in mapping.itertuples(index=False):
        row_codes = _split_board_codes(_mapping_value(row, "board_codes"))
        if row_codes:
            codes.extend(row_codes)
            continue
        for name in _split_field(_mapping_value(row, "board_names")):
            try:
                code, resolved_name = resolve_eastmoney_board_code(name)
            except RuntimeError as exc:
                warnings.append(f"{name} 代码解析失败：{exc}")
                continue
            if code:
                codes.append(code)
                if resolved_name and resolved_name != name:
                    warnings.append(f"{name} 解析为东方财富板块 {resolved_name}({code})")
            else:
                warnings.append(f"{name} 未找到东方财富 BK 板块代码")
    return list(dict.fromkeys(codes)), warnings


def _load_mapping(path: Path) -> pd.DataFrame:
    mapping = pd.read_csv(path).fillna("")
    if "board_codes" not in mapping.columns:
        mapping["board_codes"] = ""
    if "board_names" not in mapping.columns:
        mapping["board_names"] = ""
    if "notes" not in mapping.columns:
        mapping["notes"] = ""
    return mapping


def _write_or_remove(frame: pd.DataFrame, path: Path) -> None:
    if frame.empty:
        if path.exists():
            path.unlink()
        return
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def _write_metric_history(frame: pd.DataFrame, path: Path, keys: list[str]) -> None:
    if frame.empty:
        if path.exists():
            path.unlink()
        return
    current = frame.copy()
    if path.exists():
        existing = pd.read_csv(path)
        combined = pd.concat([existing, current], ignore_index=True, sort=False)
    else:
        combined = current
    combined = combined.drop_duplicates(subset=keys, keep="last").sort_values(keys).reset_index(drop=True)
    combined.to_csv(path, index=False, encoding="utf-8-sig")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch real sector fund flow data from public web sources")
    parser.add_argument("--mapping", default=str(PROJECT_ROOT / "config" / "eastmoney_flow_map.csv"))
    parser.add_argument("--output", default=str(PROJECT_ROOT / "outputs" / "latest"))
    parser.add_argument("--page-size", type=int, default=20)
    parser.add_argument("--strict", action="store_true", help="Fail if any Eastmoney page cannot be fetched")
    parser.add_argument("--ranking-fallback", action="store_true", help="Use Eastmoney ranking pages if no board codes can be resolved")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    mapping = _load_mapping(Path(args.mapping))
    codes, warnings = _resolve_codes_from_mapping(mapping)
    if codes:
        boards, fetch_warnings = fetch_eastmoney_boards_by_code(codes, strict=args.strict)
        warnings.extend(fetch_warnings)
    elif args.ranking_fallback:
        boards, fetch_warnings = fetch_eastmoney_boards(page_size=args.page_size, strict=args.strict)
        warnings.extend(fetch_warnings)
    else:
        raise RuntimeError("No Eastmoney board codes were configured or resolved from mapping")
    flow, size, sources, missing = build_real_flow_files(boards, mapping)

    _write_or_remove(boards, output_dir / "eastmoney_sector_boards.csv")
    _write_metric_history(flow, output_dir / "fund_flow_amount.csv", ["date", "id"])
    _write_metric_history(size, output_dir / "sector_total_size.csv", ["date", "id"])
    _write_or_remove(sources, output_dir / "fund_flow_sources.csv")
    _write_or_remove(missing, output_dir / "fund_flow_missing_boards.csv")

    print(f"Fetched Eastmoney boards: {boards.shape[0]}")
    print(f"Mapped real fund flow rows: {flow.shape[0]}")
    print(f"Source: {EASTMONEY_REFERER}")
    print("Flow field: f62 主力净流入；total-size field: f20 总市值；currency: CNY")
    for warning in warnings:
        print(f"Warning: {warning}")
    if not missing.empty:
        print("Missing board mappings:")
        print(missing.to_string(index=False))


if __name__ == "__main__":
    main()
