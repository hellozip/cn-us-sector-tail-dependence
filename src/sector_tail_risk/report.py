from __future__ import annotations

from html import escape
from pathlib import Path

import numpy as np
import pandas as pd


def _lerp(a: int, b: int, t: float) -> int:
    return int(round(a + (b - a) * t))


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _blend(low: str, high: str, t: float) -> str:
    t = max(0.0, min(1.0, t))
    lo = _hex_to_rgb(low)
    hi = _hex_to_rgb(high)
    return _rgb_to_hex(tuple(_lerp(lo[i], hi[i], t) for i in range(3)))


def _diverging_color(value: float) -> str:
    if pd.isna(value):
        return "#eeeeee"
    value = max(-1.0, min(1.0, float(value)))
    if value < 0:
        return _blend("#2166ac", "#f7f7f7", value + 1)
    return _blend("#f7f7f7", "#b2182b", value)


def _sequential_color(value: float, vmin: float, vmax: float) -> str:
    if pd.isna(value):
        return "#eeeeee"
    if vmax <= vmin:
        return "#f7fbff"
    t = (float(value) - vmin) / (vmax - vmin)
    return _blend("#f7fbff", "#b2182b", t)


def write_svg_heatmap(
    matrix: pd.DataFrame,
    output_path: str | Path,
    title: str,
    diverging: bool = False,
    value_format: str = ".2f",
) -> None:
    output_path = Path(output_path)
    labels = list(matrix.index)
    n = len(labels)
    cell = 31
    left = 180
    top = 150
    width = left + n * cell + 30
    height = top + n * cell + 50

    vals = matrix.to_numpy(dtype=float)
    finite = vals[np.isfinite(vals)]
    vmin = float(np.nanmin(finite)) if finite.size else 0.0
    vmax = float(np.nanmax(finite)) if finite.size else 1.0
    if not diverging:
        vmin = 0.0
        vmax = max(1.0, vmax)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>text{font-family:Arial,Microsoft YaHei,sans-serif;font-size:10px;fill:#222}.title{font-size:18px;font-weight:700}.axis{font-size:10px}.celltext{font-size:8px;fill:#111}</style>",
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="20" y="32" class="title">{escape(title)}</text>',
    ]

    for idx, label in enumerate(labels):
        x = left + idx * cell + cell / 2
        lines.append(
            f'<text x="{x:.1f}" y="{top - 8}" class="axis" transform="rotate(-45 {x:.1f},{top - 8})">{escape(label)}</text>'
        )
        y = top + idx * cell + cell / 2 + 4
        lines.append(f'<text x="{left - 8}" y="{y:.1f}" class="axis" text-anchor="end">{escape(label)}</text>')

    for row_idx, row_label in enumerate(labels):
        for col_idx, col_label in enumerate(labels):
            value = matrix.loc[row_label, col_label]
            fill = _diverging_color(value) if diverging else _sequential_color(value, vmin, vmax)
            x = left + col_idx * cell
            y = top + row_idx * cell
            lines.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{fill}" stroke="#ffffff"/>')
            if pd.notna(value):
                text = format(float(value), value_format)
                lines.append(
                    f'<text x="{x + cell / 2:.1f}" y="{y + cell / 2 + 3:.1f}" class="celltext" text-anchor="middle">{text}</text>'
                )

    lines.append("</svg>")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _table_html(df: pd.DataFrame, columns: list[str], n: int = 20) -> str:
    if df.empty:
        return "<p>No rows.</p>"
    available = [column for column in columns if column in df.columns]
    if not available:
        return "<p>No matching columns.</p>"
    view = df.loc[:, available].head(n).copy()
    for col in view.select_dtypes(include=[float]).columns:
        view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.4f}")
    return view.to_html(index=False, escape=True, border=0, classes="data-table")


