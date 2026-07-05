from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sector_tail_risk.analytics import (  # noqa: E402
    compute_log_returns,
    coverage_table,
    cvine_order_from_matrix,
    matched_sector_metrics,
    metric_matrix,
    pairwise_tail_metrics,
    read_assets,
)
from sector_tail_risk.garch import standardize_with_garch  # noqa: E402
from sector_tail_risk.report import write_html_report, write_svg_heatmap  # noqa: E402
from sector_tail_risk.signals import (  # noqa: E402
    build_flow_candidates,
    build_latest_regime,
    build_risk_contagion_candidates,
)
from sector_tail_risk.yahoo import fetch_price_volume  # noqa: E402


def _date_arg(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_args() -> argparse.Namespace:
    default_end = date.today()
    default_start = default_end - timedelta(days=365 * 7)
    parser = argparse.ArgumentParser(description="China-US sector tail-dependence analysis")
    parser.add_argument("--config", default=str(PROJECT_ROOT / "config" / "sector_assets.csv"))
    parser.add_argument("--start", default=default_start.isoformat(), help="Start date, YYYY-MM-DD")
    parser.add_argument("--end", default=default_end.isoformat(), help="End date, YYYY-MM-DD")
    parser.add_argument("--alpha", type=float, default=0.05, help="Lower-tail quantile threshold")
    parser.add_argument("--min-obs", type=int, default=500, help="Minimum pairwise observations")
    parser.add_argument("--output", default=str(PROJECT_ROOT / "outputs" / "latest"))
    parser.add_argument("--prices", default="", help="Optional existing price CSV to skip network fetching")
    parser.add_argument("--volumes", default="", help="Optional existing volume CSV to skip network fetching")
    parser.add_argument("--no-garch", action="store_true", help="Use raw returns instead of GARCH-standardized residuals")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    assets = read_assets(args.config)
    start = _date_arg(args.start)
    end = _date_arg(args.end)
    if start >= end:
        raise ValueError("--start must be before --end")

    if args.prices:
        prices = pd.read_csv(args.prices, index_col=0, parse_dates=True)
        volumes = pd.read_csv(args.volumes, index_col=0, parse_dates=True) if args.volumes else pd.DataFrame(index=prices.index)
        yahoo_meta = pd.DataFrame()
    else:
        prices, volumes, yahoo_meta = fetch_price_volume(assets, start, end)

    returns = compute_log_returns(prices)
    coverage = coverage_table(prices, returns, assets)
    if args.no_garch:
        analysis_input = returns.copy()
        sigma = pd.DataFrame(index=returns.index, columns=returns.columns, dtype=float)
        garch_params = pd.DataFrame(
            {
                "id": returns.columns,
                "status": "disabled",
                "observations": [int(returns[column].notna().sum()) for column in returns.columns],
            }
        )
        input_label = "raw log returns"
    else:
        analysis_input, sigma, garch_params = standardize_with_garch(returns, min_obs=args.min_obs)
        input_label = "GARCH(1,1)-standardized residuals"

    metrics = pairwise_tail_metrics(analysis_input, assets, alpha=args.alpha, min_obs=args.min_obs)
    latest_regime = build_latest_regime(analysis_input, returns, sigma, assets, alpha=args.alpha)
    flow_candidates = build_flow_candidates(metrics, latest_regime)
    risk_candidates = build_risk_contagion_candidates(metrics, latest_regime)

    asset_ids = assets["id"].tolist()
    lower_tail_matrix = metric_matrix(metrics, asset_ids, "lower_tail_dependence", diagonal=1.0)
    upper_tail_matrix = metric_matrix(metrics, asset_ids, "upper_tail_dependence", diagonal=1.0)
    middle_pearson_matrix = metric_matrix(metrics, asset_ids, "middle_pearson", diagonal=1.0)
    middle_spearman_matrix = metric_matrix(metrics, asset_ids, "middle_spearman", diagonal=1.0)
    pearson_matrix = metric_matrix(metrics, asset_ids, "pearson", diagonal=1.0)
    spearman_matrix = metric_matrix(metrics, asset_ids, "spearman", diagonal=1.0)
    lower_lift_matrix = metric_matrix(metrics, asset_ids, "lower_co_crash_lift_vs_independence", diagonal=1.0)
    upper_lift_matrix = metric_matrix(metrics, asset_ids, "upper_co_rally_lift_vs_independence", diagonal=1.0)
    matched = matched_sector_metrics(metrics)
    cvine_order, cvine_edges = cvine_order_from_matrix(lower_tail_matrix)

    prices.to_csv(output_dir / "prices.csv", encoding="utf-8-sig")
    if not volumes.empty:
        volumes.to_csv(output_dir / "volumes.csv", encoding="utf-8-sig")
        prices.mul(volumes).to_csv(output_dir / "turnover_amount.csv", encoding="utf-8-sig")
    returns.to_csv(output_dir / "returns.csv", encoding="utf-8-sig")
    analysis_input.to_csv(output_dir / "standardized_residuals.csv", encoding="utf-8-sig")
    sigma.to_csv(output_dir / "garch_conditional_sigma.csv", encoding="utf-8-sig")
    garch_params.to_csv(output_dir / "garch_params.csv", index=False, encoding="utf-8-sig")
    assets.to_csv(output_dir / "asset_config_used.csv", index=False, encoding="utf-8-sig")
    if not yahoo_meta.empty:
        yahoo_meta.to_csv(output_dir / "yahoo_metadata.csv", index=False, encoding="utf-8-sig")
    coverage.to_csv(output_dir / "asset_coverage.csv", index=False, encoding="utf-8-sig")
    metrics.to_csv(output_dir / f"pair_metrics_alpha_{args.alpha:.2f}.csv", index=False, encoding="utf-8-sig")
    matched.to_csv(output_dir / f"matched_sector_metrics_alpha_{args.alpha:.2f}.csv", index=False, encoding="utf-8-sig")
    lower_tail_matrix.to_csv(output_dir / f"lower_tail_dependence_matrix_alpha_{args.alpha:.2f}.csv", encoding="utf-8-sig")
    upper_tail_matrix.to_csv(output_dir / f"upper_tail_dependence_matrix_alpha_{args.alpha:.2f}.csv", encoding="utf-8-sig")
    middle_pearson_matrix.to_csv(output_dir / f"middle_pearson_matrix_alpha_{args.alpha:.2f}.csv", encoding="utf-8-sig")
    middle_spearman_matrix.to_csv(output_dir / f"middle_spearman_matrix_alpha_{args.alpha:.2f}.csv", encoding="utf-8-sig")
    lower_lift_matrix.to_csv(output_dir / f"lower_co_crash_lift_matrix_alpha_{args.alpha:.2f}.csv", encoding="utf-8-sig")
    upper_lift_matrix.to_csv(output_dir / f"upper_co_rally_lift_matrix_alpha_{args.alpha:.2f}.csv", encoding="utf-8-sig")
    pearson_matrix.to_csv(output_dir / "pearson_matrix.csv", encoding="utf-8-sig")
    spearman_matrix.to_csv(output_dir / "spearman_matrix.csv", encoding="utf-8-sig")
    cvine_order.to_csv(output_dir / "cvine_empirical_order.csv", index=False, encoding="utf-8-sig")
    cvine_edges.to_csv(output_dir / "cvine_empirical_edges.csv", index=False, encoding="utf-8-sig")
    latest_regime.to_csv(output_dir / f"latest_regime_alpha_{args.alpha:.2f}.csv", index=False, encoding="utf-8-sig")
    flow_candidates.to_csv(output_dir / f"flow_candidates_alpha_{args.alpha:.2f}.csv", index=False, encoding="utf-8-sig")
    risk_candidates.to_csv(output_dir / f"risk_contagion_candidates_alpha_{args.alpha:.2f}.csv", index=False, encoding="utf-8-sig")

    heatmaps = [
        (lower_tail_matrix, "lower_tail_dependence.svg", f"Lower-tail dependence, alpha={args.alpha:.0%}", False, ".2f"),
        (upper_tail_matrix, "upper_tail_dependence.svg", f"Upper-tail dependence, alpha={args.alpha:.0%}", False, ".2f"),
        (middle_pearson_matrix, "middle_pearson_correlation.svg", f"Middle Pearson correlation, alpha={args.alpha:.0%}", True, ".2f"),
        (middle_spearman_matrix, "middle_spearman_correlation.svg", f"Middle Spearman correlation, alpha={args.alpha:.0%}", True, ".2f"),
        (lower_lift_matrix, "lower_co_crash_lift.svg", "Lower-tail co-crash lift vs independence", False, ".1f"),
        (upper_lift_matrix, "upper_co_rally_lift.svg", "Upper-tail co-rally lift vs independence", False, ".1f"),
        (pearson_matrix, "pearson_correlation.svg", "Pearson correlation", True, ".2f"),
        (spearman_matrix, "spearman_correlation.svg", "Spearman correlation", True, ".2f"),
    ]
    heatmap_names: list[str] = []
    for matrix, filename, title, diverging, fmt in heatmaps:
        write_svg_heatmap(matrix, output_dir / filename, title=title, diverging=diverging, value_format=fmt)
        heatmap_names.append(filename)

    write_html_report(
        output_dir / "report.html",
        assets=assets,
        coverage=coverage,
        metrics=metrics,
        matched=matched,
        cvine_order=cvine_order,
        garch_params=garch_params,
        latest_regime=latest_regime,
        flow_candidates=flow_candidates,
        risk_candidates=risk_candidates,
        alpha=args.alpha,
        start=start.isoformat(),
        end=end.isoformat(),
        heatmap_files=heatmap_names,
        input_label=input_label,
    )

    print(f"Done. Report: {output_dir / 'report.html'}")
    print(
        f"Rows: prices={prices.shape}, returns={returns.shape}, "
        f"analysis_input={analysis_input.shape}, pair_metrics={metrics.shape}"
    )


if __name__ == "__main__":
    main()
