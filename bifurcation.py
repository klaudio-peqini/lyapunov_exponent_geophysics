"""
Bifurcation workflows + plotting.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
import matplotlib.pyplot as plt

from .lyapunov import SeriesLyapunovConfig, lyapunov_exponent_series
from .maps import gaussian_map, logistic_exponential_map, logistic_map


@dataclass(frozen=True)
class BifurcationConfig:
    steps: int = 2000
    last: int = 300
    rounding: int = 4
    le: SeriesLyapunovConfig = SeriesLyapunovConfig()


def _steady_state(series: np.ndarray, last: int, rounding: int) -> np.ndarray:
    tail = np.round(series[-last:], rounding)
    return np.unique(tail)


def logistic_bifurcation(
    r_min: float,
    r_max: float,
    dr: float,
    x0: float,
    cfg: BifurcationConfig,
) -> Tuple[np.ndarray, list[np.ndarray], np.ndarray, np.ndarray]:
    r_vals = np.arange(r_min, r_max, dr, dtype=float)
    steady = []
    le_series = np.empty_like(r_vals)
    le_formula = np.empty_like(r_vals)

    for idx, r in enumerate(r_vals):
        x = logistic_map(r, x0, cfg.steps)
        steady.append(_steady_state(x, cfg.last, cfg.rounding))
        le_formula[idx] = np.mean(np.log(np.abs(r * (1.0 - 2.0 * x))))
        le_series[idx] = lyapunov_exponent_series(x, cfg.le)

    return r_vals, steady, le_formula, le_series


def gaussian_bifurcation(
    beta_min: float,
    beta_max: float,
    db: float,
    alpha: float,
    x0: float,
    cfg: BifurcationConfig,
) -> Tuple[np.ndarray, list[np.ndarray], np.ndarray, np.ndarray]:
    beta_vals = np.arange(beta_min, beta_max, db, dtype=float)
    steady = []
    le_series = np.empty_like(beta_vals)
    le_formula = np.empty_like(beta_vals)

    for idx, b in enumerate(beta_vals):
        x = gaussian_map(alpha, b, x0, cfg.steps)
        steady.append(_steady_state(x, cfg.last, cfg.rounding))
        # derivative: d/dx exp(-a x^2) = -2 a x exp(-a x^2)
        le_formula[idx] = np.mean(np.log(np.abs(-2.0 * alpha * x * np.exp(-alpha * x**2))))
        le_series[idx] = lyapunov_exponent_series(x, cfg.le)

    return beta_vals, steady, le_formula, le_series


def logexp_bifurcation(
    r_min: float,
    r_max: float,
    dr: float,
    x0: float,
    cfg: BifurcationConfig,
) -> Tuple[np.ndarray, list[np.ndarray], np.ndarray, np.ndarray]:
    r_vals = np.arange(r_min, r_max, dr, dtype=float)
    steady = []
    le_series = np.empty_like(r_vals)
    le_formula = np.empty_like(r_vals)

    for idx, r in enumerate(r_vals):
        x = logistic_exponential_map(r, x0, cfg.steps)
        steady.append(_steady_state(x, cfg.last, cfg.rounding))
        fp = np.exp(r * (1.0 - x)) - r * x * np.exp(r * (1.0 - x))
        le_formula[idx] = np.mean(np.log(np.abs(fp)))
        le_series[idx] = lyapunov_exponent_series(x, cfg.le)

    return r_vals, steady, le_formula, le_series


def plot_bifurcation(
    param: np.ndarray,
    steady: list[np.ndarray],
    le_formula: np.ndarray,
    le_series: np.ndarray,
    xlabel: str,
    outpath: str,
    title: str,
):
    plt.figure(figsize=(10, 6))

    ax1 = plt.subplot(211)
    for i in range(len(param)):
        ax1.plot([param[i]] * len(steady[i]), steady[i], "m.", markersize=2)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel(xlabel, fontsize=13)
    ax1.set_ylabel("Steady state values", fontsize=13)

    ax2 = plt.subplot(212)
    ax2.plot(param, le_formula, lw=2, label="Derivative formula")
    ax2.plot(param, le_series, lw=2, label="Series estimator")
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel(xlabel, fontsize=13)
    ax2.set_ylabel("Lyapunov exponent", fontsize=13)
    ax2.legend(loc="best")

    plt.suptitle(title, fontsize=14)
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()
