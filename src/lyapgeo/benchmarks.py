from __future__ import annotations
import numpy as np

def logistic_series(r: float, x0: float, n: int, discard: int = 1000) -> np.ndarray:
    x = np.empty(n + discard + 1, dtype=float); x[0] = x0
    for i in range(n + discard): x[i + 1] = r * x[i] * (1.0 - x[i])
    return x[discard + 1:]

def logistic_true_lyapunov(r: float, x: np.ndarray) -> float:
    return float(np.mean(np.log(np.abs(r * (1.0 - 2.0 * x)))))
