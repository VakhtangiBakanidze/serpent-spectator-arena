.PHONY: help dev run-backend run-frontend test-backend test-backend-integration test-backend-all sync-backend docker-up docker-down docker-logs docker-clean

help:
	@echo "Serpent Spectator Arena Commands:"
	@echo ""
	@echo "Docker Compose (Postgres + App):"
	@echo "  make docker-up                       - Build and start the app container and PostgreSQL"
	@echo "  make docker-down                     - Stop all Docker Compose containers"
	@echo "  make docker-logs                     - Follow logs from all Docker Compose services"
	@echo "  make docker-clean                    - Stop containers and remove persistent volumes"
	@echo ""
	@echo "Local Development (without Docker):"
	@echo "  make dev (or npm run dev)            - Run backend & frontend concurrently"
	@echo ""
	@echo "Backend:"
	@echo "  make run-backend                     - Start FastAPI backend with hot-reload"
	@echo "  make test-backend                    - Run backend unit tests"
	@echo "  make test-backend-integration        - Run backend integration tests with SQLite"
	@echo "  make test-backend-all                - Run all backend test suites (unit + integration)"
	@echo "  make sync-backend                    - Install/sync backend dependencies using uv"
	@echo ""
	@echo "Frontend:"
	@echo "  make run-frontend                    - Start frontend Vite dev server"

docker-up:
	docker compose up --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-clean:
	docker compose down -v

dev:
	npm run dev

run-backend:
	$(MAKE) -C backend run

run-frontend:
	npm run --prefix frontend dev

test-backend:
	$(MAKE) -C backend test

test-backend-integration:
	$(MAKE) -C backend test-integration

test-backend-all:
	$(MAKE) -C backend test-all

sync-backend:
	$(MAKE) -C backend sync
