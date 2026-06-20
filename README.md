# lyapunov-exponent-geophysics                         

Professional Python toolkit for estimating Lyapunov exponents from geophysical time series.

The repository provides:

- a fast **local-neighbor estimator** inspired by the original simple approach;
- a **Rosenstein-style largest Lyapunov exponent** estimator;
- a **Kantz-style divergence estimator**;
- local slope distributions with **optimized histogram/PDF estimation**;
- final estimates with **bootstrap 95% confidence intervals**;
- command-line workflows for reproducible analysis;
- benchmark tools for logistic-map validation.

The main idea is not to trust one number from one algorithm. Instead, the package compares several estimators and reports both global and local information.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -e .
pytest
```

## Analyze a time series

```bash
lyapgeo series \
  --input data/raw/radon.csv \
  --column-name Radon \
  --method all \
  --emb-dim 3 \
  --tau 2 \
  --horizon 5 \
  --fit-start 0 \
  --fit-end 5 \
  --theiler 20 \
  --n-bootstrap 2000 \
  --outdir results/radon
```

Outputs:

```text
results/radon/
├─ summary.json
├─ local_estimates.csv
├─ pdf_local_estimates.pdf
├─ divergence_curves.pdf
└─ method_comparison.pdf
```

## Benchmark with the logistic map

```bash
lyapgeo benchmark-logistic --r 3.9 --n 6000 --discard 1000 --outdir results/logistic_r39
```

## Implemented estimators

1. **Local-neighbor estimator**: short local divergence windows, useful for PDFs of local Lyapunov estimates.
2. **Rosenstein estimator**: delay embedding, nearest neighbors, Theiler window, mean log divergence, slope fit.
3. **Kantz estimator**: neighborhood-averaged divergence using several neighbors per reference state.

For noisy and short geophysical series, a positive exponent should be interpreted cautiously and compared against surrogates and parameter sweeps.

## Radon Eye / FTLAB TXT files without column names

Radon Eye TXT exports are not normal CSV files. They contain a metadata header and data rows like:

```text
1)  2024-02-08 17:49:17   21   20.5°C   60%
```

Use the dedicated parser:

```bash
lyapgeo series \
  --input "data/raw/PE22111010064_LogData (14) Durres.txt" \
  --input-format radon-eye \
  --field radon \
  --method all \
  --emb-dim 3 \
  --tau 2 \
  --horizon 5 \
  --fit-start 0 \
  --fit-end 5 \
  --theiler 20 \
  --max-pairs 5000 \
  --outdir results/radon_durres
```

Available fields are `radon`, `temperature`, and `humidity`.

## Excel input, for example PADM2M.xlsx

For Excel files with named columns, such as `Age (kyr)` and `RPI`, use:

```bash
lyapgeo series \
  --input PADM2M.xlsx \
  --input-format excel \
  --sheet Sheet1 \
  --column-name RPI \
  --method all \
  --emb-dim 3 \
  --tau 2 \
  --horizon 5 \
  --fit-start 0 \
  --fit-end 5 \
  --theiler 20 \
  --max-pairs 5000 \
  --outdir results/PADM2M_RPI
```

## Direct execution without `lyapgeo`

If your terminal keeps finding an old `lyapgeo` command, run directly:

```bash
python scripts/run_lyapgeo.py series \
  --input PADM2M.xlsx \
  --input-format excel \
  --sheet Sheet1 \
  --column-name RPI \
  --method all \
  --outdir results/geomagnetic
```

Equivalent module form:

```bash
python -m lyapgeo.cli series \
  --input PADM2M.xlsx \
  --input-format excel \
  --sheet Sheet1 \
  --column-name RPI \
  --method all \
  --outdir results/geomagnetic
```
