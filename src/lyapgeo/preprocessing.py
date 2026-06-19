from __future__ import annotations
import numpy as np

def clean_series(x: np.ndarray) -> np.ndarray:
    y = np.asarray(x, dtype=float).ravel()
    return y[np.isfinite(y)]

def normalize_series(x: np.ndarray, mode: str = "none") -> np.ndarray:
    y = clean_series(x)
    if mode == "none": return y
    if mode == "demean": return y - np.mean(y)
    if mode == "zscore":
        s = np.std(y)
        return (y - np.mean(y)) / s if s > 0 else y - np.mean(y)
    if mode == "minmax":
        a, b = np.min(y), np.max(y)
        return (y - a) / (b - a) if b > a else y * 0.0
    raise ValueError(f"Unknown normalization mode: {mode}")

def delay_embedding(x: np.ndarray, emb_dim: int, tau: int) -> np.ndarray:
    y = np.asarray(x, dtype=float).ravel()
    if emb_dim < 1: raise ValueError("emb_dim must be >= 1")
    if tau < 1: raise ValueError("tau must be >= 1")
    m = y.size - (emb_dim - 1) * tau
    if m <= 1: raise ValueError("Series too short for requested embedding.")
    return np.column_stack([y[i * tau : i * tau + m] for i in range(emb_dim)])
