.PHONY: help dev run-backend run-frontend test-backend sync-backend

help:
	@echo "Serpent Spectator Arena Commands:"
	@echo ""
	@echo "Development (both services):"
	@echo "  make dev (or npm run dev)      - Run backend & frontend concurrently"
	@echo ""
	@echo "Backend:"
	@echo "  make run-backend               - Start FastAPI backend with hot-reload"
	@echo "  make test-backend              - Run backend pytest tests"
	@echo "  make sync-backend              - Install/sync backend dependencies using uv"
	@echo ""
	@echo "Frontend:"
	@echo "  make run-frontend              - Start frontend Vite dev server"

dev:
	npm run dev

run-backend:
	$(MAKE) -C backend run

run-frontend:
	npm run --prefix frontend dev

test-backend:
	$(MAKE) -C backend test

sync-backend:
	$(MAKE) -C backend sync
