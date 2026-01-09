# Docker shortcuts for pricing-manager-app
.PHONY: help up down build logs shell test coverage coverage-html migrate makemigrations

# Default target
help:
	@echo "Available commands:"
	@echo ""
	@echo "Container Management:"
	@echo "  make up              - Start containers in detached mode"
	@echo "  make down            - Stop containers"
	@echo "  make build           - Build containers"
	@echo "  make restart         - Restart all containers"
	@echo ""
	@echo "Logs:"
	@echo "  make logs            - View all container logs"
	@echo "  make logs-backend    - View backend logs"
	@echo "  make logs-celery     - View celery worker logs"
	@echo "  make logs-beat       - View celery beat logs"
	@echo "  make logs-mysql      - View MySQL source logs"
	@echo "  make logs-analytics  - View MySQL analytics logs"
	@echo "  make logs-redis      - View Redis logs"
	@echo ""
	@echo "Backend:"
	@echo "  make shell           - Open bash shell in backend container"
	@echo "  make test            - Run tests"
	@echo "  make coverage        - Run tests with coverage"
	@echo "  make coverage-html   - Generate HTML coverage report"
	@echo "  make migrate         - Run Django migrations"
	@echo "  make makemigrations  - Create new migrations"
	@echo "  make uv              - Run uv command (usage: make uv cmd='add package')"

# Container management
up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-celery:
	docker compose logs -f celery_worker

logs-beat:
	docker compose logs -f celery_beat

logs-mysql:
	docker compose logs -f mysql_source

logs-analytics:
	docker compose logs -f mysql_analytics

logs-redis:
	docker compose logs -f redis

restart:
	docker compose restart

# Backend shortcuts
shell:
	docker compose exec backend bash

test:
	docker compose exec backend bash -lc "uv run coverage run manage.py test --settings=config.settings_test"

coverage:
	docker compose exec backend bash -lc "uv run coverage run -m pytest"

coverage-html:
	docker compose exec backend bash -lc "uv run coverage html"

# Django commands
migrate:
	docker compose exec backend bash -lc "uv run python manage.py migrate"

makemigrations:
	docker compose exec backend bash -lc "uv run python manage.py makemigrations"

createsuperuser:
	docker compose exec backend bash -lc "uv run python manage.py createsuperuser"

# Generic uv command runner (usage: make uv cmd="add requests")
uv:
	docker compose exec backend bash -lc "uv $(cmd)"
