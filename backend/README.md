
# Das Backend

## Overview
This folder contains the small Flask backend used by the WIZARD tournament webapp. It serves the frontend and provides a few convenience endpoints to initialize and inspect the PostgreSQL database.

## Tech stack
- Python + Flask
- PostgreSQL (in a Docker container)
- Docker Compose for running app + database
- `uv` for Python dependency management (project uses `uv` as noted)

## Prerequisites
- Docker & Docker Compose installed
- `uv` (optional) for managing Python dependencies
- Copy `example.env` to `.env` and adjust credentials before starting

## Environment variables
Place environment variables in `.env` (see `example.env`). The backend reads these variables (via python-dotenv). Important variables used by `app.py`:

- `DB_HOST` (defaults to `db`)
- `POSTGRES_DB` (defaults to `wizard`)
- `POSTGRES_USER` (defaults to `user`)
- `POSTGRES_PASSWORD` (defaults to `pass`)

## Run (quick)
Start the whole stack (app + database) with:

```bash
docker compose up
```

After startup open http://localhost:5000 in your browser to see the frontend.

## Database
- The PostgreSQL server runs in a container; its data is stored in a Docker volume so it persists across restarts.
- The project exposes a small helper endpoint to create the tables if they are missing (see Endpoints below).

## Endpoints (from `app.py`)
- `GET /` — Serve the frontend `index.html` from the `frontend` folder.
- `GET /init_db` — Initialize database schema (creates `players` and `tournaments` tables if they do not exist).
- `GET /dump_db` — Debug endpoint: returns current rows from `players` and `tournaments` (plain text). Do not expose this in production.

You can call the endpoints with `curl`, for example:

```bash
curl http://localhost:5000/init_db
curl http://localhost:5000/dump_db
```

## Contribution
- To add a Python dependency run:

```bash
uv add <package>
```

