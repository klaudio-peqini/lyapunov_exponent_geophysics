# lyapunov-geophys-timeseries

A small, research-friendly repository to **estimate Lyapunov exponents from geophysical time series**
(geomagnetic, seismic, hydrologic, atmospheric) and to reproduce benchmark *bifurcation + Lyapunov* plots
for classic maps.

This repo is adapted from your original scripts:
- `bifurcation_diagram.py` fileciteturn0file0
- `bifurcation_Lorenz_system.py` fileciteturn0file1
- `radon_processing.py` fileciteturn0file2
- `signal_processing_tests.py` fileciteturn0file3

---

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -e .
```

---

## CLI (tracklet-style, via argparse)

### 1) Bifurcation + Lyapunov plots (PDF/PNG)

Logistic map (produces a plot similar to your earlier PDFs):

```bash
lyapgeo bifurcation logistic \
  --r-min 2.8 --r-max 4.0 --dr 0.01 \
  --x0 0.2 --steps 2000 --last 300 \
  --eps 0.01 --l 5 --max-pairs 1000 \
  --out Lyapunov_logistic_map.pdf
```

Gaussian map:

```bash
lyapgeo bifurcation gaussian \
  --alpha 1.0 --beta-min -1.0 --beta-max 1.0 --db 0.01 \
  --x0 0.2 --steps 2000 --last 300 \
  --out Lyapunov_gaussian_map.pdf
```

Logistic-exponential map:

```bash
lyapgeo bifurcation logexp \
  --r-min 3.0 --r-max 4.0 --dr 0.01 \
  --x0 0.2 --steps 2000 --last 300 \
  --out Lyapunov_logistic_exponential_map.pdf
```

Each command prints **elapsed time**.

### 2) Lyapunov exponent from a CSV time series

```bash
lyapgeo series --csv my_timeseries.csv --column-name Bz --eps 0.01 --l 10
```

(Or `--column 0` for a 0-based index.)

### 3) Lorenz Lyapunov spectrum (QR method)

```bash
lyapgeo lorenz-lyap --sigma 10 --r 28 --b 2.6666667 --iters 2000 --dt 1.0
```

---

## Your performance concern (fixed)

Your original `lyapunov_exponent()` in `radon_processing.py` uses nested loops over all pairs `(i, j)`
and becomes slow for long signals. fileciteturn0file2

The new implementation in `src/lyapunov_geo/lyapunov.py` is much faster because it:
- sorts values once (O(N log N))
- finds neighbors with a sliding window in 1D (instead of scanning all pairs)
- limits work with `--max-pairs`
- uses an O(l) closed-form linear regression for the slope

Tune performance/quality via: `--eps`, `--l`, `--max-pairs`, `--min-separation`.

---

## Repo layout

```text
src/lyapunov_geo/
  cli.py         # argparse entrypoint (lyapgeo)
  lyapunov.py    # fast series LE estimator
  maps.py        # logistic / gaussian / logexp
  bifurcation.py # bifurcation workflows + plotting
  lorenz.py      # Lorenz Lyapunov spectrum (QR)
  io.py          # simple CSV loader

examples/        # your original scripts (kept for reference)
tests/           # pytest smoke tests
```
