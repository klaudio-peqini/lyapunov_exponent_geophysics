from __future__ import annotations
from pathlib import Path
import numpy as np
from .estimators import KantzConfig, LocalNeighborConfig, RosensteinConfig, kantz_estimator, local_neighbor_estimator, rosenstein_estimator
from .io import write_local_estimates, write_summary
from .plotting import plot_divergence_curves, plot_method_comparison, plot_pdf_local_estimates
from .preprocessing import normalize_series

def run_methods(x: np.ndarray, methods: list[str], emb_dim: int, tau: int, horizon: int, fit_start: int, fit_end: int, theiler: int, k_neighbors: int, max_pairs: int, seed: int, n_bootstrap: int, ci: float, center: str, normalize: str = 'zscore'):
    y=normalize_series(x, normalize); results=[]
    if 'local' in methods:
        results.append(local_neighbor_estimator(y, LocalNeighborConfig(emb_dim=emb_dim,tau=tau,horizon=horizon,fit_start=fit_start,fit_end=fit_end,theiler=theiler,k_neighbors=k_neighbors,max_pairs=max_pairs,seed=seed,n_bootstrap=n_bootstrap,ci=ci,center=center)))
    if 'rosenstein' in methods:
        results.append(rosenstein_estimator(y, RosensteinConfig(emb_dim=emb_dim,tau=tau,horizon=horizon,fit_start=fit_start,fit_end=fit_end,theiler=theiler,max_reference_points=max_pairs,seed=seed,n_bootstrap=n_bootstrap,ci=ci,center=center)))
    if 'kantz' in methods:
        results.append(kantz_estimator(y, KantzConfig(emb_dim=emb_dim,tau=tau,horizon=horizon,fit_start=fit_start,fit_end=fit_end,theiler=theiler,k_neighbors=k_neighbors,max_reference_points=max_pairs,seed=seed,n_bootstrap=n_bootstrap,ci=ci,center=center)))
    return results

def save_analysis_outputs(results, outdir: str | Path, hist_rule: str = 'fd') -> None:
    outdir=Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    write_summary(results, outdir/'summary.json'); write_local_estimates(results, outdir/'local_estimates.csv')
    plot_pdf_local_estimates(results, outdir/'pdf_local_estimates.pdf', hist_rule=hist_rule)
    plot_divergence_curves(results, outdir/'divergence_curves.pdf'); plot_method_comparison(results, outdir/'method_comparison.pdf')
