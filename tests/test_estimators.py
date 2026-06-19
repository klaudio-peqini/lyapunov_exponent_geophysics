import numpy as np
from lyapgeo.benchmarks import logistic_series
from lyapgeo.estimators import LocalNeighborConfig, local_neighbor_estimator

def test_local_neighbor_runs_on_logistic():
    x = logistic_series(3.9, 0.2, n=1000, discard=100)
    r = local_neighbor_estimator(x, LocalNeighborConfig(emb_dim=2, tau=1, horizon=5, fit_start=0, fit_end=5, max_pairs=500, n_bootstrap=100, seed=0))
    assert r.n_local > 10
    assert np.isfinite(r.estimate)
