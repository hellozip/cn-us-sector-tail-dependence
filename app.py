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


def _read_timeseries(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, index_col=0, parse_dates=True)


def _read_metric_timeseries(path: Path, value_names: list[str]) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    raw = pd.read_csv(path)
    lower_columns = {str(column).lower(): column for column in raw.columns}
    if {"date", "id"}.issubset(lower_columns):
        value_column = next((lower_columns[name] for name in value_names if name in lower_columns), None)
        if value_column is None:
            return pd.DataFrame()
        date_column = lower_columns["date"]
        id_column = lower_columns["id"]
        frame = raw[[date_column, id_column, value_column]].copy()
        frame[date_column] = pd.to_datetime(frame[date_column])
        frame[value_column] = pd.to_numeric(frame[value_column], errors="coerce")
        return frame.pivot_table(index=date_column, columns=id_column, values=value_column, aggfunc="last").sort_index()
    if raw.empty:
        return pd.DataFrame()
    date_column = raw.columns[0]
    raw[date_column] = pd.to_datetime(raw[date_column])
    return raw.set_index(date_column).apply(pd.to_numeric, errors="coerce").sort_index()


def _read_fund_flow_sources(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    frame = pd.read_csv(path).replace({np.nan: None})
    if "id" not in frame.columns:
        return {}
    return {str(row["id"]): row for row in frame.to_dict(orient="records")}


def _latest_us_etf_snapshots(data_dir: Path) -> pd.DataFrame:
    path = data_dir / "us_etf_snapshots.csv"
    if not path.exists():
        return pd.DataFrame()
    frame = pd.read_csv(path).replace({np.nan: None})
    required = {"date", "id", "aum"}
    if not required.issubset(frame.columns):
        return pd.DataFrame()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["aum"] = pd.to_numeric(frame["aum"], errors="coerce")
    frame = frame.dropna(subset=["date", "id", "aum"])
    frame = frame[frame["aum"] > 0].copy()
    if frame.empty:
        return pd.DataFrame()
    frame["id"] = frame["id"].astype(str)
    return frame.sort_values(["id", "date"]).drop_duplicates(subset=["id"], keep="last")


def _augment_pending_us_snapshot_rows(
    data_dir: Path,
    fund_flow: pd.DataFrame,
    total_size: pd.DataFrame,
    sources: dict[str, dict],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, dict]]:
    snapshots = _latest_us_etf_snapshots(data_dir)
    if snapshots.empty:
        return fund_flow, total_size, sources
    fund_flow = fund_flow.copy()
    total_size = total_size.copy()
    sources = dict(sources)
    for row in _records(snapshots):
        asset_id = str(row.get("id") or "")
        if not asset_id.startswith("US_"):
            continue
        when = pd.Timestamp(row.get("date"))
        aum = _safe_float(row.get("aum"))
        if aum is None or aum <= 0:
            continue
        if asset_id not in total_size.columns:
            total_size[asset_id] = np.nan
        total_size.loc[when, asset_id] = aum
        if asset_id not in fund_flow.columns or pd.to_numeric(fund_flow[asset_id], errors="coerce").dropna().empty:
            if asset_id not in fund_flow.columns:
                fund_flow[asset_id] = np.nan
            fund_flow.loc[when, asset_id] = 0.0
            ticker = str(row.get("ticker") or "")
            sources.setdefault(
                asset_id,
                {
                    "flow_source": "StockAnalysis ETF AUM/份额快照：等待第二个交易日快照后估算 ETF 净申赎",
                    "total_size_source": "StockAnalysis ETF AUM",
                    "source_url": str(row.get("source_url") or ""),
                    "currency": str(row.get("currency") or "USD"),
                    "board_codes": ticker,
                    "board_names": str(row.get("name") or ticker),
                    "notes": "当前只有一张 StockAnalysis ETF AUM/份额快照，资金流金额以 0 占位用于展示板块；抓到第二个不同交易日快照后，会自动改用净申赎估算值。",
                },
            )
    return fund_flow.sort_index(), total_size.sort_index(), sources


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
    if latest_regime.empty:
        return []
    lookup = _asset_lookup(latest_regime)
    rows: list[dict] = []
    for row in _records(latest_regime):
        asset_id = row.get("id")
        if not asset_id:
            continue
        latest_sigma = _safe_float(row.get("garch_sigma"))
        if latest_sigma is None:
            continue
        percentile = None
        ratio = None
        if not sigma_history.empty and asset_id in sigma_history.columns:
            history = pd.to_numeric(sigma_history[asset_id], errors="coerce").dropna()
            if history.shape[0] >= 250:
                median_sigma = float(history.median())
                if median_sigma > 0:
                    percentile = float((history <= latest_sigma).mean())
                    ratio = latest_sigma / median_sigma
        if percentile is None:
            percentile = _safe_float(row.get("empirical_percentile"))
        residual = abs(_safe_float(row.get("standardized_residual")) or 0.0)
        latest_return = abs(_safe_float(row.get("latest_return")) or 0.0)
        if percentile is None:
            continue
        ratio_for_filter = ratio if ratio is not None else 1.0
        if percentile < 0.85 and ratio_for_filter < 1.35 and residual < 1.8:
            continue
        rows.append(
            {
                **row,
                "volatility_percentile": percentile,
                "volatility_ratio": ratio,
                "volatility_score": percentile + min(ratio_for_filter / 2.5, 1.2) + min(residual / 3.0, 1.0) + min(latest_return * 8, 0.5),
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
        reasons = [
            f"最新 GARCH 条件波动率为 {_fmt_pct(sigma)}，处在自身历史约 {_fmt_pct(percentile)} 分位。",
            f"最新标准残差为 {_fmt_num(residual, 2)}，对应{direction}，需要同时观察方向和波动是否继续扩散。",
        ]
        if ratio is not None:
            reasons.insert(1, f"当前波动率约为历史中位数的 {_fmt_num(ratio, 2)} 倍，说明波动状态已经明显抬升。")
        else:
            reasons.insert(1, "当前快照目录缺少完整 sigma 历史时，系统会使用 latest_regime 中已保存的 GARCH 分位和残差作为降级检测依据。")
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
                "reasons": reasons,
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


def _flow_ranking_for_date(
    fund_flow: pd.DataFrame,
    total_size: pd.DataFrame,
    turnover: pd.DataFrame,
    returns: pd.DataFrame,
    when: pd.Timestamp,
) -> pd.DataFrame:
    if when not in fund_flow.index:
        return pd.DataFrame()
    amount = pd.to_numeric(fund_flow.loc[when], errors="coerce")
    amount = amount.reindex(fund_flow.columns).dropna()
    if amount.empty:
        return pd.DataFrame()
    frame = pd.DataFrame({"id": amount.index, "flow_amount": amount.values})
    if when in total_size.index:
        frame["total_size"] = frame["id"].map(pd.to_numeric(total_size.loc[when], errors="coerce").to_dict())
    else:
        frame["total_size"] = np.nan
    frame["flow_ratio"] = np.where(
        frame["total_size"] > 0,
        frame["flow_amount"] / frame["total_size"],
        np.nan,
    )
    frame["flow_ratio"] = pd.to_numeric(frame["flow_ratio"], errors="coerce").replace([np.inf, -np.inf], np.nan)
    frame = frame.dropna(subset=["flow_ratio"])
    if frame.empty:
        return pd.DataFrame()
    if when in turnover.index:
        frame["turnover_amount"] = frame["id"].map(pd.to_numeric(turnover.loc[when], errors="coerce").to_dict())
    else:
        frame["turnover_amount"] = np.nan
    if when in returns.index:
        frame["latest_return"] = frame["id"].map(pd.to_numeric(returns.loc[when], errors="coerce").to_dict())
    else:
        frame["latest_return"] = np.nan
    frame = frame.sort_values("flow_ratio", ascending=False).reset_index(drop=True)
    frame["rank"] = frame.index + 1
    return frame


def _series_value_on_or_before(frame: pd.DataFrame, asset_id: str, when: pd.Timestamp) -> float:
    if frame.empty or asset_id not in frame.columns:
        return np.nan
    series = pd.to_numeric(frame[asset_id], errors="coerce").dropna()
    if series.empty:
        return np.nan
    candidates = series[series.index <= when]
    if candidates.empty:
        return np.nan
    return float(candidates.iloc[-1])


def _rank_flow_rows(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    frame = pd.DataFrame(rows)
    frame["flow_ratio"] = pd.to_numeric(frame["flow_ratio"], errors="coerce").replace([np.inf, -np.inf], np.nan)
    frame = frame.dropna(subset=["flow_ratio"])
    if frame.empty:
        return pd.DataFrame()
    frame = frame.sort_values("flow_ratio", ascending=False).reset_index(drop=True)
    frame["rank"] = frame.index + 1
    return frame


def _latest_flow_rankings(
    fund_flow: pd.DataFrame,
    total_size: pd.DataFrame,
    turnover: pd.DataFrame,
    returns: pd.DataFrame,
    as_of: pd.Timestamp | None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    fund_flow = fund_flow.rename(columns=str)
    total_size = total_size.rename(columns=str)
    turnover = turnover.rename(columns=str) if not turnover.empty else turnover
    returns = returns.rename(columns=str) if not returns.empty else returns
    asset_ids = sorted(set(fund_flow.columns).intersection(set(total_size.columns)))
    current_rows: list[dict] = []
    previous_rows: list[dict] = []
    for asset_id in asset_ids:
        observations = pd.DataFrame(
            {
                "flow_amount": pd.to_numeric(fund_flow[asset_id], errors="coerce"),
                "total_size": pd.to_numeric(total_size[asset_id], errors="coerce"),
            }
        ).dropna(subset=["flow_amount", "total_size"])
        observations = observations[observations["total_size"] > 0].sort_index()
        if as_of is not None:
            aligned_observations = observations[observations.index <= as_of]
            if not aligned_observations.empty:
                observations = aligned_observations
        if observations.empty:
            continue
        current_date = pd.Timestamp(observations.index[-1])
        previous_date = pd.Timestamp(observations.index[-2]) if len(observations) > 1 else pd.NaT
        current = observations.iloc[-1]
        flow_ratio = float(current["flow_amount"] / current["total_size"])
        current_rows.append(
            {
                "id": asset_id,
                "flow_date": current_date,
                "previous_flow_date": previous_date,
                "flow_amount": float(current["flow_amount"]),
                "total_size": float(current["total_size"]),
                "flow_ratio": flow_ratio,
                "turnover_amount": _series_value_on_or_before(turnover, asset_id, current_date),
                "latest_return": _series_value_on_or_before(returns, asset_id, current_date),
            }
        )
        if len(observations) > 1:
            previous = observations.iloc[-2]
            previous_rows.append(
                {
                    "id": asset_id,
                    "flow_date": previous_date,
                    "flow_amount": float(previous["flow_amount"]),
                    "total_size": float(previous["total_size"]),
                    "flow_ratio": float(previous["flow_amount"] / previous["total_size"]),
                }
            )
    return _rank_flow_rows(current_rows), _rank_flow_rows(previous_rows)


def _iso_date(value) -> str | None:
    if value is None or pd.isna(value):
        return None
    return pd.Timestamp(value).date().isoformat()


def _build_fund_flow_summary(data_dir: Path, latest_regime: pd.DataFrame, limit: int = 20) -> dict:
    returns = _read_timeseries(data_dir / "returns.csv")
    fund_flow = _read_metric_timeseries(data_dir / "fund_flow_amount.csv", ["flow_amount", "net_flow", "net_flow_amount"])
    total_size = _read_metric_timeseries(data_dir / "sector_total_size.csv", ["total_size", "sector_total_size", "aum", "market_cap"])
    turnover = _read_timeseries(data_dir / "turnover_amount.csv")
    sources = _read_fund_flow_sources(data_dir / "fund_flow_sources.csv")
    fund_flow, total_size, sources = _augment_pending_us_snapshot_rows(data_dir, fund_flow, total_size, sources)

    if fund_flow.empty or total_size.empty:
        return {
            "available": False,
            "method": "未配置真实资金流来源。请提供 fund_flow_amount.csv（真实净流入/净流出金额）、sector_total_size.csv（板块总规模/AUM/市值口径）和 fund_flow_sources.csv（来源说明）。当前不会用收益率×成交额替代真实资金流。",
            "rows": [],
        }

    as_of = None
    if not latest_regime.empty and "as_of_date" in latest_regime.columns:
        as_of_values = latest_regime["as_of_date"].dropna()
        if not as_of_values.empty:
            as_of = pd.Timestamp(str(as_of_values.iloc[0]))

    current, previous = _latest_flow_rankings(fund_flow, total_size, turnover, returns, as_of)
    if current.empty:
        return {"available": False, "method": "真实资金流或板块总规模暂无有效观测。", "rows": []}

    lookup = _asset_lookup(latest_regime)
    previous_rank = dict(zip(previous["id"], previous["rank"])) if not previous.empty else {}

    def decorate_row(raw: dict) -> dict:
        asset_id = str(raw["id"])
        rank = int(raw["rank"])
        prev_rank = int(previous_rank.get(asset_id, rank))
        rank_change = int(prev_rank - rank)
        if rank_change > 0:
            arrow = f"↑{rank_change}"
        elif rank_change < 0:
            arrow = f"↓{abs(rank_change)}"
        else:
            arrow = "→"
        source = sources.get(asset_id, {})
        return {
            **raw,
            "flow_date": _iso_date(raw.get("flow_date")),
            "previous_flow_date": _iso_date(raw.get("previous_flow_date")),
            "label": _asset_label(asset_id, lookup),
            "previous_rank": prev_rank,
            "rank_change": rank_change,
            "rank_arrow": arrow,
            "flow_direction": "流入" if (_safe_float(raw.get("flow_amount")) or 0) >= 0 else "流出",
            "flow_source": source.get("flow_source") or source.get("source") or "未注明",
            "total_size_source": source.get("total_size_source") or source.get("size_source") or "未注明",
            "source_url": source.get("source_url") or "",
            "currency": source.get("currency") or "",
            "board_codes": source.get("board_codes") or "",
            "board_names": source.get("board_names") or "",
            "source_notes": source.get("notes") or "",
        }

    rows: list[dict] = []
    for row in _records(current.head(limit)):
        rows.append(decorate_row(row))

    inflow = current[current["flow_amount"] > 0]
    outflow = current[current["flow_amount"] < 0]
    total_inflow = float(inflow["flow_amount"].sum()) if not inflow.empty else 0.0
    total_outflow = float(outflow["flow_amount"].sum()) if not outflow.empty else 0.0
    largest_inflow = rows[0] if rows else None
    largest_outflow_row = current.sort_values("flow_ratio", ascending=True).head(1)
    largest_outflow = None
    if not largest_outflow_row.empty:
        raw = _records(largest_outflow_row)[0]
        largest_outflow = decorate_row(raw)

    current_dates = current["flow_date"].dropna()
    previous_dates = current["previous_flow_date"].dropna()
    current_date = pd.Timestamp(current_dates.max()) if not current_dates.empty else None
    previous_date = pd.Timestamp(previous_dates.max()) if not previous_dates.empty else None

    return {
        "available": True,
        "as_of_date": _iso_date(current_date),
        "previous_date": _iso_date(previous_date),
        "method": "资金流金额来自 fund_flow_amount.csv 中接入的净流入/净流出来源；流入/流出占比 = 资金流金额 ÷ sector_total_size.csv 中的该板块总规模。排名变化按每个板块的上一个有效资金流交易日比较，不按自然日“昨天”比较。中国侧接入东方财富公开网页接口 f62 主力净流入，分母为 f20 总市值；美国侧接入 StockAnalysis ETF AUM/份额/价格快照，优先用（本期份额 - 上期份额）× 本期价格估算 ETF 净申赎，缺份额时用 AUM 按价格收益调整估算，并在来源中标注为估计值。",
        "total_inflow_amount": total_inflow,
        "total_outflow_amount": total_outflow,
        "net_flow_amount": total_inflow + total_outflow,
        "largest_inflow": largest_inflow,
        "largest_outflow": largest_outflow,
        "rows": rows,
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
        "fundFlow": _build_fund_flow_summary(data_dir, latest_regime),
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
    flow_result = None
    if result.returncode == 0:
        flow_cmd = [
            sys.executable,
            str(ROOT / "scripts" / "fetch_real_fund_flows.py"),
            "--output",
            str(OUTPUT_DIR),
        ]
        flow_result = subprocess.run(flow_cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)
    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": ((result.stdout or "") + ("\n" + flow_result.stdout if flow_result else ""))[-4000:],
        "stderr": ((result.stderr or "") + ("\n" + flow_result.stderr if flow_result and flow_result.returncode != 0 else ""))[-4000:],
        "fund_flow_returncode": flow_result.returncode if flow_result else None,
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
