# ShopFlow Data Platform

## Purpose
A personal learning and portfolio project. It builds a full data platform for a fictional
online store, using the Olist e-commerce and marketing funnel datasets from Kaggle.
The sister repo `shopflow-brain` (the AI layer) reads only the gold tables from here.

## Structure
- `docker/compose.yml`: local services, grouped by profile (`slice` for now)
- `docker/postgres/init.sql`: creates the Airflow metadata database
- `ingestion/dags/`: Airflow DAGs, plus plain helper modules they import
- `tenants/`: one YAML file per tenant (source folders, target raw schema)
- `data/raw/`: Kaggle CSVs (olist, marketing_funnel). Never committed.
- `tests/`: pytest tests

## Commands
- Install: `uv sync`
- Lint and format: `uv run ruff check . --fix && uv run ruff format .`
- Test: `uv run pytest -q`
- Start services: `docker compose -f docker/compose.yml --profile slice up -d`
- Stop services: `docker compose -f docker/compose.yml --profile slice down`

## Local URLs
- Airflow: http://localhost:18080
- Neo4j Browser: http://localhost:17474
- Qdrant dashboard: http://localhost:16333/dashboard
- Postgres: localhost:15432

## Rules
- Personal project only. Never add code, data, credentials or context from any employer.
- Never commit `data/`, `.env` or any secret. Use `.env.example` for placeholders.
- Every new feature comes with at least one test, and CI must stay green.
- Python 3.12, managed with uv. Format and lint with ruff.
- Keep commits small, with clear messages.
- Record important design choices and trade-offs in `docs/decisions.md`.
- Explain what you change and why, so the owner learns from each step.
