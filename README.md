# Flood Claim Triage MVP

A B2B web application that helps reinsurers prioritize properties for review after flood events using satellite, weather, terrain, and exposure data.

## Overview

This MVP turns multi-source geospatial data into:
- **Damage-confidence scores** using explainable rule-based models
- **Inspection priorities** (P1, P2, P3) with recommended actions
- **Evidence maps** showing all input data sources
- **Complete audit trails** for regulatory compliance

The system is a human-in-the-loop decision-support tool. It never makes automated claim-payment decisions.

## Key Features

✅ **JWT Authentication** with role-based access control (admin, analyst, reviewer, viewer)  
✅ **Event Management** - Create and track flood events  
✅ **Property Portfolio** - Ingest and manage insured properties  
✅ **Rule-Based Scoring** - MVP v0.1 transparent damage probability model  
✅ **Triage Queue** - Sortable, filterable list of properties by priority  
✅ **Evidence Transparency** - View all input signals and data sources  
✅ **Human Override** - Analysts can accept or override recommendations with reasons  
✅ **Audit Trail** - Immutable log of all decisions  
✅ **CSV Export** - Download prioritized inspection lists  
✅ **Dark Mode UI** - Professional enterprise interface  

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/LightLLM/FloodClaimTriage.git
cd FloodClaimTriage

# Start all services
docker compose up --build

# Wait for services to be ready, then access:
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Web UI: http://localhost:5173
# - MinIO Console: http://localhost:9001
```

### Option 2: Local Development

#### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 16 with PostGIS
- pnpm (for frontend)
- uv (for Python dependencies)

#### Backend Setup

```bash
cd apps/api

# Install uv if not already installed
pip install uv

# Install dependencies
uv sync

# Copy environment file
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
uv run alembic upgrade head

# Seed sample data (optional)
uv run python scripts/seed_data.py

# Start development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd apps/web

# Install pnpm if not already installed
npm install -g pnpm

# Install dependencies
pnpm install

# Copy environment file
cp .env.example .env
# Edit .env if needed (defaults to http://localhost:8000)

# Start development server
pnpm dev
```

### Sample Login Credentials

After running the seed script:
- **Admin**: admin@example.com / admin123
- **Analyst**: analyst@example.com / analyst123
- **Reviewer**: reviewer@example.com / reviewer123
- **Viewer**: viewer@example.com / viewer123

## Using the Application

### 1. Login
Navigate to http://localhost:5173 and login with one of the sample credentials.

### 2. Select an Event
Choose a flood event from the dropdown (sample events are pre-loaded).

### 3. View KPIs
See the distribution of properties across priority levels (P1, P2, P3).

### 4. Filter the Triage Queue
- Click priority buttons to filter by P1, P2, or P3
- View damage probability and exposure values
- See recommended actions for each property

### 5. Review Evidence (Coming Soon)
Click a property to view detailed evidence including:
- Flood extent signal
- Proximity to flood
- Rainfall data
- Optical change detection
- Elevation factors
- Data source references

### 6. Export Results
Click "Export CSV" to download the prioritized inspection list.

## Development Commands

Use the Makefile for common tasks:

```bash
make help          # Show all available commands
make up            # Start Docker services
make down          # Stop Docker services
make logs          # View service logs
make test          # Run all tests
make lint          # Run linters
make format        # Format code
make migrate-up    # Run database migrations
make seed          # Load sample data
make dev-api       # Start API in development mode
make dev-web       # Start frontend in development mode
```

## Testing

### Backend Tests

```bash
cd apps/api

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_scoring.py -v
```

### Frontend Tests

```bash
cd apps/web

# Run tests (when implemented)
pnpm test

# Type checking
pnpm typecheck

# Linting
pnpm lint
```

### Linting and Type Checking

```bash
# Backend
cd apps/api
uv run ruff check .        # Linting
uv run mypy app            # Type checking

