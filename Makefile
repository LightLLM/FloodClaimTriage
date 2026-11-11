.PHONY: help setup up down logs clean test lint format

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Initial setup - install dependencies
	@echo "Setting up backend..."
	cd apps/api && uv sync
	@echo "Setting up frontend..."
	cd apps/web && pnpm install
	@echo "Setup complete!"

up: ## Start all services with Docker Compose
	docker compose up -d

down: ## Stop all services
	docker compose down

logs: ## Show logs from all services
	docker compose logs -f

clean: ## Remove all containers, volumes, and build artifacts
	docker compose down -v
	rm -rf apps/api/.pytest_cache
	rm -rf apps/web/dist
	rm -rf apps/web/node_modules

test: ## Run all tests
	@echo "Running backend tests..."
	cd apps/api && uv run pytest
	@echo "Running frontend tests..."
	cd apps/web && pnpm test

lint: ## Run linters
	@echo "Linting backend..."
	cd apps/api && uv run ruff check .
	@echo "Linting frontend..."
	cd apps/web && pnpm lint

format: ## Format code
	@echo "Formatting backend..."
	cd apps/api && uv run ruff format .
	@echo "Formatting frontend..."
	cd apps/web && pnpm lint --fix

migrate-up: ## Run database migrations
	cd apps/api && uv run alembic upgrade head

migrate-down: ## Rollback last migration
	cd apps/api && uv run alembic downgrade -1

migrate-create: ## Create a new migration (use name=migration_name)
	cd apps/api && uv run alembic revision --autogenerate -m "$(name)"

dev-api: ## Start API in development mode
	cd apps/api && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-web: ## Start frontend in development mode
	cd apps/web && pnpm dev

seed: ## Load sample data
	cd apps/api && uv run python scripts/seed_data.py
