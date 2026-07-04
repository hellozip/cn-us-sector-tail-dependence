from __future__ import annotations

from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd


def read_assets(path: str | Path) -> pd.DataFrame:
    assets = pd.read_csv(path)
    required = {"id", "market", "sector", "ticker", "name", "currency", "proxy_note"}
    missing = required.difference(assets.columns)
    if missing:
        raise ValueError(f"Asset config is missing columns: {sorted(missing)}")
    if assets["id"].duplicated().any():
        dupes = assets.loc[assets["id"].duplicated(), "id"].tolist()
        raise ValueError(f"Duplicate asset ids: {dupes}")
    return assets


def compute_log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    prices = prices.sort_index()
    returns = np.log(prices / prices.shift(1))
    return returns.replace([np.inf, -np.inf], np.nan)


def coverage_table(prices: pd.DataFrame, returns: pd.DataFrame, assets: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    asset_lookup = assets.set_index("id")
    for asset_id in prices.columns:
        valid_prices = prices[asset_id].dropna()
        valid_returns = returns[asset_id].dropna()
        row = {
            "id": asset_id,
            "market": asset_lookup.loc[asset_id, "market"] if asset_id in asset_lookup.index else "",
            "sector": asset_lookup.loc[asset_id, "sector"] if asset_id in asset_lookup.index else "",
            "ticker": asset_lookup.loc[asset_id, "ticker"] if asset_id in asset_lookup.index else "",
            "first_price_date": valid_prices.index.min().date().isoformat() if not valid_prices.empty else "",
            "last_price_date": valid_prices.index.max().date().isoformat() if not valid_prices.empty else "",
            "price_observations": int(valid_prices.shape[0]),
            "return_observations": int(valid_returns.shape[0]),
            "annualized_return": float(valid_returns.mean() * 252) if not valid_returns.empty else np.nan,
            "annualized_volatility": float(valid_returns.std(ddof=1) * np.sqrt(252)) if valid_returns.shape[0] > 1 else np.nan,
            "min_daily_return": float(valid_returns.min()) if not valid_returns.empty else np.nan,
            "max_daily_return": float(valid_returns.max()) if not valid_returns.empty else np.nan,
        }
        rows.append(row)
    return pd.DataFrame(rows)


def _corr(x: pd.Series, y: pd.Series, method: str) -> float:
    if x.shape[0] < 3:
        return np.nan
    if method == "spearman":
        x = x.rank(method="average")
        y = y.rank(method="average")
        method = "pearson"
    return float(x.corr(y, method=method))


def pairwise_tail_metrics(
    returns: pd.DataFrame,
    assets: pd.DataFrame,
    alpha: float = 0.05,
    min_obs: int = 500,
) -> pd.DataFrame:
    if not 0 < alpha < 0.5:
        raise ValueError("alpha must be between 0 and 0.5")

    asset_lookup = assets.set_index("id")
    rows: list[dict] = []
    for left, right in combinations(returns.columns, 2):
        pair = returns[[left, right]].dropna()
        nobs = int(pair.shape[0])
        left_meta = asset_lookup.loc[left]
        right_meta = asset_lookup.loc[right]
        row = {
            "left_id": left,
            "right_id": right,
            "left_market": left_meta["market"],
            "right_market": right_meta["market"],
            "left_sector": left_meta["sector"],
            "right_sector": right_meta["sector"],
            "left_ticker": left_meta["ticker"],
            "right_ticker": right_meta["ticker"],
            "same_sector": bool(left_meta["sector"] == right_meta["sector"]),
            "cross_market": bool(left_meta["market"] != right_meta["market"]),
            "observations": nobs,
        }

        if nobs < min_obs:
            rows.append(row | _empty_metric_values())
            continue

        x = pair[left]
        y = pair[right]
        ux = x.rank(method="average", pct=True)
        uy = y.rank(method="average", pct=True)
        x_lower_tail = ux <= alpha
        y_lower_tail = uy <= alpha
        both_lower_tail = x_lower_tail & y_lower_tail
        either_lower_tail = x_lower_tail | y_lower_tail
        lower_tail_pair = pair.loc[either_lower_tail]

        upper_cutoff = 1.0 - alpha
        x_upper_tail = ux >= upper_cutoff
        y_upper_tail = uy >= upper_cutoff
        both_upper_tail = x_upper_tail & y_upper_tail
        either_upper_tail = x_upper_tail | y_upper_tail
        upper_tail_pair = pair.loc[either_upper_tail]

        x_middle = (ux > alpha) & (ux < upper_cutoff)
        y_middle = (uy > alpha) & (uy < upper_cutoff)
        both_middle = x_middle & y_middle
        middle_pair = pair.loc[both_middle]

        lower_both_count = int(both_lower_tail.sum())
        lower_both_prob = float(both_lower_tail.mean())
        x_lower_tail_count = int(x_lower_tail.sum())
        y_lower_tail_count = int(y_lower_tail.sum())

        upper_both_count = int(both_upper_tail.sum())
        upper_both_prob = float(both_upper_tail.mean())
        x_upper_tail_count = int(x_upper_tail.sum())
        y_upper_tail_count = int(y_upper_tail.sum())
        middle_count = int(both_middle.sum())

        row.update(
            {
                "pearson": _corr(x, y, "pearson"),
                "spearman": _corr(x, y, "spearman"),
                "tail_alpha": alpha,
                "lower_left_tail_count": x_lower_tail_count,
                "lower_right_tail_count": y_lower_tail_count,
                "lower_both_tail_count": lower_both_count,
                "lower_both_tail_probability": lower_both_prob,
                "lower_tail_dependence": lower_both_prob / alpha,
                "lower_co_crash_lift_vs_independence": lower_both_prob / (alpha * alpha),
                "lower_right_given_left_tail": lower_both_count / x_lower_tail_count
                if x_lower_tail_count
                else np.nan,
                "lower_left_given_right_tail": lower_both_count / y_lower_tail_count
                if y_lower_tail_count
                else np.nan,
                "lower_tail_union_pearson": _corr(lower_tail_pair[left], lower_tail_pair[right], "pearson")
                if lower_tail_pair.shape[0] >= 10
                else np.nan,
                "lower_avg_left_return_when_both_tail": float(x.loc[both_lower_tail].mean())
                if lower_both_count
                else np.nan,
                "lower_avg_right_return_when_both_tail": float(y.loc[both_lower_tail].mean())
                if lower_both_count
                else np.nan,
                "upper_left_tail_count": x_upper_tail_count,
                "upper_right_tail_count": y_upper_tail_count,
                "upper_both_tail_count": upper_both_count,
                "upper_both_tail_probability": upper_both_prob,
                "upper_tail_dependence": upper_both_prob / alpha,
                "upper_co_rally_lift_vs_independence": upper_both_prob / (alpha * alpha),
                "upper_right_given_left_tail": upper_both_count / x_upper_tail_count
                if x_upper_tail_count
                else np.nan,
                "upper_left_given_right_tail": upper_both_count / y_upper_tail_count
                if y_upper_tail_count
                else np.nan,
                "upper_tail_union_pearson": _corr(upper_tail_pair[left], upper_tail_pair[right], "pearson")
                if upper_tail_pair.shape[0] >= 10
                else np.nan,
                "upper_avg_left_return_when_both_tail": float(x.loc[both_upper_tail].mean())
                if upper_both_count
                else np.nan,
                "upper_avg_right_return_when_both_tail": float(y.loc[both_upper_tail].mean())
                if upper_both_count
                else np.nan,
                "middle_both_count": middle_count,
                "middle_both_probability": float(both_middle.mean()),
                "middle_pearson": _corr(middle_pair[left], middle_pair[right], "pearson")
                if middle_count >= 10
                else np.nan,
                "middle_spearman": _corr(middle_pair[left], middle_pair[right], "spearman")
                if middle_count >= 10
                else np.nan,
            }
        )
        rows.append(row)

    return pd.DataFrame(rows).sort_values(
        ["lower_tail_dependence", "lower_co_crash_lift_vs_independence"], ascending=False, na_position="last"
    )


def _empty_metric_values() -> dict:
    return {
        "pearson": np.nan,
        "spearman": np.nan,
        "tail_alpha": np.nan,
        "lower_left_tail_count": np.nan,
        "lower_right_tail_count": np.nan,
        "lower_both_tail_count": np.nan,
        "lower_both_tail_probability": np.nan,
        "lower_tail_dependence": np.nan,
        "lower_co_crash_lift_vs_independence": np.nan,
        "lower_right_given_left_tail": np.nan,
        "lower_left_given_right_tail": np.nan,
        "lower_tail_union_pearson": np.nan,
        "lower_avg_left_return_when_both_tail": np.nan,
        "lower_avg_right_return_when_both_tail": np.nan,
        "upper_left_tail_count": np.nan,
        "upper_right_tail_count": np.nan,
        "upper_both_tail_count": np.nan,
        "upper_both_tail_probability": np.nan,
        "upper_tail_dependence": np.nan,
        "upper_co_rally_lift_vs_independence": np.nan,
        "upper_right_given_left_tail": np.nan,
        "upper_left_given_right_tail": np.nan,
        "upper_tail_union_pearson": np.nan,
        "upper_avg_left_return_when_both_tail": np.nan,
        "upper_avg_right_return_when_both_tail": np.nan,
        "middle_both_count": np.nan,
        "middle_both_probability": np.nan,
        "middle_pearson": np.nan,
        "middle_spearman": np.nan,
    }


def metric_matrix(metrics: pd.DataFrame, asset_ids: list[str], metric: str, diagonal: float = 1.0) -> pd.DataFrame:
    matrix = pd.DataFrame(np.nan, index=asset_ids, columns=asset_ids, dtype=float)
    for asset_id in asset_ids:
        matrix.loc[asset_id, asset_id] = diagonal
    for row in metrics.itertuples(index=False):
        value = getattr(row, metric)
        matrix.loc[row.left_id, row.right_id] = value
        matrix.loc[row.right_id, row.left_id] = value
    return matrix


def matched_sector_metrics(metrics: pd.DataFrame, sort_metric: str = "lower_tail_dependence") -> pd.DataFrame:
    matched = metrics.loc[metrics["same_sector"] & metrics["cross_market"]].copy()
    return matched.sort_values(sort_metric, ascending=False, na_position="last")


def cvine_order_from_matrix(matrix: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    values = matrix.copy()
    for asset_id in values.index:
        values.loc[asset_id, asset_id] = np.nan
    total_tail = values.sum(axis=1, skipna=True).sort_values(ascending=False)
    order = total_tail.index.tolist()
    order_df = pd.DataFrame(
        {
            "rank": range(1, len(order) + 1),
            "asset_id": order,
            "tail_dependence_sum": [total_tail.loc[item] for item in order],
        }
    )

    edges = []
    for tree_level, root in enumerate(order[:-1], start=1):
        for target in order[tree_level:]:
            edges.append(
                {
                    "tree_level": tree_level,
                    "root": root,
                    "target": target,
                    "conditioning_set": ";".join(order[: tree_level - 1]),
                    "lower_tail_dependence": matrix.loc[root, target],
                }
            )
    return order_df, pd.DataFrame(edges)
