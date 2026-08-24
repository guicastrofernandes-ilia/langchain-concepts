# Record Store Catalog — Tasks

**Spec**: `.specs/features/record-store-catalog/spec.md`
**Design**: `.specs/features/record-store-catalog/design.md`

## Phase 1: Scaffold & Infrastructure

### T1: Add dependencies and docker-compose

- **Done when**: `docker compose up -d` starts PostgreSQL, `pyproject.toml` lists fastapi + sqlalchemy + asyncpg + alembic + httpx
- **Files**: `pyproject.toml`, `docker-compose.yaml`
- **Tests**: none
- **Gate**: build (ruff, mypy, import check)
- **Depends on**: nothing

### T2: Database session, Base, and engine

- **Done when**: `database.py` has async engine, session factory, `Base`, and `get_db` dependency; module imports without error
- **Files**: `src/record_catalog/__init__.py`, `src/record_catalog/database.py`
- **Tests**: unit test verifies `get_db` yields a session and closes it
- **Gate**: quick (`pytest tests/test_record_catalog/ -k "test_db"`)
- **Depends on**: T1

## Phase 2: Domain Model & Schemas

### T3: SQLAlchemy Record model

- **Done when**: `Record` ORM model with all fields (artist, album, year, genre, label, condition, tracks as JSON, timestamps, unique constraint)
- **Files**: `src/record_catalog/models.py`
- **Tests**: test model construction, repr, unique constraint
- **Gate**: quick (`pytest tests/test_record_catalog/ -k "test_model"`)
- **Depends on**: T2

### T4: Pydantic schemas

- **Done when**: `RecordCreate`, `RecordResponse`, `RecordListResponse`, `ConditionEnum`, `TrackSchema` — all with validators for year bounds and condition
- **Files**: `src/record_catalog/schemas.py`
- **Tests**: test valid/invalid inputs, field validation
- **Gate**: quick (`pytest tests/test_record_catalog/ -k "test_schema"`)
- **Depends on**: T3

## Phase 3: API Endpoints (P1)

### T5: Create + Retrieve endpoints

- **Done when**: `POST /records` returns 201 with record; duplicate returns 409; `GET /records/{id}` returns 200 or 404
- **Files**: `src/record_catalog/router.py`, `src/record_catalog/main.py`
- **Tests**: e2e tests via TestClient — create (201, 422, 409), retrieve (200, 404)
- **Gate**: full (`pytest tests/test_record_catalog/ -k "test_create or test_retrieve"`)
- **Depends on**: T4

### T6: Update + Delete endpoints

- **Done when**: `PUT /records/{id}` returns 200 or 404 or 409; `DELETE /records/{id}` returns 204 or 404
- **Files**: `src/record_catalog/router.py`
- **Tests**: e2e tests — update (200, 404, 409), delete (204, 404)
- **Gate**: full (`pytest tests/test_record_catalog/ -k "test_update or test_delete"`)
- **Depends on**: T5

### T7: List with pagination

- **Done when**: `GET /records` returns paginated list with `items`, `total`, `limit`, `offset`; empty returns `total: 0`; `limit` clamped to 100
- **Files**: `src/record_catalog/router.py`
- **Tests**: e2e tests — paginated list (empty, single, multiple, limit clamp)
- **Gate**: full (`pytest tests/test_record_catalog/ -k "test_list"`)
- **Depends on**: T5

## Phase 4: Search & Filter (P2)

### T8: Search by artist, album, genre

- **Done when**: `?artist=`, `?album=`, `?genre=` filters work (case-insensitive substring); combined filters AND
- **Files**: `src/record_catalog/router.py`
- **Tests**: e2e tests — each filter individually and combined
- **Gate**: full (`pytest tests/test_record_catalog/ -k "test_search"`)
- **Depends on**: T7

### T9: Filter by year and condition

- **Done when**: `?year=`, `?condition=` filters work
- **Files**: `src/record_catalog/router.py`
- **Tests**: e2e tests — year filter, condition filter
- **Gate**: full (`pytest tests/test_record_catalog/ -k "test_filter"`)
- **Depends on**: T8

## Phase 5: Edge Cases & Integration

### T10: Error handlers and 503

- **Done when**: 422 for invalid inputs, 503 handler for DB failure
- **Files**: `src/record_catalog/router.py`, `src/record_catalog/main.py`
- **Tests**: e2e tests — future year, year < 1900, malformed condition, invalid condition value, track without title
- **Gate**: full (`pytest tests/test_record_catalog/ -k "test_error"`)
- **Depends on**: T7

---

## Test Coverage Matrix

| Layer | Coverage Expectation |
| ----- | -------------------- |
| Unit (model/schema) | Every field, every validator, edge case |
| E2E (api via TestClient) | Every route, every status code, every filter |

## Gate Check Commands

| Gate | Command |
| ---- | ------- |
| quick | `pytest tests/test_record_catalog/ -k "<filter>" -v` |
| full | `pytest tests/test_record_catalog/ -k "<filter>" -v` |
| build | `ruff check src/record_catalog tests/test_record_catalog && ruff format --check src/record_catalog tests/test_record_catalog && mypy src/record_catalog && pytest tests/test_record_catalog/ -v` |

## Execution Plan

10 tasks across 5 phases. This exceeds the ~8 task threshold for a single batch.