# Validation Report: langchain-feature-agents

## Verdict: PASS

## Acceptance Criteria Evidence

| AC | Requirement | Evidence |
|----|-------------|----------|
| AC-1 | Working Python project with virtual environment and dependency manifest | `pyproject.toml` exists; `pip install -e ".[dev]"` succeeded; `.venv/` created. |
| AC-2 | `MARVINCODE_SERVER_URL` required; clear failure if missing | CLI prints explicit error if missing; tests verify. |
| AC-3 | CLI entry point accepts `--description` and prints plan + code | `python -m feature_crew` works; `cli.py` parses args and prints PLAN, CODE, REVIEW sections. |
| AC-4 | At least three agents: Planner, Coder, Reviewer | `agents.py` defines `create_planner`, `create_coder`, `create_reviewer`; `Crew.run` orchestrates all three. |
| AC-5 | Planner emits Plan, Coder emits CodeArtifact, Reviewer emits Review | Pydantic models in `models.py`; each agent uses structured JSON output via `invoke_structured`. |
| AC-6 | Unit tests cover orchestration and agent outputs without live LLM calls | `tests/test_crew.py` and `tests/test_cli.py` mock agents / `Crew`; `pytest` passes 6/6. |
| AC-7 | `AGENTS.md` documents the exact verify-loop commands | `AGENTS.md` updated with marvincode serve harness details. |

## LLM backend

- **marvincode serve** — the marvincode CLI server.
- Custom provider (`marvincode_provider.py`) calls the session-based API (session, prompt_async, wait, messages).
- Server URL: `MARVINCODE_SERVER_URL` env var or `--server` flag.

## Commands run

```bash
source .venv/bin/activate
ruff check src tests
ruff format --check src tests
mypy src
pytest
```

All passed.

## Manual checks

- `python -m feature_crew --description "..."` without `MARVINCODE_SERVER_URL` -> fails fast with clear error.
- `python -m feature_crew ... --server http://127.0.0.1:4097` -> accepts server URL via flag.

## Diff range

- Added: `src/feature_crew/marvincode_provider.py`
- Modified: `src/feature_crew/agents.py`, `src/feature_crew/crew.py`, `src/feature_crew/cli.py`, `AGENTS.md`, `README.md`, `pyproject.toml`
- Updated tests: `tests/test_crew.py`, `tests/test_cli.py`

## Sensor result

No discrimination sensor run -- feature is scaffolding/tooling with mocked LLM boundaries. All acceptance criteria asserted by tests are spec-anchored.