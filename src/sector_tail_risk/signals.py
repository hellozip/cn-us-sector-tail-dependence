from __future__ import annotations

import numpy as np
import pandas as pd


def _empirical_percentile(history: pd.Series, value: float) -> float:
    clean = history.dropna().astype(float)
    if clean.empty or not np.isfinite(value):
        return np.nan
    return float((clean <= value).sum() / (clean.shape[0] + 1))


def _regime_from_percentile(percentile: float, alpha: float) -> str:
    if pd.isna(percentile):
        return "unavailable"
    if percentile <= alpha:
        return "lower_tail"
    if percentile >= 1.0 - alpha:
        return "upper_tail"
    return "middle"


def _tail_strength(percentile: float, regime: str, alpha: float) -> float:
    if pd.isna(percentile):
        return np.nan
    if regime == "upper_tail":
        return max(0.0, min(1.0, (percentile - (1.0 - alpha)) / alpha))
    if regime == "lower_tail":
        return max(0.0, min(1.0, (alpha - percentile) / alpha))
    return max(0.0, min(1.0, abs(percentile - 0.5) / (0.5 - alpha)))


def latest_common_date(frame: pd.DataFrame, min_valid_ratio: float = 1.0) -> pd.Timestamp:
    min_count = int(np.ceil(frame.shape[1] * min_valid_ratio))
    valid_counts = frame.notna().sum(axis=1)
    candidates = valid_counts.loc[valid_counts >= min_count]
    if candidates.empty:
        raise ValueError("No date has enough valid observations for latest signal generation")
    return candidates.index.max()


def build_latest_regime(
    standardized: pd.DataFrame,
    raw_returns: pd.DataFrame,
    sigma: pd.DataFrame,
    assets: pd.DataFrame,
    alpha: float,
    as_of_date: pd.Timestamp | None = None,
) -> pd.DataFrame:
    if as_of_date is None:
        as_of_date = latest_common_date(standardized)
    if as_of_date not in standardized.index:
        raise ValueError(f"as_of_date {as_of_date} is not in standardized residual index")

    asset_lookup = assets.set_index("id")
    rows: list[dict] = []
    for asset_id in standardized.columns:
        value = standardized.loc[as_of_date, asset_id]
        history = standardized.loc[standardized.index < as_of_date, asset_id]
        percentile = _empirical_percentile(history, value)
        regime = _regime_from_percentile(percentile, alpha)
        strength = _tail_strength(percentile, regime, alpha)
        raw_return = raw_returns.loc[as_of_date, asset_id] if asset_id in raw_returns.columns else np.nan
        sigma_value = sigma.loc[as_of_date, asset_id] if asset_id in sigma.columns else np.nan
        meta = asset_lookup.loc[asset_id]
        rows.append(
            {
                "as_of_date": as_of_date.date().isoformat(),
                "id": asset_id,
                "market": meta["market"],
                "sector": meta["sector"],
                "ticker": meta["ticker"],
                "latest_return": raw_return,
                "garch_sigma": sigma_value,
                "standardized_residual": value,
                "empirical_percentile": percentile,
                "regime": regime,
                "regime_strength": strength,
            }
        )

    return pd.DataFrame(rows).sort_values("empirical_percentile", ascending=False, na_position="last")


def _pair_rows(metrics: pd.DataFrame) -> pd.DataFrame:
    left = metrics.copy()
    left = left.rename(columns={"left_id": "source_id", "right_id": "target_id"})
    right = metrics.copy()
    right = right.rename(columns={"right_id": "source_id", "left_id": "target_id"})
    return pd.concat([left, right], ignore_index=True)


