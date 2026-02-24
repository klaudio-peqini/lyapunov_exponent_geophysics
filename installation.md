# Installation

## pip / venv

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -e .
```

## conda/mamba (optional)

```bash
mamba env create -f environment.yml
mamba activate lyapunov-geo
pip install -e .
```

## Quick sanity check

```bash
python -c "import lyapunov_geo; print('ok')"
pytest
```

## Optional dev tooling

```bash
pre-commit install
ruff check .
ruff format .
```
