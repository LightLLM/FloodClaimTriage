# Flood Triage API

FastAPI backend for the Flood Claim Triage MVP.

## Setup

```bash
# Install dependencies
uv sync

# Run migrations
uv run alembic upgrade head

# Seed sample data
uv run python scripts/seed_data.py

# Start development server
uv run uvicorn app.main:app --reload
```

## Testing

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Linting
uv run ruff check .

# Type checking
uv run mypy app
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: Secret key for JWT tokens
- `S3_ENDPOINT`: MinIO/S3 endpoint
- `S3_ACCESS_KEY` / `S3_SECRET_KEY`: Object storage credentials

## API Documentation

When the server is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
app/
├── api/           # Route handlers
├── core/          # Configuration and security
├── db/            # Database setup
├── models/        # SQLAlchemy models
├── schemas/       # Pydantic schemas
└── services/      # Business logic
```
