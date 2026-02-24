# Lyapunov estimator notes

This repo includes two Lyapunov exponent paths:

## A) Discrete maps (derivative formula)

For 1D maps `x_{n+1} = f(x_n)`, the largest exponent can be computed via:

\[ \lambda = \langle \log |f'(x_n)| \rangle \]

This is used for the benchmark curves in the bifurcation plots.

## B) Time series estimator (neighbor divergence)

For an observed scalar time series `x[n]`, we estimate the exponent by tracking divergence
between initially close points:

1. Find pairs `(i, j)` such that `|x[i] - x[j]| < eps` (and `|i-j| > min_separation`).
2. Track the distances for `k = 0..l-1`: `d_k = |x[i+k]-x[j+k]|`.
3. Fit a slope of `log(d_k)` vs `k` for each pair.
4. Average slopes over pairs.

### Why it is faster than the original script

Your original prototype scanned all `(i, j)` pairs (O(N²)). The implementation here:

- sorts values once (O(N log N))
- finds neighbors using a sliding window in 1D
- caps the number of tracked pairs (`max_pairs`)
- computes slopes with a closed-form least squares slope

### Parameters to tune

- `eps`: neighborhood size (too small → no pairs; too large → biased)
- `l`: horizon length (bigger can stabilize slope but costs more)
- `max_pairs`: main speed knob
- `min_separation`: avoids trivial temporal neighbors / autocorrelation bias

## Recommended validation workflow

For a new dataset:
1. Sweep `eps` and `l` over a small grid on a short subset of data.
2. Check stability of the estimated exponent and runtime.
3. Compare with an established method (e.g. Rosenstein/Wolf) if needed.
