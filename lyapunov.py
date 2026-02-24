"""
Lyapunov exponent estimators (time series).

This module contains a fast estimator for the largest Lyapunov exponent from a *scalar* time series.
It is intended as a practical replacement for the original O(N^2) nested-loop prototype found in
`radon_processing.py`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass(frozen=True)
class SeriesLyapunovConfig:
    eps: float = 0.01
    l: int = 5
    max_pairs: int = 1000
    min_separation: int = 10  # ignore temporally-near pairs (|i-j| <= this)
    seed: int = 0
    tiny: float = 1e-12


def _pair_candidates_1d(
    x: np.ndarray,
    l: int,
    eps: float,
    max_pairs: int,
    min_separation: int,
    rng: np.random.Generator,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Find up to `max_pairs` index pairs (i, j) such that |x[i] - x[j]| < eps.

    Method:
      - Sort values once (1D) and use a sliding window of width `eps` to find neighbors.
      - Filter out temporally-close pairs to reduce bias.
      - Subsample large neighbor sets to stay fast on quantized/flat signals.
    """
    n = int(x.shape[0])
    n_eff = n - l  # ensure i+k, j+k valid for k in [0..l-1]
    if n_eff <= 1:
        return np.array([], dtype=int), np.array([], dtype=int)

    vals = x[:n_eff]
    order = np.argsort(vals, kind="mergesort")
    sorted_vals = vals[order]

    pairs_i: list[int] = []
    pairs_j: list[int] = []

    right = 1
    for left in range(n_eff):
        if right < left + 1:
            right = left + 1
        while right < n_eff and (sorted_vals[right] - sorted_vals[left]) < eps:
            right += 1

        if right <= left + 1:
            continue

        i_idx = int(order[left])
        cand = order[left + 1 : right]

        if min_separation > 0:
            cand = cand[np.abs(cand - i_idx) > min_separation]
        if cand.size == 0:
            continue

        # Subsample if too many neighbors
        if cand.size > 32:
            cand = rng.choice(cand, size=min(8, cand.size), replace=False)

        for j_idx in cand:
            pairs_i.append(i_idx)
            pairs_j.append(int(j_idx))
            if len(pairs_i) >= max_pairs:
                return np.asarray(pairs_i, dtype=int), np.asarray(pairs_j, dtype=int)

    return np.asarray(pairs_i, dtype=int), np.asarray(pairs_j, dtype=int)


def lyapunov_exponent_series(series: np.ndarray, config: SeriesLyapunovConfig = SeriesLyapunovConfig()) -> float:
    """
    Estimate the largest Lyapunov exponent from a scalar time series.

    Steps:
      1) pick pairs (i,j) with |x[i]-x[j]| < eps (efficient 1D search)
      2) track separations for k=0..l-1: d_k = |x[i+k]-x[j+k]|
      3) fit slope of log(d_k) vs k via least squares
      4) average slopes over pairs

    Returns NaN if no valid pairs exist.
    """
    x = np.asarray(series, dtype=float).ravel()
    if x.size < config.l + 2:
        return float("nan")

    rng = np.random.default_rng(config.seed)
    ii, jj = _pair_candidates_1d(
        x,
        l=config.l,
        eps=config.eps,
        max_pairs=config.max_pairs,
        min_separation=config.min_separation,
        rng=rng,
    )
    if ii.size == 0:
        return float("nan")

    t = np.arange(config.l, dtype=float)
    t0 = t - t.mean()
    denom = float(np.dot(t0, t0))  # constant

    slopes = []
    for i, j in zip(ii, jj):
        d = np.abs(x[i : i + config.l] - x[j : j + config.l])
        d = np.where(d <= 0.0, config.tiny, d)
        y = np.log(d)
        if not np.all(np.isfinite(y)):
            continue
        y0 = y - y.mean()
        slope = float(np.dot(t0, y0) / denom)
        if np.isfinite(slope):
            slopes.append(slope)

    if not slopes:
        return float("nan")
    return float(np.mean(slopes))
