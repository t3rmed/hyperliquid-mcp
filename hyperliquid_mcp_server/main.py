"""Main MCP server for Hyperliquid integration."""

import asyncio
import sys
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    ListToolsRequest,
    TextContent,
)

from .tools import (
    # Market data
    get_all_mids_tool,
    get_candle_snapshot_tool,
    get_l2_book_tool,
    handle_get_all_mids,
    handle_get_candle_snapshot,
    handle_get_l2_book,
    # Account info
    get_open_orders_tool,
    get_portfolio_tool,
    get_user_fills_by_time_tool,
    get_user_fills_tool,
    handle_get_open_orders,
    handle_get_portfolio,
    handle_get_user_fills,
    handle_get_user_fills_by_time,
    # Trading
    cancel_all_orders_tool,
    cancel_order_tool,
    handle_cancel_all_orders,
    handle_cancel_order,
    handle_place_order,
    handle_place_trigger_order,
    place_order_tool,
    place_trigger_order_tool,
)
from .utils import HyperliquidClient, get_config, validate_config

# Load environment variables
load_dotenv()

# Initialize configuration and client
config = get_config()
config_errors = validate_config(config)

if config_errors:
    print("Configuration errors:", file=sys.stderr)
    for error in config_errors:
        print(f"- {error}", file=sys.stderr)
    print("\nPlease set the following environment variables:", file=sys.stderr)
    print("- HYPERLIQUID_PRIVATE_KEY (optional, required for trading)", file=sys.stderr)
    print("- HYPERLIQUID_WALLET_ADDRESS (optional, defaults to derived from private key)", file=sys.stderr)
    print("- HYPERLIQUID_TESTNET=true (optional, defaults to mainnet)", file=sys.stderr)

client = HyperliquidClient(config)

# Create the server
app = Server("hyperliquid-mcp-server")


@app.list_tools()
async def list_tools() -> list:
    """List all available tools."""
    return [
        # Market data tools
        get_all_mids_tool,
        get_l2_book_tool,
        get_candle_snapshot_tool,
        # Account info tools
        get_open_orders_tool,
        get_user_fills_tool,
        get_user_fills_by_time_tool,
        get_portfolio_tool,
        # Trading tools
        place_order_tool,
        place_trigger_order_tool,
        cancel_order_tool,
        cancel_all_orders_tool,
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    """Handle tool calls."""
    args = arguments or {}

    try:
        if name == "get_all_mids":
            result = await handle_get_all_mids(client, args)
        elif name == "get_l2_book":
            result = await handle_get_l2_book(client, args)
        elif name == "get_candle_snapshot":
            result = await handle_get_candle_snapshot(client, args)
        elif name == "get_open_orders":
            result = await handle_get_open_orders(client, args)
        elif name == "get_user_fills":
            result = await handle_get_user_fills(client, args)
        elif name == "get_user_fills_by_time":
            result = await handle_get_user_fills_by_time(client, args)
        elif name == "get_portfolio":
            result = await handle_get_portfolio(client, args)
        elif name == "place_order":
            result = await handle_place_order(client, args)
        elif name == "place_trigger_order":
            result = await handle_place_trigger_order(client, args)
        elif name == "cancel_order":
            result = await handle_cancel_order(client, args)
        elif name == "cancel_all_orders":
            result = await handle_cancel_all_orders(client, args)
        else:
            raise ValueError(f"Unknown tool: {name}")

        return result["content"]

    except Exception as error:
        error_message = str(error)
        return [
            TextContent(
                type="text",
                text=f"Error: {error_message}",
            )
        ]


async def main():
    """Main entry point."""
    print(f"Hyperliquid MCP server running on stdio", file=sys.stderr)
    print(f"Configuration: {'Testnet' if config.is_testnet else 'Mainnet'}", file=sys.stderr)
    print(f"Wallet configured: {bool(config.private_key)}", file=sys.stderr)

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())