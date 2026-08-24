# Feature Crew

A small multi-agent crew that turns a feature description into a plan, draft code, and review.

Uses **marvincode serve** as the LLM backend — start the server first, then run the crew.

## Quick start

```bash
# Terminal 1: start the marvincode server
marvincode serve --port 4097

# Terminal 2: run the feature crew
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

export MARVINCODE_SERVER_URL=http://127.0.0.1:4097
python -m feature_crew --description "Add a function that sums a list of integers"
```

## Record Store Catalog (REST API + React Frontend)

### Start the API

```bash
# Terminal 1: start PostgreSQL
docker compose up -d

# Terminal 2: serve the API
source .venv/bin/activate
uvicorn record_catalog.main:create_app --reload --port 8000
```

### Start the Frontend

```bash
cd frontend
npm install     # first time only
npm run dev     # starts on http://localhost:5173
```

The Vite dev server proxies `/records` requests to the API at `:8000`.

### Endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| POST   | `/records` | Create a record (201/409/422) |
| GET    | `/records` | List with pagination & filters (`?artist=`, `?album=`, `?genre=`, `?year=`, `?condition=`) |
| GET    | `/records/{id}` | Get by ID |
| PUT    | `/records/{id}` | Update (200/404/409) |
| DELETE | `/records/{id}` | Delete (204/404) |

## Verify loop

```bash
source .venv/bin/activate
ruff check src tests
ruff format --check src tests
mypy src
pytest

# Frontend
cd frontend && npx vite build  # verify build
```

See `AGENTS.md` for agent-focused harness notes.