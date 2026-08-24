# Record Store Catalog Specification

## Problem Statement

A record store needs to manage its inventory of vinyl records/disks. Currently the store has no digital catalog — inventory is tracked informally. We need a REST API to add, list, search, update, and delete records so the store can keep an accurate, queryable inventory.

## Goals

- [ ] Provide a REST API to CRUD vinyl records (create, read, update, delete)
- [ ] Support search/filtering of records by common attributes
- [ ] Persist data in PostgreSQL via Docker Compose

## Out of Scope

| Feature                          | Reason                                     |
| -------------------------------- | ------------------------------------------ |
| Authentication / user accounts   | Single-user local catalog                  |
| Web frontend / UI                | API-only per user decision                 |
| Sales / stock movements          | Catalog-only feature                       |
| Import from external sources     | Not requested                              |
| Image uploads of cover art       | Not requested                              |

---

## Assumptions & Open Questions

| Assumption / decision                  | Chosen default                                   | Rationale                                 | Confirmed? |
| -------------------------------------- | ------------------------------------------------ | ----------------------------------------- | ---------- |
| Framework                               | FastAPI                                          | Modern async, auto OpenAPI docs           | n (agent)  |
| ORM / DB access                         | SQLAlchemy 2.0 + asyncpg                         | Standard, type-friendly                   | n (agent)  |
| Migrations                              | Alembic                                          | Standard SQLAlchemy migration tool        | n (agent)  |
| Conservation status enum                | `Mint, Excellent, Very Good, Good, Fair, Poor`   | Common vinyl grading scale                | n (agent)  |
| Track duration format                   | ISO 8601 duration string (e.g. `PT4M32S`)        | Unambiguous, parseable                    | n (agent)  |
| Pagination                              | `limit` (default 20, max 100) + `offset`         | Simple, predictable                       | n (agent)  |
| DB host/port                            | `db:5432` (Docker) / `localhost:5432` (local)    | Standard                                  | n (agent)  |

**Open questions:** none — all resolved or logged above (required before the spec is confirmed).

---

## User Stories

### P1: Create a record ⭐ MVP

**User Story**: As a store clerk, I want to add a vinyl record to the catalog so that it is recorded in inventory.

**Why P1**: Without creation, there is no catalog.

**Acceptance Criteria**:

1. WHEN a client POSTs a valid record to `/records` THEN the system SHALL create it, return HTTP 201, and return the created record with an assigned `id` and `created_at`.
2. WHEN a client POSTs a record missing a required field (`artist` or `album`) THEN the system SHALL return HTTP 422 with a validation error.
3. WHEN a client POSTs a record with a duplicate `artist` + `album` combination THEN the system SHALL return HTTP 409 Conflict and not create a duplicate.

**Independent Test**: POST a valid record and observe HTTP 201 with an id; POST invalid and observe 422.

---

### P1: List records ⭐ MVP

**User Story**: As a store clerk, I want to list all records so that I can see the full catalog.

**Why P1**: The catalog must be viewable.

**Acceptance Criteria**:

1. WHEN a client GETs `/records` THEN the system SHALL return HTTP 200 with a paginated list of records (`items`, `total`, `limit`, `offset`).
2. WHEN the catalog is empty THEN the system SHALL return HTTP 200 with an empty `items` array and `total: 0`.
3. WHEN a client sends `limit > 100` THEN the system SHALL clamp it to 100.

**Independent Test**: GET `/records` on empty DB returns empty array; after adds, returns them.

---

### P1: Retrieve a single record ⭐ MVP

**User Story**: As a store clerk, I want to look up a single record by id.

**Why P1**: Needed to view details of one record.

**Acceptance Criteria**:

1. WHEN a client GETs `/records/{id}` for an existing record THEN the system SHALL return HTTP 200 with the record.
2. WHEN a client GETs `/records/{id}` for a non-existent id THEN the system SHALL return HTTP 404.

---

### P1: Update a record ⭐ MVP

**User Story**: As a store clerk, I want to update a record's details so that corrections can be made.

**Why P1**: Corrections are part of maintaining a catalog.

**Acceptance Criteria**:

