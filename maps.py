"""
Discrete maps used in bifurcation experiments.
"""
from __future__ import annotations

import numpy as np


def logistic_map(r: float, x0: float, steps: int) -> np.ndarray:
    x = np.empty(steps + 1, dtype=float)
    x[0] = x0
    for i in range(steps):
        x[i + 1] = r * x[i] * (1.0 - x[i])
    return x[1:]


def gaussian_map(alpha: float, beta: float, x0: float, steps: int) -> np.ndarray:
    x = np.empty(steps + 1, dtype=float)
    x[0] = x0
    for i in range(steps):
        x[i + 1] = np.exp(-alpha * x[i] ** 2) + beta
    return x[1:]


def logistic_exponential_map(r: float, x0: float, steps: int) -> np.ndarray:
    x = np.empty(steps + 1, dtype=float)
    x[0] = x0
    for i in range(steps):
        x[i + 1] = x[i] * np.exp(r * (1.0 - x[i]))
    return x[1:]
