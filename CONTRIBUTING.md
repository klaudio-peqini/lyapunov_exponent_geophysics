# Contributing

Thanks for considering contributing!

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -e .
pre-commit install
```

## Quality checks

```bash
ruff check .
ruff format .
pytest
```

## Pull requests

- Keep PRs focused and small.
- Add tests for new behavior.
- Prefer clear, scientific docstrings and references.
