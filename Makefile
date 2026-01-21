.PHONY: help up-main-server down-main-server logs-main-server dev-install dev-run

help:
	@echo "Available commands:"
	@echo "  make up-main-server      - Start only main-server container"
	@echo "  make down-main-server    - Stop main-server container"
	@echo "  make logs-main-server    - View main-server logs"
	@echo "  make dev-install         - Install dependencies for local development"
	@echo "  make dev-run             - Run main-server locally (no Docker)"

up-main-server:
	docker-compose up -d postgres main-server

down-main-server:
	docker-compose down main-server

logs-main-server:
	docker-compose logs -f main-server

dev-install:
	pip install -r main-server/requirements.txt

dev-run:
	cd main-server && uv run uvicorn app.main:app --port 8000 --reload
