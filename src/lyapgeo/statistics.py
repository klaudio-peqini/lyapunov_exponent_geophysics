from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class SummaryConfig:
    n_bootstrap: int = 2000
    ci: float = 0.95
    seed: int = 0
    center: str = "median"

def bootstrap_ci(values: np.ndarray, cfg: SummaryConfig) -> tuple[float, float]:
    x = np.asarray(values, dtype=float); x = x[np.isfinite(x)]
    if x.size == 0: return float("nan"), float("nan")
    if x.size == 1 or cfg.n_bootstrap <= 0: return float(x[0]), float(x[0])
    rng = np.random.default_rng(cfg.seed)
    idx = rng.integers(0, x.size, size=(cfg.n_bootstrap, x.size))
    samples = x[idx]
    stat = np.mean(samples, axis=1) if cfg.center == "mean" else np.median(samples, axis=1)
    alpha = (1.0 - cfg.ci) / 2.0
    return tuple(np.quantile(stat, [alpha, 1.0 - alpha]).astype(float))

def summarize_local_estimates(values: np.ndarray, cfg: SummaryConfig = SummaryConfig()) -> dict[str, float | int]:
    x = np.asarray(values, dtype=float); x = x[np.isfinite(x)]
    if x.size == 0:
        return {"estimate": float("nan"), "ci_low": float("nan"), "ci_high": float("nan"), "median": float("nan"), "mean": float("nan"), "std": float("nan"), "n_local": 0}
    ci_low, ci_high = bootstrap_ci(x, cfg)
    center = float(np.mean(x)) if cfg.center == "mean" else float(np.median(x))
    return {"estimate": center, "ci_low": ci_low, "ci_high": ci_high, "median": float(np.median(x)), "mean": float(np.mean(x)), "std": float(np.std(x, ddof=1)) if x.size > 1 else 0.0, "n_local": int(x.size)}

def optimal_histogram(values: np.ndarray, rule: str = "fd") -> tuple[np.ndarray, np.ndarray, str]:
    x = np.asarray(values, dtype=float); x = x[np.isfinite(x)]
    if x.size == 0: return np.array([]), np.array([]), rule
    if rule == "fd":
        q25, q75 = np.percentile(x, [25, 75]); iqr = q75 - q25
        width = 2 * iqr / np.cbrt(x.size) if iqr > 0 else 0
        bins = max(5, int(np.ceil((np.max(x) - np.min(x)) / width))) if width > 0 else "sturges"
    elif rule == "scott":
        sigma = np.std(x, ddof=1) if x.size > 1 else 0
        width = 3.5 * sigma / np.cbrt(x.size) if sigma > 0 else 0
        bins = max(5, int(np.ceil((np.max(x) - np.min(x)) / width))) if width > 0 else "sturges"
    elif rule in {"sturges", "auto"}: bins = rule
    else: raise ValueError("rule must be fd, scott, sturges, or auto")
    density, edges = np.histogram(x, bins=bins, density=True)
    return 0.5 * (edges[:-1] + edges[1:]), density, rule
