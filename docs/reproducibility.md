# Reproducibility conventions

## Data folders
- `data/raw/` is ignored by git (put large CSVs here).
- `data/processed/` is also ignored by git.

The `.gitkeep` files ensure the folders exist in the repo.

## Outputs
Prefer writing figures to `results/` or an analysis-specific directory you create.

## Randomness
The time-series estimator can subsample neighbors when many candidates exist.
Use `--seed` to make results reproducible.