1. WHEN a client PUTs `/records/{id}` with valid fields THEN the system SHALL update the record and return HTTP 200 with the updated record.
2. WHEN a client PUTs `/records/{id}` with a non-existent id THEN the system SHALL return HTTP 404.
3. WHEN a client PUTs `/records/{id}` that changes to a duplicate `artist` + `album` THEN the system SHALL return HTTP 409.

---

### P1: Delete a record ⭐ MVP

**User Story**: As a store clerk, I want to remove a record so that sold or removed stock is not listed.

**Why P1**: Catalog must reflect reality.

**Acceptance Criteria**:

1. WHEN a client DELETEs `/records/{id}` for an existing record THEN the system SHALL delete it and return HTTP 204.
2. WHEN a client DELETEs `/records/{id}` for a non-existent id THEN the system SHALL return HTTP 404.

---

### P2: Search records

**User Story**: As a store clerk, I want to search records by artist, album, or genre so that I can find a specific record quickly.

**Why P2**: Core usability once the catalog grows.

**Acceptance Criteria**:

1. WHEN a client GETs `/records?artist=...` THEN the system SHALL return only records whose artist contains the query (case-insensitive).
2. WHEN a client GETs `/records?album=...` THEN the system SHALL return only records whose album contains the query (case-insensitive).
3. WHEN a client GETs `/records?genre=...` THEN the system SHALL return only records whose genre equals the query (case-insensitive).
4. WHEN a client combines multiple filters THEN the system SHALL apply all of them (AND).

**Independent Test**: Add records with different artists, filter by artist, observe only matches.

---

### P2: Filter by year and conservation status

**User Story**: As a store clerk, I want to filter records by release year or condition so that I can evaluate stock.

**Why P2**: Useful for inventory management.

**Acceptance Criteria**:

1. WHEN a client GETs `/records?year=1980` THEN the system SHALL return only records released in 1980.
2. WHEN a client GETs `/records?condition=Mint` THEN the system SHALL return only records with that conservation status.

---

## Edge Cases

- WHEN a client POSTs a record with `year` in the future THEN the system SHALL reject with HTTP 422.
- WHEN a client POSTs a record with `year` older than 1900 THEN the system SHALL reject with HTTP 422.
- WHEN a client sends a malformed `condition` value THEN the system SHALL reject with HTTP 422.
- WHEN a client sends a track without `title` THEN the system SHALL reject with HTTP 422.
- WHEN the database is unreachable THEN the system SHALL return HTTP 503 Service Unavailable.

---

## Requirement Traceability

| Requirement ID | Story                     | Phase  | Status  |
| -------------- | ------------------------- | ------ | ------- |
| RCD-01         | P1: Create a record       | Design | Verified |
| RCD-02         | P1: Create a record       | Design | Verified |
| RCD-03         | P1: Create a record       | Design | Verified |
| RCD-04         | P1: List records          | Design | Verified |
| RCD-05         | P1: List records          | Design | Verified |
| RCD-06         | P1: List records          | Design | Verified |
| RCD-07         | P1: Retrieve a record     | Design | Verified |
| RCD-08         | P1: Retrieve a record     | Design | Verified |
| RCD-09         | P1: Update a record       | Design | Verified |
| RCD-10         | P1: Update a record       | Design | Verified |
| RCD-11         | P1: Update a record       | Design | Verified |
| RCD-12         | P1: Delete a record       | Design | Verified |
| RCD-13         | P1: Delete a record       | Design | Verified |
| RCD-14         | P2: Search records        | -      | Verified |
| RCD-15         | P2: Search records        | -      | Verified |
| RCD-16         | P2: Search records        | -      | Verified |
| RCD-17         | P2: Search records        | -      | Verified |
| RCD-18         | P2: Filter by year/condition | -    | Verified |
| RCD-19         | P2: Filter by year/condition | -    | Verified |

**Coverage:** 19 total, 19 verified ✅

---

## Success Criteria

- [ ] A client can complete the full CRUD lifecycle (create → read → update → delete) for a record via the API
- [ ] Search returns only matching records
- [ ] Data survives a container restart (persisted in PostgreSQL)
