.PHONY: help run dev test sync clean

HOST ?= 127.0.0.1
PORT ?= 8000

help:
	@echo "Backend Makefile commands:"
	@echo "  make run   (or make dev)  - Run FastAPI backend with hot-reload at http://$(HOST):$(PORT)"
	@echo "  make test                 - Run pytest suite"
	@echo "  make sync                 - Sync dependencies using uv"
	@echo "  make clean                - Clean python bytecode and test caches"

run dev:
	uv run uvicorn backend.main:app --reload --host $(HOST) --port $(PORT)

test:
	uv run pytest tests/ -v

sync:
	uv sync

clean:
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

