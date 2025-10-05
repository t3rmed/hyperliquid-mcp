# Hyperliquid MCP Server Makefile

.PHONY: help build run dev test clean install

# Default target
help:
	@echo "Available commands:"
	@echo "  build     - Build the Docker image"
	@echo "  run       - Run the container in production mode"
	@echo "  dev       - Run the container in development mode"
	@echo "  test      - Run tests"
	@echo "  clean     - Clean up Docker resources"
	@echo "  install   - Install dependencies with uv"
	@echo "  lint      - Run linting"
	@echo "  format    - Format code"

# Build the Docker image
build:
	docker-compose build hyperliquid-mcp

# Run in production mode
run:
	docker-compose up hyperliquid-mcp

# Run in development mode with hot reloading
dev:
	docker-compose --profile dev up hyperliquid-mcp-dev

# Install dependencies locally
install:
	uv sync

# Run tests
test:
	uv run pytest

# Run tests with coverage
test-cov:
	uv run pytest --cov=hyperliquid_mcp_server --cov-report=term-missing --cov-report=html

# Run tests in verbose mode
test-verbose:
	uv run pytest -v

# Run specific test file
test-file:
	uv run pytest $(FILE) -v

# Lint code
lint:
	uv run ruff check .
	uv run mypy .

# Format code
format:
	uv run black .
	uv run isort .
	uv run ruff --fix .

# Clean up Docker resources
clean:
	docker-compose down --rmi all --volumes --remove-orphans
	docker system prune -f

# Run the server locally (without Docker)
local:
	uv run python -m hyperliquid_mcp_server.main

# Build and run
up: build run

# Build and run in dev mode
dev-up: build dev

# Stop all containers
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Shell into the container
shell:
	docker-compose exec hyperliquid-mcp /bin/bash

# Update dependencies
update:
	uv sync --upgrade