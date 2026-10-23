.PHONY: help run dev test test-integration test-all sync clean

HOST ?= 127.0.0.1
PORT ?= 8000

help:
	@echo "Backend Makefile commands:"
	@echo "  make run   (or make dev)   - Run FastAPI backend with hot-reload at http://$(HOST):$(PORT)"
	@echo "  make test                  - Run unit tests (tests/)"
	@echo "  make test-integration      - Run integration tests with SQLite (tests_integration/)"
	@echo "  make test-all              - Run both unit and integration test suites"
	@echo "  make sync                  - Sync dependencies using uv"
	@echo "  make clean                 - Clean python bytecode and test caches"

run dev:
	uv run uvicorn backend.main:app --reload --host $(HOST) --port $(PORT)

test:
	uv run pytest tests/ -v

test-integration:
	uv run pytest tests_integration/ -v

test-all:
	uv run pytest tests/ tests_integration/ -v

sync:
	uv sync

clean:
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