# Frontend
cd apps/web
pnpm lint                  # ESLint
pnpm typecheck             # TypeScript
```

## Project Structure

```
flood-triage-mvp/
├─ apps/
│  ├─ api/                 # FastAPI backend
│  │  ├─ app/
│  │  │  ├─ api/          # Route handlers
│  │  │  ├─ core/         # Config, security
│  │  │  ├─ db/           # Database setup
│  │  │  ├─ models/       # SQLAlchemy models
│  │  │  ├─ schemas/      # Pydantic schemas
│  │  │  └─ services/     # Business logic
│  │  ├─ alembic/         # Database migrations
│  │  ├─ scripts/         # Utility scripts
│  │  └─ tests/           # Backend tests
│  └─ web/                # React frontend
│     ├─ src/
│     │  ├─ components/   # UI components
│     │  ├─ pages/        # Page components
│     │  ├─ lib/          # API client, utilities
│     │  ├─ store/        # State management
│     │  └─ types/        # TypeScript types
│     └─ public/          # Static assets
├─ pipelines/             # Data processing (future)
│  ├─ ingestion/
│  ├─ features/
│  ├─ scoring/
│  └─ validation/
├─ infra/                 # Infrastructure
│  ├─ docker/
│  └─ terraform/
├─ docs/                  # Documentation
│  ├─ architecture.md
│  ├─ data-model.md
│  ├─ api.md
│  ├─ pilot-plan.md
│  └─ security.md
└─ .github/workflows/     # CI/CD pipelines
```

## Technology Stack

### Backend
- **Python 3.11+** - Modern async Python
- **FastAPI** - High-performance API framework
- **Pydantic v2** - Data validation and settings
- **SQLAlchemy 2.0** - Async ORM
- **Alembic** - Database migrations
- **PostgreSQL 16** - Primary database
- **PostGIS** - Geospatial extension
- **asyncpg** - Async PostgreSQL driver

### Frontend
- **TypeScript** - Type-safe JavaScript
- **React 18** - UI framework
- **Vite** - Fast build tool
- **TanStack Query** - Data fetching and caching
- **Zustand** - State management
- **Tailwind CSS** - Utility-first CSS
- **MapLibre GL JS** - Open-source mapping (future)
- **Recharts** - Charting library (future)

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Local orchestration
- **MinIO** - S3-compatible object storage
- **GitHub Actions** - CI/CD
- **Terraform** - Infrastructure as Code (future)

### Data Formats
- **Cloud-Optimized GeoTIFF** - Raster imagery
- **Zarr** - Multidimensional arrays
- **GeoParquet** - Columnar geospatial data
- **STAC** - Satellite data metadata

## Scoring Model

MVP v0.1 uses an explainable rule-based model:

```
damage_probability = 
  0.45 × flood_extent_signal
+ 0.20 × proximity_signal
+ 0.15 × rainfall_signal
+ 0.10 × river_stage_signal
+ 0.10 × optical_change_signal
- 0.10 × elevation_signal

Clamped to [0.01, 0.99]
```

**Priority Assignment**:
- **P1** (≥ 0.75): Field inspection required
- **P2** (0.45-0.74): Desk review recommended
- **P3** (< 0.45): No immediate action

**Why Rule-Based?**
- Fully explainable to reinsurers
- No training data required
- Easy to tune based on pilot feedback
- Establishes baseline for future ML models

## API Documentation

Interactive API documentation is automatically generated by FastAPI:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

See [docs/api.md](docs/api.md) for detailed endpoint documentation.

## Documentation

- **[Architecture](docs/architecture.md)** - System design, components, data flow
- **[Data Model](docs/data-model.md)** - Database schema, relationships, indexes
- **[API Reference](docs/api.md)** - All endpoints with examples
- **[Pilot Plan](docs/pilot-plan.md)** - Six-week pilot timeline and metrics
- **[Security](docs/security.md)** - Threat model, controls, compliance

## Roadmap

### MVP v0.1 (Current) ✅
- Rule-based scoring model
- Basic web interface
- Manual event creation
- CSV export
- Audit trail

### MVP v0.2 (Next)
- Map visualization with MapLibre GL
- Evidence detail drawer
- Real-time score updates
- Property search and filtering
- Enhanced KPI dashboard

### Production Features
- Automated satellite data ingestion
- Machine learning scoring model
- Real-time event detection
- Multi-tenant architecture
- Advanced analytics and reporting
- Mobile-responsive design
- Offline mode support

## Contributing

This is a pilot project. Contributions should follow:
- Conventional commits (feat, fix, docs, test, etc.)
- All tests must pass
- Linting and type checking must pass
- Pull request review required

## License

Proprietary - All Rights Reserved

## Support

For questions or issues during the pilot:
- Create a GitHub issue
- Contact the development team
- Review documentation in `/docs`

## Acknowledgments

Built for reinsurers by the Flood Triage team.  
Powered by open-source technologies and satellite data.
