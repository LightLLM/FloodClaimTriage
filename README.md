# Flood Claim Triage MVP

A B2B web application that helps reinsurers prioritize properties for review after flood events using satellite, weather, terrain, and exposure data.

## Overview

This MVP turns multi-source geospatial data into:
- Damage-confidence scores
- Inspection priorities
- Evidence maps
- Complete audit trails

The system is a human-in-the-loop decision-support tool. It never makes automated claim-payment decisions.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- pnpm

### Local Development with Docker

```bash
# Start all services
docker compose up --build

# API will be available at http://localhost:8000
# Web UI will be available at http://localhost:5173
# PostgreSQL at localhost:5432
# MinIO at localhost:9000
```

### Backend Development

```bash
cd apps/api

# Install dependencies
uv sync

# Run migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd apps/web

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

## Testing

```bash
# Backend tests
cd apps/api
uv run pytest

# Frontend tests
cd apps/web
pnpm test

# Linting and type checks
cd apps/api
uv run ruff check .
uv run mypy .

cd apps/web
pnpm lint
pnpm typecheck
```

## Project Structure

```
flood-triage-mvp/
├─ apps/
│  ├─ api/          # FastAPI backend
│  └─ web/          # React frontend
├─ pipelines/       # Data ingestion and processing
│  ├─ ingestion/
│  ├─ features/
│  ├─ scoring/
│  └─ validation/
├─ infra/           # Infrastructure as code
│  ├─ docker/
│  └─ terraform/
├─ docs/            # Documentation
├─ tests/           # Integration tests
└─ .github/workflows/ # CI/CD
```

## Technology Stack

**Backend**: Python 3.11+, FastAPI, PostgreSQL, PostGIS, SQLAlchemy, Pydantic

**Frontend**: TypeScript, React 18, Vite, TanStack Query, Tailwind CSS, MapLibre GL

**Infrastructure**: Docker, PostgreSQL 16, PostGIS, MinIO/S3, GitHub Actions

**Data**: Cloud-Optimized GeoTIFF, Zarr, GeoParquet, STAC

## Documentation

- [Architecture](docs/architecture.md)
- [Data Model](docs/data-model.md)
- [API Reference](docs/api.md)
- [Pilot Plan](docs/pilot-plan.md)
- [Security](docs/security.md)

## License

Proprietary - All Rights Reserved
