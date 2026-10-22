.PHONY: help run run-backend dev-backend test-backend sync-backend

help:
	@echo "Serpent Spectator Arena Commands:"
	@echo ""
	@echo "Backend:"
	@echo "  make run-backend (or make run) - Start FastAPI backend with hot-reload"
	@echo "  make test-backend              - Run backend pytest tests"
	@echo "  make sync-backend              - Install/sync backend dependencies using uv"

run run-backend dev-backend:
	$(MAKE) -C backend run

test-backend:
	$(MAKE) -C backend test

sync-backend:
	$(MAKE) -C backend sync
