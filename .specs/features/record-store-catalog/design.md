# Record Store Catalog — Design

**Spec**: `.specs/features/record-store-catalog/spec.md`
**Status**: Draft

---

## Architecture Overview

Standard layered REST API: FastAPI routes → Pydantic validation → SQLAlchemy ORM → PostgreSQL.

```
┌──────────────┐     ┌────────────────┐     ┌──────────────┐     ┌────────────┐
│  HTTP Client │ ──▶ │  FastAPI App   │ ──▶ │  SQLAlchemy  │ ──▶ │ PostgreSQL │
│  (curl/http) │ ◀── │  (router.py)   │ ◀── │  (models.py) │ ◀── │  (Docker)  │
└──────────────┘     └────────────────┘     └──────────────┘     └────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Pydantic    │
                     │  Schemas     │
                     │ (schemas.py) │
                     └──────────────┘
```

---

## Code Reuse Analysis

### Existing Components to Leverage

| Component | Location | How to Use |
| --------- | -------- | ---------- |
| `pyproject.toml` | root | Add FastAPI, SQLAlchemy, asyncpg, alembic deps |
| `httpx` | existing dep | Used in tests to call the API |

### Integration Points

| System | Integration Method |
| ------ | ------------------ |
| Existing project | New independent package `src/record_catalog/` — no coupling to `feature_crew` |

---

## Components

### FastAPI app (`src/record_catalog/main.py`)

- **Purpose**: Application entry point; creates the FastAPI instance, includes the router, and configures CORS.
- **Location**: `src/record_catalog/main.py`
- **Interfaces**:
  - `create_app() -> FastAPI` — factory function for testability
- **Dependencies**: `fastapi`, `router`, `database`

### Database setup (`src/record_catalog/database.py`)

- **Purpose**: SQLAlchemy engine + session factory + Base + lifecycle hooks.
- **Location**: `src/record_catalog/database.py`
- **Interfaces**:
  - `get_db() -> AsyncIterator[AsyncSession]` — FastAPI dependency that yields a session
  - `engine: AsyncEngine` — singleton engine
- **Dependencies**: `sqlalchemy[asyncio]`, `asyncpg`

### SQLAlchemy models (`src/record_catalog/models.py`)

- **Purpose**: ORM model for the `Record` table.
- **Location**: `src/record_catalog/models.py`
- **Interfaces**:
  - `Record` — SQLAlchemy model with fields per spec
- **Dependencies**: `database.Base`

### Pydantic schemas (`src/record_catalog/schemas.py`)

- **Purpose**: Request/response validation with Pydantic v2.
- **Location**: `src/record_catalog/schemas.py`
- **Interfaces**:
  - `RecordCreate` — input schema for POST/PUT
  - `RecordResponse` — output schema (includes `id`, `created_at`, `updated_at`)
  - `RecordListResponse` — paginated wrapper (`items`, `total`, `limit`, `offset`)
  - `ConditionEnum` — `Mint | Excellent | VeryGood | Good | Fair | Poor`
  - `TrackSchema` — nested track schema
- **Dependencies**: `pydantic`

### API router (`src/record_catalog/router.py`)

- **Purpose**: All route handlers.
- **Location**: `src/record_catalog/router.py`
- **Interfaces**:
  - `GET /records` — list with pagination + filters
  - `GET /records/{id}` — get one
  - `POST /records` — create
  - `PUT /records/{id}` — update
  - `DELETE /records/{id}` — delete
- **Dependencies**: `schemas`, `models`, `database.get_db`

---

## Data Models

### Record

```
Record {
  id: int (PK, auto-increment)
  artist: str (required, indexed)
  album: str (required, indexed)
  year: int | null
  genre: str | null (indexed)
  label: str | null
  condition: ConditionEnum | null
  tracks: list[Track] (JSON column)
  created_at: datetime (auto)
  updated_at: datetime (auto)

  UNIQUE(artist, album)
}
```

### Track (nested, stored as JSON)

```
Track {
  title: str (required)
  duration: str | null (ISO 8601 duration, e.g. "PT4M32S")
}
```

### ConditionEnum

```
Mint | Excellent | VeryGood | Good | Fair | Poor
```

---

## Error Handling Strategy

| Error Scenario | Handling | User Impact |
| -------------- | -------- | ----------- |
| Missing required field | FastAPI/Pydantic validation | HTTP 422 with field-level errors |
| Duplicate artist+album | Catch `IntegrityError`, return 409 | HTTP 409 with message |
| Record not found | Raise `HTTPException(404)` | HTTP 404 |
| Invalid condition value | Pydantic validator | HTTP 422 |
| Future year or year < 1900 | Pydantic validator | HTTP 422 |
| DB unreachable | FastAPI exception handler | HTTP 503 |

---

## Risks & Concerns

| Concern | Location | Impact | Mitigation |
| ------- | -------- | ------ | ---------- |
| None found | — | — | New feature, no existing code to conflict with |

---

## Tech Decisions

| Decision | Choice | Rationale |
| -------- | ------ | --------- |
| Async SQLAlchemy | `sqlalchemy[asyncio]` + `asyncpg` | Matches FastAPI's async nature |
| Track storage | JSON column (not separate table) | Tracks are always loaded with the record; no need for independent track queries |
| Unique constraint | `UNIQUE(artist, album)` | Prevents accidental duplicates per spec AC-03 |
| Pagination | `limit` + `offset` | Simple, stateless, easy to implement |
| Container | Docker Compose only for DB | App runs locally via `uvicorn` for simplicity; no Dockerfile needed |

---

## AD-NNN Candidate

This is a new package convention (`src/record_catalog/`) that future features may follow. If we want to formalize this, we can add an AD entry. For now, keep it local.