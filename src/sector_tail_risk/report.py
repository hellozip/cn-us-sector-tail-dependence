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
        return _blend("#2166ac", "#f7f7f7", (value + 1) / 1)
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
    view = df.loc[:, columns].head(n).copy()
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
    alpha: float,
    start: str,
    end: str,
    heatmap_files: list[str],
) -> None:
    output_path = Path(output_path)
    top_cols = [
        "left_id",
        "right_id",
        "observations",
        "pearson",
        "spearman",
        "lower_tail_dependence",
        "co_crash_lift_vs_independence",
        "right_given_left_tail",
        "left_given_right_tail",
    ]
    matched_cols = [
        "left_sector",
        "left_id",
        "right_id",
        "observations",
        "pearson",
        "spearman",
        "lower_tail_dependence",
        "co_crash_lift_vs_independence",
    ]
    low_tail = metrics.loc[metrics["cross_market"]].sort_values("lower_tail_dependence", ascending=True)

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>China-US Sector Tail Dependence Report</title>
  <style>
    body {{ font-family: Arial, "Microsoft YaHei", sans-serif; margin: 32px; color: #17202a; line-height: 1.48; }}
    h1, h2 {{ margin: 24px 0 10px; }}
    .note {{ color: #4d5b66; max-width: 980px; }}
    .data-table {{ border-collapse: collapse; font-size: 13px; margin: 12px 0 24px; }}
    .data-table th, .data-table td {{ border-bottom: 1px solid #dde3ea; padding: 6px 8px; text-align: right; }}
    .data-table th:first-child, .data-table td:first-child {{ text-align: left; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 20px; align-items: start; }}
    img {{ max-width: 100%; border: 1px solid #dde3ea; }}
    code {{ background: #f4f6f8; padding: 1px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
  <h1>中美板块下尾相关性报告</h1>
  <p class="note">样本区间：<code>{escape(start)}</code> 至 <code>{escape(end)}</code>。下尾阈值 alpha = <code>{alpha:.2%}</code>。
  核心指标 <code>lower_tail_dependence = P(U_i&lt;=alpha, U_j&lt;=alpha) / alpha</code>，数值越高，表示两个板块在极端下跌日共同下跌的经验概率越高。</p>

  <h2>热力图</h2>
  <div class="grid">
    {''.join(f'<div><img src="{escape(name)}" alt="{escape(name)}"></div>' for name in heatmap_files)}
  </div>

  <h2>下尾共振最高的组合</h2>
  {_table_html(metrics, top_cols, 25)}

  <h2>同板块中美对照</h2>
  {_table_html(matched, matched_cols, 20)}

  <h2>跨市场低下尾相关候选</h2>
  {_table_html(low_tail, top_cols, 20)}

  <h2>C-Vine 经验排序</h2>
  <p class="note">这是基于下尾相关性矩阵的非参数 Vine 排序，用来判断哪个板块更像尾部风险中心节点；它不是完整的参数化 C-Vine Copula 拟合。</p>
  {_table_html(cvine_order, ["rank", "asset_id", "tail_dependence_sum"], 30)}

  <h2>资产覆盖</h2>
  {_table_html(coverage, ["id", "ticker", "first_price_date", "last_price_date", "return_observations", "annualized_return", "annualized_volatility"], 30)}

  <h2>代理标的</h2>
  {assets.to_html(index=False, escape=True, border=0, classes="data-table")}
</body>
</html>
"""
    output_path.write_text(html, encoding="utf-8")

