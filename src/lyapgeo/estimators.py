from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.spatial import cKDTree
from .preprocessing import delay_embedding
from .results import LyapunovResult
from .statistics import SummaryConfig, summarize_local_estimates

@dataclass(frozen=True)
class LocalNeighborConfig:
    emb_dim: int = 1; tau: int = 1; eps: float | None = None; k_neighbors: int = 8; horizon: int = 5; fit_start: int = 0; fit_end: int = 5; theiler: int = 10; max_pairs: int = 5000; seed: int = 0; tiny: float = 1e-12; n_bootstrap: int = 2000; ci: float = 0.95; center: str = "median"
@dataclass(frozen=True)
class RosensteinConfig:
    emb_dim: int = 3; tau: int = 1; horizon: int = 20; fit_start: int = 1; fit_end: int = 8; theiler: int = 20; max_reference_points: int = 5000; seed: int = 0; tiny: float = 1e-12; n_bootstrap: int = 2000; ci: float = 0.95; center: str = "median"
@dataclass(frozen=True)
class KantzConfig:
    emb_dim: int = 3; tau: int = 1; horizon: int = 20; fit_start: int = 1; fit_end: int = 8; theiler: int = 20; k_neighbors: int = 20; max_reference_points: int = 5000; seed: int = 0; tiny: float = 1e-12; n_bootstrap: int = 2000; ci: float = 0.95; center: str = "median"

def _linear_slopes(y: np.ndarray, fit_start: int, fit_end: int) -> np.ndarray:
    z = y[:, fit_start:fit_end]; k = np.arange(fit_start, fit_end, dtype=float)
    k0 = k - np.mean(k); denom = np.dot(k0, k0)
    z0 = z - np.nanmean(z, axis=1, keepdims=True)
    return np.nansum(z0 * k0, axis=1) / denom

def _query_valid_neighbors(emb: np.ndarray, ref_indices: np.ndarray, k_query: int, theiler: int) -> list[np.ndarray]:
    tree = cKDTree(emb)
    _, idx = tree.query(emb[ref_indices], k=min(k_query, emb.shape[0]))
    if idx.ndim == 1: idx = idx[:, None]
    out=[]
    for ref, row in zip(ref_indices, idx):
        out.append(row[(row != ref) & (np.abs(row - ref) > theiler)])
    return out

def _make_result(method, local, cfg, log_mean):
    summary = summarize_local_estimates(local, SummaryConfig(n_bootstrap=cfg.n_bootstrap, ci=cfg.ci, seed=cfg.seed, center=cfg.center))
    return LyapunovResult(method=method, estimate=float(summary['estimate']), ci_low=float(summary['ci_low']), ci_high=float(summary['ci_high']), median=float(summary['median']), mean=float(summary['mean']), std=float(summary['std']), n_local=int(summary['n_local']), fit_start=cfg.fit_start, fit_end=cfg.fit_end, emb_dim=cfg.emb_dim, tau=cfg.tau, horizon=cfg.horizon, local_estimates=local, divergence_k=np.arange(cfg.horizon), divergence_log_mean=log_mean)

def local_neighbor_estimator(x: np.ndarray, cfg: LocalNeighborConfig = LocalNeighborConfig()) -> LyapunovResult:
    emb = delay_embedding(np.asarray(x, dtype=float), cfg.emb_dim, cfg.tau)
    n = emb.shape[0] - cfg.horizon
    if n <= 2: raise ValueError("Time series too short for requested horizon/embedding.")
    rng = np.random.default_rng(cfg.seed); refs = np.arange(n)
    if refs.size > cfg.max_pairs: refs = np.sort(rng.choice(refs, size=cfg.max_pairs, replace=False))
    neigh = _query_valid_neighbors(emb[:n], refs, max(cfg.k_neighbors + 1, 16), cfg.theiler)
    local_logs=[]; used=0
    for i, js in zip(refs, neigh):
        for j in js[:cfg.k_neighbors]:
            d = np.array([np.linalg.norm(emb[i+k] - emb[j+k]) for k in range(cfg.horizon)])
            d = np.maximum(d, cfg.tiny)
            if cfg.eps is not None and d[0] > cfg.eps: continue
            local_logs.append(np.log(d)); used += 1
            if used >= cfg.max_pairs: break
        if used >= cfg.max_pairs: break
    if not local_logs: local, log_mean = np.array([], dtype=float), None
    else:
        logs=np.vstack(local_logs); local=_linear_slopes(logs, cfg.fit_start, cfg.fit_end); log_mean=np.nanmean(logs, axis=0)
    return _make_result('local_neighbor', local, cfg, log_mean)

def rosenstein_estimator(x: np.ndarray, cfg: RosensteinConfig = RosensteinConfig()) -> LyapunovResult:
    emb = delay_embedding(np.asarray(x, dtype=float), cfg.emb_dim, cfg.tau)
    n = emb.shape[0] - cfg.horizon
    if n <= 2: raise ValueError("Time series too short for requested horizon/embedding.")
    rng=np.random.default_rng(cfg.seed); refs=np.arange(n)
    if refs.size > cfg.max_reference_points: refs=np.sort(rng.choice(refs, size=cfg.max_reference_points, replace=False))
    neigh=_query_valid_neighbors(emb[:n], refs, 64, cfg.theiler)
    logs=[]
    for i, js in zip(refs, neigh):
        if js.size == 0: continue
        j=int(js[0]); d=[np.linalg.norm(emb[i+k] - emb[j+k]) for k in range(cfg.horizon)]
        logs.append(np.log(np.maximum(d, cfg.tiny)))
    if not logs: local, log_mean=np.array([], dtype=float), None
    else:
        logs=np.vstack(logs); local=_linear_slopes(logs, cfg.fit_start, cfg.fit_end); log_mean=np.nanmean(logs, axis=0)
    return _make_result('rosenstein', local, cfg, log_mean)

def kantz_estimator(x: np.ndarray, cfg: KantzConfig = KantzConfig()) -> LyapunovResult:
    emb = delay_embedding(np.asarray(x, dtype=float), cfg.emb_dim, cfg.tau)
    n = emb.shape[0] - cfg.horizon
    if n <= 2: raise ValueError("Time series too short for requested horizon/embedding.")
    rng=np.random.default_rng(cfg.seed); refs=np.arange(n)
    if refs.size > cfg.max_reference_points: refs=np.sort(rng.choice(refs, size=cfg.max_reference_points, replace=False))
    neigh=_query_valid_neighbors(emb[:n], refs, max(64, cfg.k_neighbors + 8), cfg.theiler)
    logs=[]
    for i, js in zip(refs, neigh):
        js=js[:cfg.k_neighbors]
        if js.size == 0: continue
        vals=[]
        for k in range(cfg.horizon):
            d=np.linalg.norm(emb[i+k] - emb[js+k], axis=1)
            vals.append(np.mean(np.maximum(d, cfg.tiny)))
        logs.append(np.log(np.asarray(vals)))
    if not logs: local, log_mean=np.array([], dtype=float), None
    else:
        logs=np.vstack(logs); local=_linear_slopes(logs, cfg.fit_start, cfg.fit_end); log_mean=np.nanmean(logs, axis=0)
    return _make_result('kantz', local, cfg, log_mean)
