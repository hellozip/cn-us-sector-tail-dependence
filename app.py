from __future__ import annotations

import json
import mimetypes
import os
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import parse_qs, unquote

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "outputs" / "latest"
REPORTS_DIR = ROOT / "reports"
WEB_DIR = ROOT / "web"
STATIC_DIR = WEB_DIR / "static"

MARKET_LABELS = {
    "US": "美国",
    "CN": "中国",
}

SECTOR_LABELS = {
    "Internet": "互联网",
    "Semiconductor": "半导体",
    "New Energy": "新能源",
    "Healthcare": "医药",
    "Financials": "金融",
    "Real Estate Chain": "地产链",
    "Energy": "能源",
    "Materials": "材料",
    "Industrials": "工业",
    "Utilities": "公用事业",
}

ID_SECTOR_LABELS = {
    "INTERNET": "互联网",
    "SEMICONDUCTOR": "半导体",
    "NEW_ENERGY": "新能源",
    "HEALTHCARE": "医药",
    "FINANCIALS": "金融",
    "REAL_ESTATE_CHAIN": "地产链",
    "ENERGY": "能源",
    "MATERIALS": "材料",
    "INDUSTRIALS": "工业",
    "UTILITIES": "公用事业",
}

REGIME_LABELS = {
    "upper_tail": "上尾强势",
    "lower_tail": "下尾弱势",
    "middle": "中间区间",
}

HEATMAP_LABELS = {
    "lower_tail_dependence.svg": "下尾相关性",
    "upper_tail_dependence.svg": "上尾相关性",
    "middle_pearson_correlation.svg": "中间区间 Pearson 相关",
    "middle_spearman_correlation.svg": "中间区间 Spearman 相关",
    "lower_co_crash_lift.svg": "共同下跌放大倍数",
    "upper_co_rally_lift.svg": "共同上涨放大倍数",
    "pearson_correlation.svg": "全样本 Pearson 相关",
    "spearman_correlation.svg": "全样本 Spearman 相关",
}


def _json_response(start_response, payload: dict, status: str = "200 OK"):
    body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
    start_response(
        status,
        [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
        ],
    )
    return [body]


def _text_response(start_response, text: str, status: str = "200 OK", content_type: str = "text/plain; charset=utf-8"):
    body = text.encode("utf-8")
    start_response(status, [("Content-Type", content_type), ("Content-Length", str(len(body)))])
    return [body]


def _file_response(start_response, path: Path):
    if not path.exists() or not path.is_file():
        return _text_response(start_response, "Not found", "404 Not Found")
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    body = path.read_bytes()
    start_response(
        "200 OK",
        [
            ("Content-Type", content_type),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "public, max-age=60"),
        ],
    )
    return [body]


def _safe_child(root: Path, relative: str) -> Path | None:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def _latest_snapshot_dir() -> Path | None:
    if not REPORTS_DIR.exists():
        return None
    candidates = [path for path in REPORTS_DIR.iterdir() if path.is_dir() and (path / "report.html").exists()]
    if not candidates:
        return None
    return sorted(candidates, key=lambda path: path.name)[-1]


def _active_data_dir() -> Path:
    if (OUTPUT_DIR / "latest_regime_alpha_0.05.csv").exists() or (OUTPUT_DIR / "report.html").exists():
        return OUTPUT_DIR
    snapshot = _latest_snapshot_dir()
    return snapshot if snapshot else OUTPUT_DIR


def _alpha_token(value: str | float | int | None) -> str | None:
    if value is None or value == "":
        return None
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return None


def _detect_alpha_token(data_dir: Path, requested: str | None = None) -> str:
    if requested and (data_dir / f"latest_regime_alpha_{requested}.csv").exists():
        return requested
    candidates = list(data_dir.glob("latest_regime_alpha_*.csv"))
    if not candidates:
        return requested or "0.05"
    latest = max(candidates, key=lambda path: path.stat().st_mtime)
    return latest.stem.removeprefix("latest_regime_alpha_")


def _read_csv(path: Path, limit: int | None = None, sort_by: str | None = None, ascending: bool = False) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    frame = pd.read_csv(path)
    if sort_by and sort_by in frame.columns:
        frame = frame.sort_values(sort_by, ascending=ascending, na_position="last")
    if limit is not None:
        frame = frame.head(limit)
    return frame


def _records(frame: pd.DataFrame) -> list[dict]:
    if frame.empty:
        return []
    clean = frame.replace({np.nan: None})
    return clean.to_dict(orient="records")


