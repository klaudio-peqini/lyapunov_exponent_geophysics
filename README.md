# lyapunov-geophys-timeseries

A small, research-friendly repository template to **estimate Lyapunov exponents from geophysical time series**
(e.g., geomagnetic, seismic, hydrologic, atmospheric).

> This repo is intentionally **scaffold-only**: no calculation scripts are included yet.
> You can drop in your existing code (which you'll share next) under `src/` or `lyapunov/` and it will
> integrate cleanly with packaging, testing, linting, and CI.

---

## What’s included

- **Modern Python packaging** via `pyproject.toml` (setuptools backend)
- **Reproducible environments**
  - `requirements.txt` (pip)
  - optional `environment.yml` (conda/mamba)
- **Testing + CI**: `pytest` + GitHub Actions workflow
- **Code quality**: `ruff` (lint + format) and optional `pre-commit`
- **Documentation-ready structure** (placeholder `docs/`)
- Community/metadata files: `LICENSE`, `CITATION.cff`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`

---

## Repository structure

```text
lyapunov-geophys-timeseries/
├─ src/
│  └─ lyapunov_geo/
│     └─ __init__.py
├─ tests/
│  └─ test_smoke.py
├─ data/
│  ├─ raw/
│  └─ processed/
├─ notebooks/
├─ docs/
├─ .github/workflows/ci.yml
├─ .gitignore
├─ .pre-commit-config.yaml
├─ pyproject.toml
├─ requirements.txt
├─ environment.yml
├─ LICENSE
├─ CITATION.cff
├─ CONTRIBUTING.md
├─ CODE_OF_CONDUCT.md
└─ CHANGELOG.md
```

Notes:
- Put raw time series in `data/raw/` (kept out of git by default; see `.gitignore`).
- Store derived data in `data/processed/`.
- Add your implementation under `src/lyapunov_geo/` (recommended) or adjust to your preferred layout.

---

## Quick start (pip)

```bash
python -m venv .venv
source .venv/bin/activate  # (Windows) .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
pip install -e .
```

Run tests:

```bash
pytest
```

Lint/format (ruff):

```bash
ruff check .
ruff format .
```

---

## Quick start (conda/mamba)

```bash
mamba env create -f environment.yml
mamba activate lyapunov-geo
pip install -e .
pytest
```

---

## Where your code will go

When you share your earlier codes, we’ll adapt them into a clean API, typically:

- `src/lyapunov_geo/embedding.py` — delay/embedding helpers (if needed)
- `src/lyapunov_geo/lyapunov.py` — main estimator(s)
- `src/lyapunov_geo/utils.py` — shared utilities
- `src/lyapunov_geo/io.py` — loading/standardizing time series (CSV, miniseed, etc.)

…but we won’t add any calculation scripts until you provide your code.

---

## Citation

If you use this repository in academic work, please cite it using the metadata in `CITATION.cff`.

---

## License

MIT License (see `LICENSE`).

---

## Maintainer notes

- Default Python version target: **3.10+**
- CI runs on Ubuntu with Python 3.10–3.12.
- Data folders contain `.gitkeep` files so the directories exist in the repo.

