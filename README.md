# Hyperliquid MCP Server

A Model Context Protocol (MCP) server for interacting with the Hyperliquid DEX. This server provides tools for retrieving market data, managing positions, and executing trades on Hyperliquid.

Built with Python 3.11+ and uv package manager, with full Docker support for easy deployment.

## Features

### Market Data Tools
- `get_all_mids` - Get current mid prices for all coins
- `get_l2_book` - Get L2 order book snapshot for a specific coin
- `get_candle_snapshot` - Get historical candle data

### Account Information Tools
- `get_open_orders` - Get all open orders
- `get_user_fills` - Get trading history (fills)
- `get_user_fills_by_time` - Get fills for a specific time range
- `get_portfolio` - Get portfolio information including PnL and margin

### Trading Tools
- `place_order` - Place limit orders
- `place_trigger_order` - Place stop-loss or take-profit orders
- `cancel_order` - Cancel specific orders
- `cancel_all_orders` - Cancel all open orders

## Installation

### Prerequisites
- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (optional, for containerized deployment)

### Local Installation

1. Clone this repository
2. Install dependencies with uv:
   ```bash
   uv sync
   ```

3. Run the server:
   ```bash
   uv run python -m hyperliquid_mcp_server.main
   ```

### Docker Installation

1. Clone this repository
2. Build and run with Docker Compose:
   ```bash
   # Production mode
   make build && make run

   # Or using docker-compose directly
   docker-compose up --build
   ```

3. For development with hot reloading:
   ```bash
   # Development mode
   make dev

   # Or using docker-compose directly
   docker-compose --profile dev up --build
   ```

## Configuration

Configure the server using environment variables:

### Required for Trading Operations
- `HYPERLIQUID_PRIVATE_KEY` - Your wallet's private key (with 0x prefix)

### Optional
- `HYPERLIQUID_WALLET_ADDRESS` - Your wallet address (derived from private key if not provided)
- `HYPERLIQUID_TESTNET` - Set to "true" for testnet, "false" or unset for mainnet

### Example Environment Setup

Create a `.env` file (not recommended for production):
```bash
HYPERLIQUID_PRIVATE_KEY=0x1234567890abcdef...
HYPERLIQUID_WALLET_ADDRESS=0xabcdef1234567890...
HYPERLIQUID_TESTNET=true
```

## Usage

### Using Make Commands

The project includes a Makefile for common operations:

```bash
# Install dependencies
make install

# Run locally (without Docker)
make local

# Build Docker image
make build

# Run in production mode
make run

# Run in development mode
make dev

# Run tests
make test

# Format code
make format

# Clean up Docker resources
make clean
```

### Manual Commands

```bash
# Local development
uv run python -m hyperliquid_mcp_server.main

# Docker production
docker-compose up --build

# Docker development
docker-compose --profile dev up --build
```

### With Claude Desktop

Add this server to your Claude Desktop configuration:

#### Local Installation
```json
{
  "mcpServers": {
    "hyperliquid": {
      "command": "uv",
      "args": ["run", "python", "-m", "hyperliquid_mcp_server.main"],
      "cwd": "/path/to/hyperliq-mcp",
      "env": {
        "HYPERLIQUID_PRIVATE_KEY": "0x...",
        "HYPERLIQUID_TESTNET": "true"
      }
    }
  }
}
```

#### Docker Installation
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

## API Reference

### Market Data

#### get_all_mids
Get current mid prices for all coins.
```json
{}
```

#### get_l2_book
Get L2 order book for a specific coin.
```json
{
  "coin": "BTC",
  "nSigFigs": 3
}
```

#### get_candle_snapshot
Get historical candle data.
```json
{
  "coin": "BTC",
  "interval": "1h",
  "startTime": 1640995200000,
  "endTime": 1641081600000
}
```

### Account Information

#### get_open_orders
Get open orders for the configured wallet or a specific user.
```json
{
  "user": "0x..." // optional
}
```

#### get_user_fills
Get trading history.
```json
{
  "user": "0x..." // optional
}
```

#### get_portfolio
Get portfolio information.
```json
{
  "user": "0x..." // optional
}
```

### Trading

#### place_order
Place a limit order.
```json
{
  "assetIndex": 0,
  "isBuy": true,
  "price": "50000",
  "size": "0.1",
  "timeInForce": "Gtc",
  "reduceOnly": false,
  "clientOrderId": "my-order-1"
}
```

#### place_trigger_order
Place a trigger order (stop-loss/take-profit).
```json
{
  "assetIndex": 0,
  "isBuy": false,
  "size": "0.1",
  "triggerPrice": "45000",
  "isMarket": true,
  "triggerType": "sl",
  "reduceOnly": true
}
```

#### cancel_order
Cancel a specific order.
```json
{
  "assetIndex": 0,
  "orderId": 12345
}
```

#### cancel_all_orders
Cancel all open orders.
```json
{}
```

## Security Notes

- Never share your private key
- Use testnet for development and testing
- Consider using environment variables or secure secret management for production
- This server requires your private key to sign trading transactions
- Read-only operations (market data, account info) work without a private key

## Asset Indices

Common asset indices for Hyperliquid:
- BTC: 0
- ETH: 1
- SOL: 2
- (Check Hyperliquid documentation for complete list)

## Error Handling

The server includes comprehensive error handling:
- Invalid configurations are reported on startup
- API errors are caught and returned with descriptive messages
- Network timeouts are handled gracefully
- Input validation prevents malformed requests

## Development

### Project Structure
```
hyperliquid_mcp_server/
├── main.py              # Main MCP server
├── types/
│   └── hyperliquid.py   # Pydantic type definitions
├── utils/
│   ├── hyperliquid_client.py  # API client
│   └── config.py        # Configuration management
└── tools/
    ├── market_data.py   # Market data tools
    ├── account_info.py  # Account information tools
    └── trading.py       # Trading tools
```

### Development Setup
```bash
# Install dependencies
uv sync

# Install with development dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Format code
uv run black .
uv run isort .

# Lint code
uv run ruff check .
uv run mypy .
```

### Docker Development
```bash
# Development mode with hot reloading
make dev

# Shell into container
make shell

# View logs
make logs
```

## License

MIT