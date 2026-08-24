# Design: LangChain Multi-Agent Feature Builder

## Components

```
feature_crew/
├── __init__.py
├── models.py      # Pydantic schemas: Plan, CodeArtifact, Review
├── agents.py      # Planner, Coder, Reviewer agent builders
├── crew.py        # Orchestrates agent execution and aggregates output
└── cli.py         # argparse entry point
```

## Data flow

1. CLI receives `--description` and optional `--model`.
2. `Crew.run(description)` invokes agents in order:
   - **Planner** → emits `Plan` (feature summary + list of tasks).
   - **Coder** → receives `Plan`, emits `CodeArtifact` (filename + code body).
   - **Reviewer** → receives `Plan` + `CodeArtifact`, emits `Review` (pass/fail + feedback).
3. CLI prints the plan, generated code, and review.

## Tooling

- Dependency management: `pyproject.toml` + `requirements-dev.txt`.
- Virtual env: `.venv/` in repo root.
- Lint/format: `ruff check .` and `ruff format .`.
- Tests: `pytest`.
- Type check: `mypy` (optional, added if it passes cleanly).

## Secrets

Only `OPENAI_API_KEY`; loaded from environment. No `.env` file committed.
