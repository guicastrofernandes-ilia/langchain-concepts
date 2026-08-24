# Feature: LangChain Multi-Agent Feature Builder

## Goal

Provide a local Python harness that uses **marvincode serve** as the LLM backend to run a small multi-agent crew. Given a natural-language feature request, the crew plans, drafts code, and reviews the result -- producing a concrete implementation plan and generated code artifacts.

## Acceptance Criteria

- AC-1: Repository contains a working Python project with a virtual environment and dependency manifest.
- AC-2: `MARVINCODE_SERVER_URL` must be set (env or `--server` flag); the app fails fast with a clear message if missing.
- AC-3: The system exposes a CLI entry point that accepts a feature description and prints the generated plan + code.
- AC-4: At least three specialized agents collaborate: Planner, Coder, and Reviewer.
- AC-5: Planner emits a structured task list; Coder emits code files; Reviewer emits a pass/fail assessment with concrete feedback.
- AC-6: Unit tests cover the agent orchestration and individual agent outputs without requiring live LLM calls (mocked).
- AC-7: `AGENTS.md` documents the exact local verify-loop commands for this Python project.

## Out of scope

- Actually writing files to disk outside a designated output directory.
- Integration with git, CI, or automatic PR creation.
- Long-term memory or cross-session state.
- Real-time streaming output.

## Decisions

- Use `httpx` for HTTP calls to the marvincode serve API (session-based, not OpenAI-compatible).
- Use `pytest` for tests and `ruff` for lint/format.
- Use `pyproject.toml` for project metadata and tool config.