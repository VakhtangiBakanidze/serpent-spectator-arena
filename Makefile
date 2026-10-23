.PHONY: help dev run-backend run-frontend test-backend test-backend-integration test-backend-all sync-backend

help:
	@echo "Serpent Spectator Arena Commands:"
	@echo ""
	@echo "Development (both services):"
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
