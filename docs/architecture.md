# Architecture

## System Overview

The Flood Claim Triage MVP is a three-tier web application designed to help reinsurers prioritize property inspections after flood events.

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Browser                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │   React Frontend (TypeScript, Vite, Tailwind)         │  │
│  │   - Authentication & RBAC                             │  │
│  │   - Event Dashboard                                   │  │
│  │   - Triage Queue & Map                                │  │
│  │   - Evidence Viewer                                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │ HTTPS / REST
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python 3.11+)                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │   API Layer                                           │  │
│  │   - JWT Authentication                                │  │
│  │   - Event Management                                  │  │
│  │   - Triage Endpoints                                  │  │
│  │   - Score Review & Audit                              │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │   Business Logic Layer                                │  │
│  │   - ScoringService (v0.1 rule-based)                  │  │
│  │   - Evidence Generation                               │  │
│  │   - Audit Logging                                     │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌─────────────────┐ ┌────────────────┐ ┌──────────────────┐
│  PostgreSQL 16  │ │  MinIO / S3    │ │  Redis (Future)  │
│   + PostGIS     │ │  (COG, Zarr,   │ │  (Job Queue)     │
│                 │ │   GeoParquet)  │ │                  │
└─────────────────┘ └────────────────┘ └──────────────────┘
```

## Layers

### Presentation Layer (Frontend)

**Technology**: React 18, TypeScript, Vite, Tailwind CSS, MapLibre GL JS

**Responsibilities**:
- User authentication and session management
- Event selection and filtering
- Triage queue visualization
- Property detail views with evidence
- Score review and override
- CSV export
- Map-based property visualization

**Key Features**:
- JWT-based authentication with automatic token refresh
- Role-based UI rendering (admin, analyst, reviewer, viewer)
- Responsive dark-mode enterprise design
- Real-time filtering and sorting
- Evidence transparency displays

### Application Layer (Backend API)

**Technology**: FastAPI, Python 3.11+, Pydantic v2

**Responsibilities**:
- REST API endpoints for all operations
- JWT token generation and validation
- Request validation with Pydantic schemas
- Business logic orchestration
- Audit trail generation

**Endpoints**:
- `/api/v1/auth/*` - Authentication and user management
- `/api/v1/events/*` - Event CRUD and scoring triggers
- `/api/v1/properties/*` - Property queries
- `/api/v1/events/{id}/triage` - Triage queue with filters
- `/api/v1/events/{id}/properties/{id}/evidence` - Evidence details
- `/api/v1/scores/{id}/review` - Human review and override
- `/api/v1/events/{id}/export.csv` - CSV export
- `/health` - Health check

### Business Logic Layer

**Scoring Service**:
- Implements MVP v0.1 rule-based damage probability model
- Calculates inspection priority (P1, P2, P3)
- Generates explainable evidence payloads
- Tracks model version and input data lineage

**Audit Service** (implicit):
- Records all human overrides
- Tracks before/after values
- Captures reasons and timestamps
- Links to user, property, event, and score

### Data Layer

**PostgreSQL 16 + PostGIS**:
- Stores structured application data
- Spatial queries for property-event joins
- Full ACID compliance for audit records
- Indexed for triage queue queries

**MinIO / S3**:
- Stores Cloud-Optimized GeoTIFFs (satellite imagery)
- Stores Zarr arrays (weather/model data)
- Stores GeoParquet files (analytical outputs)
- STAC metadata references

## Data Pipelines (Future)

```
┌──────────────────────────────────────────────────────────────┐
│               Data Ingestion & Processing                     │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  STAC      │  │  Weather     │  │  Elevation / Terrain │ │
│  │  Satellite │  │  API         │  │  DEM                 │ │
│  │  Imagery   │  │              │  │                      │ │
│  └────────────┘  └──────────────┘  └──────────────────────┘ │
│         │               │                    │                │
│         ▼               ▼                    ▼                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │         Feature Engineering Pipeline                  │    │
│  │  - Flood extent detection                            │    │
│  │  - Distance to flood calculation                     │    │
│  │  - Rainfall analysis                                 │    │
│  │  - Optical change detection                          │    │
│  └──────────────────────────────────────────────────────┘    │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              Observation Records → DB                 │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

## Security Architecture

- **Authentication**: JWT tokens with 30-minute access and 7-day refresh
- **Authorization**: Role-based access control (admin, analyst, reviewer, viewer)
- **Transport**: TLS 1.3 for all API communication
- **Database**: Encrypted at rest, parameterized queries only
- **Object Storage**: Encrypted at rest, presigned URLs for access
- **Secrets**: Environment variables, never committed to Git
- **Audit**: Immutable append-only audit log table

## Deployment Architecture

### Development (Docker Compose)
- All services run locally
- PostgreSQL + PostGIS in container
- MinIO for local S3-compatible storage
- Hot-reloading for API and frontend
- No authentication required for local MinIO

### Production (Future)
- Container orchestration (ECS, Cloud Run, or K8s)
- Managed PostgreSQL (RDS, Cloud SQL, or Aurora)
- S3 or equivalent object storage
- CDN for frontend static assets
- Secrets manager integration
- VPC isolation, least-privilege IAM
- Infrastructure as Code with Terraform

## Monitoring & Observability

**Current**:
- Structured JSON logging
- Health check endpoint
- Manual log inspection

**Planned**:
- OpenTelemetry traces and metrics
- Prometheus metrics export
- Grafana dashboards
- Sentry error tracking
- Log aggregation (CloudWatch, Datadog, or ELK)

## Scalability Considerations

**MVP (Current)**:
- Single API instance
- Synchronous scoring (acceptable for pilot)
- In-memory session state
- Direct database queries

**Production (Future)**:
- Horizontal API scaling behind load balancer
- Background job queue (Redis + workers) for scoring
- Read replicas for query-heavy workloads
- CDN caching for static assets
- Connection pooling for database

## Data Lineage

Every score includes:
- `model_version` - Scoring algorithm version
- `evidence.data_sources` - STAC item IDs, weather API references
- `created_at` - Timestamp of score generation
- Link to `observation` record with raw feature values

This enables:
- Reproducibility of scores
- Model comparison across versions
- Input data traceability
- Regulatory compliance

## Technology Choices

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Frontend | React 18 + TypeScript | Industry standard, strong typing, rich ecosystem |
| Build Tool | Vite | Fast dev server, modern ESM-based tooling |
| State Management | Zustand + React Query | Simple, performant, cache management |
| UI Framework | Tailwind CSS | Rapid development, consistent design system |
| Map | MapLibre GL JS | Open-source, vector tiles, WebGL performance |
| Backend | FastAPI | Modern async Python, automatic OpenAPI docs |
| ORM | SQLAlchemy 2.0 | Mature, async support, type safety |
| Validation | Pydantic v2 | Runtime validation, IDE integration, performance |
| Database | PostgreSQL 16 + PostGIS | ACID compliance, spatial queries, proven reliability |
| Object Storage | MinIO (dev) / S3 (prod) | S3-compatible, COG/Zarr support |
| Migrations | Alembic | Integrates with SQLAlchemy, version control |
| Testing | pytest (backend), Vitest (frontend) | Standard tools, async support |

## Decision Log

### Why Rule-Based Model for MVP?
- Explainable by design (critical for reinsurer trust)
- No training data required for initial pilot
- Transparent scoring formula
- Easy to tune based on pilot feedback
- Establishes baseline for ML comparison

### Why PostgreSQL + PostGIS?
- Proven reliability for transactional data
- Native spatial query support
- Full ACID compliance for audit trail
- Strong ecosystem and operational tooling

### Why FastAPI?
- Automatic API documentation
- Native async/await support
- Built-in validation with Pydantic
- High performance comparable to Node.js
- Strong Python ecosystem for geospatial libraries

### Why Dark Mode Enterprise UI?
- Reduces eye strain for long analyst sessions
- Professional appearance for B2B product
- Aligns with catastrophe analytics industry standards
- High contrast improves priority indicator visibility
