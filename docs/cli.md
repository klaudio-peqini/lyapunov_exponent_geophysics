# CLI guide (`lyapgeo`)

After `pip install -e .`, the `lyapgeo` command should be available.

```bash
lyapgeo --help
```

## 1) Bifurcation diagrams

### Logistic map

```bash
lyapgeo bifurcation logistic   --r-min 2.8 --r-max 4.0 --dr 0.01   --x0 0.2 --steps 2000 --last 300   --out Lyapunov_logistic_map.pdf
```

### Gaussian map

```bash
lyapgeo bifurcation gaussian   --alpha 1.0 --beta-min -1.0 --beta-max 1.0 --db 0.01   --x0 0.2 --steps 2000 --last 300   --out Lyapunov_gaussian_map.pdf
```

### Logistic-exponential map

```bash
lyapgeo bifurcation logexp   --r-min 3.0 --r-max 4.0 --dr 0.01   --x0 0.2 --steps 2000 --last 300   --out Lyapunov_logistic_exponential_map.pdf
```

All bifurcation commands print elapsed time.

## 2) Lyapunov exponent from a time-series CSV

### Example with a named column

```bash
lyapgeo series --csv my_timeseries.csv --column-name Bz --eps 0.01 --l 10
```

### Example with a 0-based column index

```bash
lyapgeo series --csv my_timeseries.csv --column 0 --eps 0.01 --l 10
```

## 3) Lorenz Lyapunov spectrum

```bash
lyapgeo lorenz-lyap --sigma 10 --r 28 --b 2.6666667 --iters 2000 --dt 1.0
```