def write_html_report(
    output_path: str | Path,
    assets: pd.DataFrame,
    coverage: pd.DataFrame,
    metrics: pd.DataFrame,
    matched: pd.DataFrame,
    cvine_order: pd.DataFrame,
    garch_params: pd.DataFrame,
    latest_regime: pd.DataFrame,
    flow_candidates: pd.DataFrame,
    risk_candidates: pd.DataFrame,
    alpha: float,
    start: str,
    end: str,
    heatmap_files: list[str],
    input_label: str,
) -> None:
    output_path = Path(output_path)
    lower_cols = [
        "left_id",
        "right_id",
        "observations",
        "pearson",
        "spearman",
        "lower_tail_dependence",
        "lower_co_crash_lift_vs_independence",
        "lower_right_given_left_tail",
        "lower_left_given_right_tail",
    ]
    upper_cols = [
        "left_id",
        "right_id",
        "observations",
        "pearson",
        "spearman",
        "upper_tail_dependence",
        "upper_co_rally_lift_vs_independence",
        "upper_right_given_left_tail",
        "upper_left_given_right_tail",
    ]
    middle_cols = [
        "left_id",
        "right_id",
        "observations",
        "middle_both_count",
        "middle_pearson",
        "middle_spearman",
        "pearson",
        "spearman",
    ]
    matched_cols = [
        "left_sector",
        "left_id",
        "right_id",
        "observations",
        "lower_tail_dependence",
        "upper_tail_dependence",
        "middle_pearson",
        "middle_spearman",
        "pearson",
        "spearman",
    ]
    garch_cols = [
        "id",
        "status",
        "mean",
        "omega",
        "alpha",
        "beta",
        "persistence",
        "observations",
    ]
    latest_cols = [
        "as_of_date",
        "id",
        "market",
        "sector",
        "latest_return",
        "garch_sigma",
        "standardized_residual",
        "empirical_percentile",
        "regime",
        "regime_strength",
    ]
    signal_cols = [
        "signal_type",
        "source_id",
        "target_id",
        "source_regime",
        "target_regime",
        "source_percentile",
        "target_percentile",
        "relation_metric",
        "score",
        "interpretation",
    ]

    lower_top = metrics.sort_values("lower_tail_dependence", ascending=False, na_position="last")
    upper_top = metrics.sort_values("upper_tail_dependence", ascending=False, na_position="last")
    middle_top = metrics.sort_values("middle_pearson", ascending=False, na_position="last")
    lower_low_cross_market = metrics.loc[metrics["cross_market"]].sort_values(
        "lower_tail_dependence", ascending=True, na_position="last"
    )
    upper_low_cross_market = metrics.loc[metrics["cross_market"]].sort_values(
        "upper_tail_dependence", ascending=True, na_position="last"
    )

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>China-US Sector Dependence Report</title>
  <style>
    body {{ font-family: Arial, "Microsoft YaHei", sans-serif; margin: 32px; color: #17202a; line-height: 1.48; }}
    h1, h2 {{ margin: 24px 0 10px; }}
    .note {{ color: #4d5b66; max-width: 1040px; }}
    .data-table {{ border-collapse: collapse; font-size: 13px; margin: 12px 0 24px; }}
    .data-table th, .data-table td {{ border-bottom: 1px solid #dde3ea; padding: 6px 8px; text-align: right; }}
    .data-table th:first-child, .data-table td:first-child {{ text-align: left; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 20px; align-items: start; }}
    img {{ max-width: 100%; border: 1px solid #dde3ea; }}
    code {{ background: #f4f6f8; padding: 1px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
  <h1>China-US Sector Dependence Report</h1>
  <p class="note">Sample window: <code>{escape(start)}</code> to <code>{escape(end)}</code>. Tail alpha = <code>{alpha:.2%}</code>.</p>
  <p class="note">Dependence input: <code>{escape(input_label)}</code>. The default workflow removes conditional volatility with GARCH before computing empirical Copula dependence.</p>
  <p class="note">
    Lower tail: <code>P(U_i&lt;=alpha, U_j&lt;=alpha) / alpha</code>.
    Upper tail: <code>P(U_i&gt;=1-alpha, U_j&gt;=1-alpha) / alpha</code>.
    Middle correlation: Pearson/Spearman correlation conditional on both assets staying inside <code>(alpha, 1-alpha)</code>.
  </p>

  <h2>Heatmaps</h2>
  <div class="grid">
    {''.join(f'<div><img src="{escape(name)}" alt="{escape(name)}"></div>' for name in heatmap_files)}
  </div>

  <h2>Latest GARCH-Standardized Regime</h2>
  <p class="note">The latest row classifies each sector by today's standardized residual percentile versus its own historical GARCH-standardized residual distribution.</p>
  {_table_html(latest_regime, latest_cols, 30)}

  <h2>Potential Flow Candidates</h2>
  <p class="note">Candidates are inferred from current upper-tail or positive middle-regime leaders and their historical upper-tail or middle-market dependence with other sectors. These are follow-through candidates, not deterministic forecasts.</p>
  {_table_html(flow_candidates, signal_cols, 30)}

  <h2>Downside Contagion Watchlist</h2>
  <p class="note">This table uses current lower-tail stress and historical lower-tail dependence to flag sectors that may share downside pressure.</p>
  {_table_html(risk_candidates, signal_cols, 30)}

  <h2>Highest Lower-Tail Co-Crash Dependence</h2>
  {_table_html(lower_top, lower_cols, 25)}

  <h2>Highest Upper-Tail Co-Rally Dependence</h2>
  {_table_html(upper_top, upper_cols, 25)}

  <h2>Highest Middle-Market Correlation</h2>
  {_table_html(middle_top, middle_cols, 25)}

  <h2>Matched China-US Sectors</h2>
  {_table_html(matched, matched_cols, 20)}

  <h2>Cross-Market Low Lower-Tail Candidates</h2>
  {_table_html(lower_low_cross_market, lower_cols, 20)}

  <h2>Cross-Market Low Upper-Tail Candidates</h2>
  {_table_html(upper_low_cross_market, upper_cols, 20)}

  <h2>Lower-Tail Empirical C-Vine Order</h2>
  <p class="note">This non-parametric ordering uses the lower-tail dependence matrix to identify assets that behave like co-crash hubs. It is not a full parameterized C-Vine Copula fit.</p>
  {_table_html(cvine_order, ["rank", "asset_id", "tail_dependence_sum"], 30)}

  <h2>GARCH Parameters</h2>
  {_table_html(garch_params, garch_cols, 30)}

  <h2>Asset Coverage</h2>
  {_table_html(coverage, ["id", "ticker", "first_price_date", "last_price_date", "return_observations", "annualized_return", "annualized_volatility"], 30)}

  <h2>Asset Proxies</h2>
  {assets.to_html(index=False, escape=True, border=0, classes="data-table")}
</body>
</html>
"""
    output_path.write_text(html, encoding="utf-8")