def _safe_float(value) -> float | None:
    try:
        if pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _fmt_pct(value) -> str:
    number = _safe_float(value)
    if number is None:
        return "暂无"
    return f"{number * 100:.1f}%"


def _fmt_num(value, digits: int = 3) -> str:
    number = _safe_float(value)
    if number is None:
        return "暂无"
    return f"{number:.{digits}f}"


def _asset_lookup(latest_regime: pd.DataFrame) -> dict[str, dict]:
    if latest_regime.empty or "id" not in latest_regime.columns:
        return {}
    return {str(row["id"]): row for row in _records(latest_regime)}


def _asset_label(asset_id: str | None, lookup: dict[str, dict]) -> str:
    if not asset_id:
        return "未知板块"
    row = lookup.get(str(asset_id), {})
    market = row.get("market") or str(asset_id).split("_", 1)[0]
    sector = row.get("sector")
    if not sector and "_" in str(asset_id):
        sector = str(asset_id).split("_", 1)[1]
    market_label = MARKET_LABELS.get(str(market), str(market))
    sector_label = SECTOR_LABELS.get(str(sector), ID_SECTOR_LABELS.get(str(sector), str(sector).replace("_", " ")))
    return f"{market_label}{sector_label}"


def _regime_label(value) -> str:
    return REGIME_LABELS.get(str(value), str(value) if value is not None else "暂无")


def _flow_alerts(flow: pd.DataFrame, latest_regime: pd.DataFrame, limit: int = 6) -> list[dict]:
    if flow.empty:
        return []
    lookup = _asset_lookup(latest_regime)
    alerts: list[dict] = []
    for row in _records(flow.head(limit)):
        source_id = row.get("source_id")
        target_id = row.get("target_id")
        source_label = _asset_label(source_id, lookup)
        target_label = _asset_label(target_id, lookup)
        relation = _safe_float(row.get("relation_metric"))
        score = _safe_float(row.get("score"))
        target_regime = row.get("target_regime")
        target_note = "目标板块尚未完全确认强势，更适合作为后续承接观察。"
        if target_regime == "upper_tail":
            target_note = "目标板块已经进入上尾强势区，说明动量已经确认，但追高回撤风险也更高。"
        alerts.append(
            {
                "type": "opportunity",
                "subtype": "资金扩散观察",
                "title": f"{target_label} 可能承接 {source_label} 的扩散",
                "source_id": source_id,
                "target_id": target_id,
                "source_label": source_label,
                "target_label": target_label,
                "score": score,
                "relation_metric": relation,
                "summary": f"{source_label} 当前偏强，历史上与 {target_label} 的联动较明显。",
                "reasons": [
                    f"{source_label} 当前处于{_regime_label(row.get('source_regime'))}，{target_label} 当前处于{_regime_label(target_regime)}。",
                    f"历史关系强度为 {_fmt_pct(relation)}，综合分数为 {_fmt_num(score)}。",
                    target_note,
                ],
                "watch": "适合作为观察名单：后续若目标板块同步放量走强，说明资金扩散正在被市场确认。",
            }
        )
    return alerts


def _contagion_alerts(risk: pd.DataFrame, latest_regime: pd.DataFrame, limit: int = 6) -> list[dict]:
    if risk.empty:
        return []
    lookup = _asset_lookup(latest_regime)
    alerts: list[dict] = []
    for row in _records(risk.head(limit)):
        source_id = row.get("source_id")
        target_id = row.get("target_id")
        source_label = _asset_label(source_id, lookup)
        target_label = _asset_label(target_id, lookup)
        relation = _safe_float(row.get("relation_metric"))
        score = _safe_float(row.get("score"))
        alerts.append(
            {
                "type": "risk",
                "subtype": "下尾传导风险",
                "title": f"{target_label} 可能受到 {source_label} 的下跌拖累",
                "source_id": source_id,
                "target_id": target_id,
                "source_label": source_label,
                "target_label": target_label,
                "score": score,
                "relation_metric": relation,
                "summary": f"{source_label} 已进入下尾弱势区，历史上与 {target_label} 存在共同下跌关系。",
                "reasons": [
                    f"{source_label} 当前处于{_regime_label(row.get('source_regime'))}，{target_label} 当前处于{_regime_label(row.get('target_regime'))}。",
                    f"下尾关系强度为 {_fmt_pct(relation)}，风险分数为 {_fmt_num(score)}。",
                    f"来源板块当日收益为 {_fmt_pct(row.get('source_latest_return'))}，目标板块当日收益为 {_fmt_pct(row.get('target_latest_return'))}。",
                ],
                "watch": "适合检查持仓是否集中暴露在同一条下跌传导链上，尤其是同市场、同产业链板块。",
            }
        )
    return alerts


