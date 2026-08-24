# AGENTS.md

## Project

Python 3.10+ repo that uses **marvincode serve** as the LLM backend to run a small multi-agent crew (`Planner`, `Coder`, `Reviewer`) that drafts a feature from a description.

## Quick start

First, start the marvincode server:

```bash
marvincode serve --port 4097
```

Then run the crew:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

export MARVINCODE_SERVER_URL=http://127.0.0.1:4097
python -m feature_crew --description "Add a function that sums a list of integers"
```

Or pass the server URL directly:

```bash
python -m feature_crew --description "..." --server http://127.0.0.1:4097
```

## Verify loop

Run these in order after any change. All commands assume the virtual environment is activated.

```bash
source .venv/bin/activate
ruff check src tests
ruff format --check src tests
mypy src
pytest
```

Apply fixes with `ruff format src tests` and `ruff check --fix src tests`.

## Harness details

- Package layout: `src/feature_crew/`.
- Entry point: `python -m feature_crew` (also `python -m feature_crew.cli`).
- LLM backend: marvincode serve (the marvincode CLI server).
- Server URL set via `MARVINCODE_SERVER_URL` env var or `--server` flag.
- Authentication: optional, set `MARVINCODE_API_KEY` if the server requires it.
- Tests mock the LLM calls so `pytest` does not need a live marvincode server.

## Tool config

- `pyproject.toml` defines dependencies, `[tool.pytest.ini_options]`, `[tool.ruff]`, and `[tool.mypy]`.
- `mypy` ignores missing imports (`ignore_missing_imports = true`) because LangChain typing can be noisy.