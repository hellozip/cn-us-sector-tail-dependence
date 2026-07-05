from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class GarchFit:
    mean: float
    omega: float
    alpha: float
    beta: float
    persistence: float
    unconditional_variance: float
    neg_log_likelihood: float
    sigma: pd.Series
    standardized_residual: pd.Series


def _garch_variance(eps: np.ndarray, alpha: float, beta: float, variance: float) -> np.ndarray:
    persistence = alpha + beta
    omega = max(variance * (1.0 - persistence), 1e-14)
    h = np.empty_like(eps, dtype=float)
    h[0] = max(variance, 1e-14)
    for idx in range(1, eps.shape[0]):
        h[idx] = omega + alpha * eps[idx - 1] ** 2 + beta * h[idx - 1]
        if not np.isfinite(h[idx]) or h[idx] <= 1e-14:
            h[idx] = 1e-14
    return h


def _negative_log_likelihood(eps: np.ndarray, alpha: float, beta: float, variance: float) -> float:
    if alpha <= 0 or beta < 0 or alpha + beta >= 0.999:
        return float("inf")
    h = _garch_variance(eps, alpha, beta, variance)
    return float(0.5 * np.sum(np.log(h) + (eps * eps) / h))


def _fit_alpha_beta(eps: np.ndarray, variance: float) -> tuple[float, float, float]:
    # Coarse grid over ARCH weight and persistence, followed by a small pattern search.
    best_alpha = 0.05
    best_beta = 0.90
    best_nll = _negative_log_likelihood(eps, best_alpha, best_beta, variance)

    alpha_grid = np.array([0.01, 0.02, 0.035, 0.05, 0.075, 0.10, 0.13, 0.16, 0.20])
    persistence_grid = np.array([0.70, 0.80, 0.88, 0.92, 0.95, 0.97, 0.985, 0.995])
    for alpha in alpha_grid:
        for persistence in persistence_grid:
            beta = persistence - alpha
            if beta < 0:
                continue
            nll = _negative_log_likelihood(eps, float(alpha), float(beta), variance)
            if nll < best_nll:
                best_alpha, best_beta, best_nll = float(alpha), float(beta), nll

    for step in [0.05, 0.025, 0.0125, 0.00625, 0.003, 0.0015, 0.00075]:
        improved = True
        while improved:
            improved = False
            candidates = []
            for da in (-step, 0.0, step):
                for db in (-step, 0.0, step):
                    if da == 0.0 and db == 0.0:
                        continue
                    alpha = best_alpha + da
                    beta = best_beta + db
                    if alpha <= 1e-5 or beta < 0 or alpha + beta >= 0.999:
                        continue
                    candidates.append((alpha, beta))
            for alpha, beta in candidates:
                nll = _negative_log_likelihood(eps, alpha, beta, variance)
                if nll + 1e-9 < best_nll:
                    best_alpha, best_beta, best_nll = alpha, beta, nll
                    improved = True

    return best_alpha, best_beta, best_nll


def fit_garch_11(series: pd.Series, min_obs: int = 500) -> GarchFit | None:
    clean = series.dropna().astype(float)
    if clean.shape[0] < min_obs:
        return None

    mean = float(clean.mean())
    eps = (clean - mean).to_numpy(dtype=float)
    variance = float(np.var(eps, ddof=1))
    if not np.isfinite(variance) or variance <= 1e-14:
        return None

    alpha, beta, nll = _fit_alpha_beta(eps, variance)
    h = _garch_variance(eps, alpha, beta, variance)
    sigma_clean = pd.Series(np.sqrt(h), index=clean.index, name=series.name)
    standardized_clean = pd.Series(eps / np.sqrt(h), index=clean.index, name=series.name)

    sigma = pd.Series(np.nan, index=series.index, name=series.name, dtype=float)
    standardized = pd.Series(np.nan, index=series.index, name=series.name, dtype=float)
    sigma.loc[sigma_clean.index] = sigma_clean
    standardized.loc[standardized_clean.index] = standardized_clean

    persistence = alpha + beta
    omega = max(variance * (1.0 - persistence), 1e-14)
    return GarchFit(
        mean=mean,
        omega=omega,
        alpha=alpha,
        beta=beta,
        persistence=persistence,
        unconditional_variance=variance,
        neg_log_likelihood=nll,
        sigma=sigma,
        standardized_residual=standardized,
    )


def standardize_with_garch(returns: pd.DataFrame, min_obs: int = 500) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    standardized_columns: list[pd.Series] = []
    sigma_columns: list[pd.Series] = []
    param_rows: list[dict] = []

    for column in returns.columns:
        fit = fit_garch_11(returns[column], min_obs=min_obs)
        if fit is None:
            standardized_columns.append(pd.Series(np.nan, index=returns.index, name=column, dtype=float))
            sigma_columns.append(pd.Series(np.nan, index=returns.index, name=column, dtype=float))
            param_rows.append(
                {
                    "id": column,
                    "status": "insufficient_or_constant_data",
                    "mean": np.nan,
                    "omega": np.nan,
                    "alpha": np.nan,
                    "beta": np.nan,
                    "persistence": np.nan,
                    "unconditional_variance": np.nan,
                    "neg_log_likelihood": np.nan,
                    "observations": int(returns[column].notna().sum()),
                }
            )
            continue

        standardized_columns.append(fit.standardized_residual)
        sigma_columns.append(fit.sigma)
        param_rows.append(
            {
                "id": column,
                "status": "ok",
                "mean": fit.mean,
                "omega": fit.omega,
                "alpha": fit.alpha,
                "beta": fit.beta,
                "persistence": fit.persistence,
                "unconditional_variance": fit.unconditional_variance,
                "neg_log_likelihood": fit.neg_log_likelihood,
                "observations": int(returns[column].notna().sum()),
            }
        )

    standardized = pd.concat(standardized_columns, axis=1).sort_index()
    sigma = pd.concat(sigma_columns, axis=1).sort_index()
    params = pd.DataFrame(param_rows)
    return standardized, sigma, params

