from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
import numpy as np

@dataclass
class LyapunovResult:
    method: str
    estimate: float
    ci_low: float
    ci_high: float
    median: float
    mean: float
    std: float
    n_local: int
    fit_start: int
    fit_end: int
    emb_dim: int
    tau: int
    horizon: int
    local_estimates: np.ndarray
    divergence_k: np.ndarray | None = None
    divergence_log_mean: np.ndarray | None = None

    def summary_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("local_estimates", None)
        d.pop("divergence_k", None)
        d.pop("divergence_log_mean", None)
        return d