def build_flow_candidates(
    metrics: pd.DataFrame,
    latest_regime: pd.DataFrame,
    top_n: int = 30,
    min_relation: float = 0.05,
) -> pd.DataFrame:
    regime_lookup = latest_regime.set_index("id")
    rows: list[dict] = []
    for pair in _pair_rows(metrics).itertuples(index=False):
        if pair.source_id not in regime_lookup.index or pair.target_id not in regime_lookup.index:
            continue
        source = regime_lookup.loc[pair.source_id]
        target = regime_lookup.loc[pair.target_id]

        signal_type = None
        relation_metric = np.nan
        source_strength = float(source["regime_strength"]) if pd.notna(source["regime_strength"]) else 0.0
        target_modifier = 1.0

        if source["regime"] == "upper_tail":
            signal_type = "upper_tail_follow_through"
            relation_metric = float(pair.upper_tail_dependence)
            if target["regime"] == "upper_tail":
                target_modifier = 0.65
            elif target["regime"] == "middle":
                target_modifier = 1.0
            else:
                target_modifier = 0.0
        elif source["regime"] == "middle" and source["empirical_percentile"] >= 0.65:
            signal_type = "middle_regime_rotation"
            relation_metric = max(0.0, float(pair.middle_pearson)) if pd.notna(pair.middle_pearson) else np.nan
            source_strength = max(0.0, min(1.0, (float(source["empirical_percentile"]) - 0.65) / 0.30))
            if target["regime"] == "lower_tail":
                target_modifier = 0.0

        if signal_type is None or pd.isna(relation_metric) or relation_metric < min_relation or target_modifier <= 0:
            continue

        target_room = 1.0
        if target["regime"] == "upper_tail":
            target_room = 0.6
        elif target["regime"] == "middle":
            target_room = max(0.2, 1.0 - max(0.0, float(target["empirical_percentile"]) - 0.5))

        score = relation_metric * max(source_strength, 0.2) * target_modifier * target_room
        rows.append(
            {
                "signal_type": signal_type,
                "source_id": pair.source_id,
                "target_id": pair.target_id,
                "source_regime": source["regime"],
                "target_regime": target["regime"],
                "source_percentile": source["empirical_percentile"],
                "target_percentile": target["empirical_percentile"],
                "relation_metric": relation_metric,
                "score": score,
                "source_latest_return": source["latest_return"],
                "target_latest_return": target["latest_return"],
                "interpretation": "possible_flow_follow_through"
                if target["regime"] == "middle"
                else "already_confirming_move",
            }
        )

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("score", ascending=False).head(top_n)


def build_risk_contagion_candidates(
    metrics: pd.DataFrame,
    latest_regime: pd.DataFrame,
    top_n: int = 30,
    min_relation: float = 0.05,
) -> pd.DataFrame:
    regime_lookup = latest_regime.set_index("id")
    rows: list[dict] = []
    for pair in _pair_rows(metrics).itertuples(index=False):
        if pair.source_id not in regime_lookup.index or pair.target_id not in regime_lookup.index:
            continue
        source = regime_lookup.loc[pair.source_id]
        target = regime_lookup.loc[pair.target_id]
        if source["regime"] != "lower_tail":
            continue
        relation_metric = float(pair.lower_tail_dependence)
        if pd.isna(relation_metric) or relation_metric < min_relation:
            continue
        source_strength = float(source["regime_strength"]) if pd.notna(source["regime_strength"]) else 0.0
        target_modifier = 0.65 if target["regime"] == "lower_tail" else 1.0
        score = relation_metric * max(source_strength, 0.2) * target_modifier
        rows.append(
            {
                "signal_type": "lower_tail_contagion_watch",
                "source_id": pair.source_id,
                "target_id": pair.target_id,
                "source_regime": source["regime"],
                "target_regime": target["regime"],
                "source_percentile": source["empirical_percentile"],
                "target_percentile": target["empirical_percentile"],
                "relation_metric": relation_metric,
                "score": score,
                "source_latest_return": source["latest_return"],
                "target_latest_return": target["latest_return"],
                "interpretation": "possible_downside_spillover",
            }
        )

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("score", ascending=False).head(top_n)