def _overheat_alerts(latest_regime: pd.DataFrame, limit: int = 5) -> list[dict]:
    if latest_regime.empty:
        return []
    frame = latest_regime.copy()
    for column in ["latest_return", "standardized_residual", "empirical_percentile", "regime_strength"]:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    required = {"latest_return", "standardized_residual", "empirical_percentile", "id"}
    if not required.issubset(frame.columns):
        return []
    hot = frame[
        (frame["latest_return"] > 0)
        & (
            (frame["regime"].eq("upper_tail") if "regime" in frame.columns else False)
            | (frame["empirical_percentile"] >= 0.95)
            | (frame["standardized_residual"] >= 1.8)
        )
    ].copy()
    if hot.empty:
        return []
    hot["pullback_score"] = (
        hot["empirical_percentile"].fillna(0) * 2
        + hot["standardized_residual"].clip(lower=0).fillna(0)
        + hot["latest_return"].fillna(0) * 20
    )
    lookup = _asset_lookup(latest_regime)
    alerts: list[dict] = []
    for row in _records(hot.sort_values("pullback_score", ascending=False).head(limit)):
        asset_id = row.get("id")
        label = _asset_label(asset_id, lookup)
        score = _safe_float(row.get("pullback_score"))
        alerts.append(
            {
                "type": "risk",
                "subtype": "过热回调风险",
                "title": f"{label} 短线偏离过大，回调风险升高",
                "source_id": asset_id,
                "target_id": asset_id,
                "source_label": label,
                "target_label": label,
                "score": score,
                "relation_metric": None,
                "summary": f"{label} 当日涨幅和 GARCH 标准残差都偏高，说明走势已经明显偏离自身常态波动。",
                "reasons": [
                    f"当日收益为 {_fmt_pct(row.get('latest_return'))}，GARCH 标准残差为 {_fmt_num(row.get('standardized_residual'), 2)}。",
                    f"历史分位数为 {_fmt_pct(row.get('empirical_percentile'))}，当前处于{_regime_label(row.get('regime'))}。",
                    "强势不等于立刻看空，但当涨幅远超自身波动水平时，下一步更容易出现回撤、横盘消化或资金轮动。",
                ],
                "watch": "如果后续价格不能继续放量确认，优先把它当作追高风险和仓位再平衡提示。",
            }
        )
    return alerts


def _volatility_alerts(latest_regime: pd.DataFrame, sigma_history: pd.DataFrame, limit: int = 8) -> list[dict]:
    if latest_regime.empty or sigma_history.empty:
        return []
    lookup = _asset_lookup(latest_regime)
    rows: list[dict] = []
    for row in _records(latest_regime):
        asset_id = row.get("id")
        if not asset_id or asset_id not in sigma_history.columns:
            continue
        history = pd.to_numeric(sigma_history[asset_id], errors="coerce").dropna()
        if history.shape[0] < 250:
            continue
        latest_sigma = _safe_float(row.get("garch_sigma"))
        if latest_sigma is None:
            latest_sigma = _safe_float(history.iloc[-1])
        if latest_sigma is None:
            continue
        median_sigma = float(history.median())
        if median_sigma <= 0:
            continue
        percentile = float((history <= latest_sigma).mean())
        ratio = latest_sigma / median_sigma
        residual = abs(_safe_float(row.get("standardized_residual")) or 0.0)
        latest_return = abs(_safe_float(row.get("latest_return")) or 0.0)
        if percentile < 0.85 and ratio < 1.35 and residual < 1.8:
            continue
        rows.append(
            {
                **row,
                "volatility_percentile": percentile,
                "volatility_ratio": ratio,
                "volatility_score": percentile + min(ratio / 2.5, 1.2) + min(residual / 3.0, 1.0) + min(latest_return * 8, 0.5),
            }
        )

    alerts: list[dict] = []
    for row in sorted(rows, key=lambda item: item["volatility_score"], reverse=True)[:limit]:
        asset_id = row.get("id")
        label = _asset_label(asset_id, lookup)
        sigma = _safe_float(row.get("garch_sigma"))
        percentile = _safe_float(row.get("volatility_percentile"))
        ratio = _safe_float(row.get("volatility_ratio"))
        residual = _safe_float(row.get("standardized_residual"))
        score = _safe_float(row.get("volatility_score"))
        direction = "上涨冲击" if (_safe_float(row.get("latest_return")) or 0.0) > 0 else "下跌冲击"
        alerts.append(
            {
                "type": "volatility",
                "subtype": "波动率异常检测",
                "title": f"{label} 波动率显著偏离自身常态",
                "source_id": asset_id,
                "target_id": asset_id,
                "source_label": label,
                "target_label": label,
                "score": score,
                "relation_metric": percentile,
                "summary": f"{label} 的最新 GARCH 条件波动率处在自身历史高位，当前价格变化更像是异常波动，而不是普通日内噪声。",
                "reasons": [
                    f"最新 GARCH 条件波动率为 {_fmt_pct(sigma)}，处在自身历史约 {_fmt_pct(percentile)} 分位。",
                    f"当前波动率约为历史中位数的 {_fmt_num(ratio, 2)} 倍，说明波动状态已经明显抬升。",
                    f"最新标准残差为 {_fmt_num(residual, 2)}，对应{direction}，需要同时观察方向和波动是否继续扩散。",
                ],
                "watch": "适合检查仓位杠杆、止损距离和同类板块暴露；波动率异常本身不等于一定上涨或下跌，但会放大后续价格路径的不确定性。",
            }
        )
    return alerts


