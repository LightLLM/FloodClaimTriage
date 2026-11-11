# Flood Claim Triage MVP Rules

This file contains the core rules and guidelines for the Flood Claim Triage MVP project.

## Technology Stack

### Backend
- Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic
- PostgreSQL 16 with PostGIS for geospatial data
- Redis for background jobs (if needed)
- Rasterio, GDAL, Rioxarray for geospatial processing

### Frontend
- TypeScript, React 18+, Vite
- TanStack Query for data fetching
- Zustand for state management
- Tailwind CSS with specified color scheme
- MapLibre GL JS for mapping

### Color Scheme
- Background: #0f172a
- Card: #1f2937
- Border: #334155
- Primary: #38bdf8
- P1 (Critical): #ef4444
- P2 (Review): #f59e0b
- P3 (Low): #10b981
- Text: #e5e7eb
- Muted Text: #94a3b8

## Scoring Rules

MVP v0.1 uses a rule-based model:

```
damage_probability =
  0.45 * flood_extent_signal
+ 0.20 * proximity_signal
+ 0.15 * rainfall_signal
+ 0.10 * river_stage_signal
+ 0.10 * optical_change_signal
- 0.10 * elevation_signal
```

Clamped between 0.01 and 0.99.

Priority assignment:
- P1: probability >= 0.75 (Field inspection)
- P2: probability >= 0.45 and < 0.75 (Desk review)
- P3: probability < 0.45 (No action)

## Code Standards

- Write strongly typed Python and TypeScript
- Use Pydantic models for all API schemas
- Use dependency injection for database sessions
- Never put business logic in route handlers
- Use Alembic migrations for schema changes
- Use parameterized queries only
- Validate every API input
- Use structured JSON logging
- Never log secrets, tokens, or PII
- Use environment variables for configuration
- Add tests for scoring logic and API endpoints
- Use conventional commits

## Security Requirements

- Encrypt data in transit and at rest
- Use least-privilege IAM roles
- Store secrets in secrets manager
- Enforce RBAC
- Maintain immutable audit logs
- Anonymize or pseudonymize customer data

## Never Do

- Generate massive unreviewable changes
- Store raw addresses in database
- Concatenate SQL strings
- Log sensitive data
- Commit secrets to Git
- Override security controls
- Skip input validation
- Make automated claim-payment decisions

## Always Do

- Explain scoring decisions with evidence
- Track data lineage
- Log human overrides
- Use transactions for multi-step operations
- Validate CRS and geometry before processing
- Make ingestion jobs idempotent
- Test migrations up and down
