FROM python:3.11-slim

WORKDIR /app

# Runtime deps for PostgreSQL client libraries
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY pyproject.toml README.md ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY tests ./tests
COPY scripts ./scripts

RUN uv pip install --system -e ".[dev]"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
