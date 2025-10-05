# Docker & uv Setup Guide

This document provides a quick start guide for the Python/Docker version of the Hyperliquid MCP server.

## Quick Start

### Local Development with uv
```bash
# Install dependencies
uv sync

# Run the server
uv run python -m hyperliquid_mcp_server.main

# Run with environment variables
HYPERLIQUID_TESTNET=true uv run python -m hyperliquid_mcp_server.main
```

### Docker Development
```bash
# Build the image
docker build -t hyperliquid-mcp-server .

# Run with environment file
docker run --rm -i --env-file .env hyperliquid-mcp-server

# Run with inline environment variables
docker run --rm -i \
  -e HYPERLIQUID_TESTNET=true \
  -e HYPERLIQUID_PRIVATE_KEY=0x... \
  hyperliquid-mcp-server
```

### Docker Compose
```bash
# Production mode
docker-compose up --build

# Development mode with hot reloading
docker-compose --profile dev up --build

# Background mode
docker-compose up -d
```

### Using Make Commands
```bash
make install    # Install dependencies with uv
make local      # Run locally without Docker
make build      # Build Docker image
make run        # Run with Docker Compose
make dev        # Development mode with hot reloading
make test       # Run tests
make format     # Format code
make clean      # Clean Docker resources
```

## Environment Configuration

Create a `.env` file from the example:
```bash
cp .env.example .env
# Edit .env with your values
```

Required for trading:
- `HYPERLIQUID_PRIVATE_KEY` - Your wallet's private key
- `HYPERLIQUID_WALLET_ADDRESS` - Your wallet address (optional)
- `HYPERLIQUID_TESTNET` - Set to "true" for testnet

## Claude Desktop Integration

### Local uv installation:
```json
{
  "mcpServers": {
    "hyperliquid": {
      "command": "uv",
      "args": ["run", "python", "-m", "hyperliquid_mcp_server.main"],
      "cwd": "/path/to/hyperliq-mcp",
      "env": {
        "HYPERLIQUID_TESTNET": "true"
      }
    }
  }
}
```

### Docker installation:
```json
{
  "mcpServers": {
    "hyperliquid": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "--env-file", ".env", "hyperliquid-mcp-server:latest"],
      "cwd": "/path/to/hyperliq-mcp"
    }
  }
}
```

## Project Structure

```
hyperliquid_mcp_server/
├── __init__.py
├── main.py                 # MCP server entry point
├── types/
│   ├── __init__.py
│   └── hyperliquid.py      # Pydantic models
├── utils/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   └── hyperliquid_client.py  # API client
└── tools/
    ├── __init__.py
    ├── market_data.py      # Price and market tools
    ├── account_info.py     # Account management tools
    └── trading.py          # Trading operations
```

## Development Workflow

1. **Install dependencies**: `uv sync`
2. **Make changes** to the Python code
3. **Test locally**: `uv run python -m hyperliquid_mcp_server.main`
4. **Format code**: `uv run black . && uv run isort .`
5. **Lint code**: `uv run ruff check .`
6. **Build Docker**: `docker build -t hyperliquid-mcp-server .`
7. **Test Docker**: `docker run --rm -i hyperliquid-mcp-server`

## Benefits of Python/uv/Docker

- **uv**: Fast, modern Python package manager
- **Type Safety**: Full type hints with Pydantic models
- **Docker**: Consistent deployment across environments
- **Hot Reloading**: Development mode with volume mounts
- **Easy Scaling**: Container-ready for production deployment
- **Better Error Handling**: Python's exception handling
- **Modern Dependencies**: Latest Python ecosystem packages