def _build_alerts(flow: pd.DataFrame, risk: pd.DataFrame, latest_regime: pd.DataFrame, sigma_history: pd.DataFrame) -> dict:
    opportunity_items = _flow_alerts(flow, latest_regime)
    contagion_items = _contagion_alerts(risk, latest_regime)
    overheat_items = _overheat_alerts(latest_regime)
    volatility_items = _volatility_alerts(latest_regime, sigma_history)
    risk_items = contagion_items + overheat_items
    return {
        "opportunity": {
            "title": "机会提示",
            "summary": "根据当前强势板块和历史相关结构，筛选下一步可能获得资金扩散的板块。",
            "count": len(opportunity_items),
            "items": opportunity_items,
        },
        "risk": {
            "title": "风险提示",
            "summary": "同时观察下尾传导风险和短线过热回调风险，避免把高波动误读成确定性机会。",
            "count": len(risk_items),
            "items": risk_items,
        },
        "volatility": {
            "title": "波动异常",
            "summary": "基于 GARCH 条件波动率的历史分位数，识别当前明显偏离自身常态波动的板块。",
            "count": len(volatility_items),
            "items": volatility_items,
        },
    }


def _first_existing(data_dir: Path, names: list[str]) -> Path | None:
    for name in names:
        path = data_dir / name
        if path.exists():
            return path
    return None


def _dashboard_payload(alpha: str | float | int | None = None) -> dict:
    data_dir = _active_data_dir()
    alpha_key = _detect_alpha_token(data_dir, _alpha_token(alpha))
    latest_regime = _read_csv(data_dir / f"latest_regime_alpha_{alpha_key}.csv")
    flow = _read_csv(data_dir / f"flow_candidates_alpha_{alpha_key}.csv", limit=30, sort_by="score")
    risk = _read_csv(data_dir / f"risk_contagion_candidates_alpha_{alpha_key}.csv", limit=30, sort_by="score")
    matched = _read_csv(data_dir / f"matched_sector_metrics_alpha_{alpha_key}.csv", limit=20)
    garch = _read_csv(data_dir / "garch_params.csv", limit=30)
    sigma_history = _read_csv(data_dir / "garch_conditional_sigma.csv")
    coverage = _read_csv(data_dir / "asset_coverage.csv", limit=30)
    metrics = _read_csv(data_dir / f"pair_metrics_alpha_{alpha_key}.csv")

    as_of = None
    regime_counts: dict[str, int] = {}
    if not latest_regime.empty:
        if "as_of_date" in latest_regime.columns:
            as_of = str(latest_regime["as_of_date"].dropna().iloc[0])
        if "regime" in latest_regime.columns:
            regime_counts = latest_regime["regime"].value_counts(dropna=False).to_dict()

    top_lower = pd.DataFrame()
    top_upper = pd.DataFrame()
    top_middle = pd.DataFrame()
    if not metrics.empty:
        top_lower = metrics.sort_values("lower_tail_dependence", ascending=False, na_position="last").head(15)
        top_upper = metrics.sort_values("upper_tail_dependence", ascending=False, na_position="last").head(15)
        top_middle = metrics.sort_values("middle_pearson", ascending=False, na_position="last").head(15)

    heatmap_names = [
        "lower_tail_dependence.svg",
        "upper_tail_dependence.svg",
        "middle_pearson_correlation.svg",
        "middle_spearman_correlation.svg",
        "lower_co_crash_lift.svg",
        "upper_co_rally_lift.svg",
        "pearson_correlation.svg",
        "spearman_correlation.svg",
    ]
    heatmaps = [
        {
            "name": name,
            "label": HEATMAP_LABELS.get(name, name.replace("_", " ").replace(".svg", "").title()),
            "url": f"/report-assets/{name}",
        }
        for name in heatmap_names
        if (data_dir / name).exists()
    ]

    report_path = _first_existing(data_dir, ["report.html"])
    summary = {
        "data_dir": str(data_dir.relative_to(ROOT)) if data_dir.exists() else str(data_dir),
        "as_of_date": as_of,
        "alpha": float(alpha_key),
        "alpha_file_token": alpha_key,
        "regime_counts": regime_counts,
        "flow_count": int(flow.shape[0]),
        "risk_count": int(risk.shape[0]),
        "latest_report_url": "/report-assets/report.html" if report_path else None,
        "uses_live_outputs": data_dir == OUTPUT_DIR,
    }

    return {
        "summary": summary,
        "latestRegime": _records(latest_regime),
        "flowCandidates": _records(flow),
        "riskCandidates": _records(risk),
        "alerts": _build_alerts(flow, risk, latest_regime, sigma_history),
        "matchedSectors": _records(matched),
        "garchParams": _records(garch),
        "coverage": _records(coverage),
        "topLower": _records(top_lower),
        "topUpper": _records(top_upper),
        "topMiddle": _records(top_middle),
        "heatmaps": heatmaps,
    }


