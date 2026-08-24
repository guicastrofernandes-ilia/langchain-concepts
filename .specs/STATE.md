# Project State

## Active Decisions

- AD-001: Project language is Python 3.10+; use modern `pyproject.toml` packaging.
- AD-002: LLM backend is **marvincode serve** — the marvincode CLI server.
- AD-003: Multi-agent system uses three fixed-role agents: Planner, Coder, Reviewer.
- AD-004: Secrets are read from environment only; no committed `.env` files.
- AD-005: Server URL set via `MARVINCODE_SERVER_URL` env var or `--server` flag.
- AD-006: `record-catalog` feature: FastAPI + SQLAlchemy async + PostgreSQL + Docker Compose.
- AD-007: Frontend: React + Vite with proxy to backend API.

## Handoff

- Feature complete: `record-store-catalog` (API + React frontend).
- Commit range: `9144e03..91a4900` (14 commits).
- All verify loops pass: Python (ruff, mypy, pytest 37/37) + React (vite build).
- Validation: PASS — all 20 ACs verified, 3/3 sensor mutations killed.
- Docker Compose with PostgreSQL ready — run `docker compose up -d` to start the DB.
- Frontend at `frontend/` — run `npm run dev` for dev server at `:5173`.