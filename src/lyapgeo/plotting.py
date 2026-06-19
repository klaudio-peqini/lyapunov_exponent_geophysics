from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from .results import LyapunovResult
from .statistics import optimal_histogram

def plot_pdf_local_estimates(results: list[LyapunovResult], outpath: str | Path, hist_rule: str = 'fd') -> None:
    outpath=Path(outpath); outpath.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8,5))
    for r in results:
        x=r.local_estimates[np.isfinite(r.local_estimates)]
        if x.size == 0: continue
        centers,density,_=optimal_histogram(x, rule=hist_rule)
        plt.plot(centers,density,marker='o',lw=1.5,label=f'{r.method} (n={x.size})')
        plt.axvline(r.estimate,linestyle='--',lw=1)
    plt.xlabel('Local Lyapunov estimate'); plt.ylabel('Estimated PDF'); plt.grid(True,alpha=0.3); plt.legend(); plt.tight_layout(); plt.savefig(outpath,dpi=200); plt.close()

def plot_divergence_curves(results: list[LyapunovResult], outpath: str | Path) -> None:
    outpath=Path(outpath); outpath.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8,5))
    for r in results:
        if r.divergence_k is None or r.divergence_log_mean is None: continue
        plt.plot(r.divergence_k,r.divergence_log_mean,marker='o',lw=1.5,label=r.method)
        plt.axvspan(r.fit_start, r.fit_end-1, alpha=0.08)
    plt.xlabel('Prediction step k'); plt.ylabel('Mean log divergence'); plt.grid(True,alpha=0.3); plt.legend(); plt.tight_layout(); plt.savefig(outpath,dpi=200); plt.close()

def plot_method_comparison(results: list[LyapunovResult], outpath: str | Path) -> None:
    outpath=Path(outpath); outpath.parent.mkdir(parents=True, exist_ok=True)
    names=[r.method for r in results]; y=np.array([r.estimate for r in results]); lo=np.array([r.estimate-r.ci_low for r in results]); hi=np.array([r.ci_high-r.estimate for r in results])
    plt.figure(figsize=(8,5)); plt.errorbar(np.arange(len(names)),y,yerr=[lo,hi],fmt='o',capsize=4); plt.xticks(np.arange(len(names)),names,rotation=20); plt.axhline(0.0,lw=1); plt.ylabel('Lyapunov exponent estimate'); plt.grid(True,alpha=0.3); plt.tight_layout(); plt.savefig(outpath,dpi=200); plt.close()