def _refresh_from_body(environ) -> dict:
    length = int(environ.get("CONTENT_LENGTH") or 0)
    raw = environ["wsgi.input"].read(length) if length else b"{}"
    try:
        params = json.loads(raw.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        params = {}

    today = date.today()
    start = params.get("start") or (today - timedelta(days=365 * 7)).isoformat()
    end = params.get("end") or today.isoformat()
    alpha = _alpha_token(params.get("alpha")) or "0.05"
    no_garch = bool(params.get("noGarch"))

    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "run_analysis.py"),
        "--start",
        start,
        "--end",
        end,
        "--alpha",
        alpha,
        "--output",
        str(OUTPUT_DIR),
    ]
    if no_garch:
        cmd.append("--no-garch")

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=900)
    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
        "dashboard": _dashboard_payload(alpha=alpha) if result.returncode == 0 else None,
    }


def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = unquote(environ.get("PATH_INFO", "/"))

    if method == "GET" and path == "/":
        return _file_response(start_response, WEB_DIR / "index.html")
    if method == "GET" and path == "/healthz":
        return _json_response(start_response, {"ok": True})
    if method == "GET" and path == "/api/dashboard":
        try:
            query = parse_qs(environ.get("QUERY_STRING", ""))
            return _json_response(start_response, _dashboard_payload(alpha=(query.get("alpha") or [None])[0]))
        except Exception as exc:  # pragma: no cover - defensive web boundary.
            return _json_response(start_response, {"error": str(exc)}, "500 Internal Server Error")
    if method == "POST" and path == "/api/refresh":
        try:
            payload = _refresh_from_body(environ)
            status = "200 OK" if payload["ok"] else "500 Internal Server Error"
            return _json_response(start_response, payload, status)
        except subprocess.TimeoutExpired:
            return _json_response(start_response, {"ok": False, "error": "analysis timed out"}, "504 Gateway Timeout")
        except Exception as exc:  # pragma: no cover - defensive web boundary.
            return _json_response(start_response, {"ok": False, "error": str(exc)}, "500 Internal Server Error")

    if method == "GET" and path.startswith("/static/"):
        child = _safe_child(STATIC_DIR, path.removeprefix("/static/"))
        return _file_response(start_response, child) if child else _text_response(start_response, "Not found", "404 Not Found")

    if method == "GET" and path.startswith("/report-assets/"):
        data_dir = _active_data_dir()
        child = _safe_child(data_dir, path.removeprefix("/report-assets/"))
        return _file_response(start_response, child) if child else _text_response(start_response, "Not found", "404 Not Found")

    if method == "GET" and path == "/api/raw":
        query = parse_qs(environ.get("QUERY_STRING", ""))
        name = (query.get("file") or [""])[0]
        child = _safe_child(_active_data_dir(), name)
        return _file_response(start_response, child) if child else _text_response(start_response, "Not found", "404 Not Found")

    return _text_response(start_response, "Not found", "404 Not Found")


if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    port = int(os.environ.get("PORT", "8000"))
    with make_server("127.0.0.1", port, app) as server:
        print(f"Serving on http://127.0.0.1:{port}")
        server.serve_forever()
