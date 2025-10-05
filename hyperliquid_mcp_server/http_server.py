"""HTTP wrapper for Hyperliquid MCP server to enable cloud deployment."""

import asyncio
import json
import os
import sys
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
from uvicorn import run

from .utils import HyperliquidClient, get_config
from .tools import (
    # Market data tools
    get_all_mids_tool, get_l2_book_tool, get_candle_snapshot_tool,
    handle_get_all_mids, handle_get_l2_book, handle_get_candle_snapshot,
    # Account info tools
    get_open_orders_tool, get_user_fills_tool, get_user_fills_by_time_tool, get_portfolio_tool,
    handle_get_open_orders, handle_get_user_fills, handle_get_user_fills_by_time, handle_get_portfolio,
    # Trading tools
    place_order_tool, place_trigger_order_tool, cancel_order_tool, cancel_all_orders_tool,
    handle_place_order, handle_place_trigger_order, handle_cancel_order, handle_cancel_all_orders,
)

# Create FastAPI app
http_app = FastAPI(
    title="Hyperliquid MCP Server",
    description="HTTP wrapper for Hyperliquid MCP server",
    version="1.0.0"
)

config = get_config()
client = HyperliquidClient(config)

# Define all available tools
ALL_TOOLS = [
    get_all_mids_tool, get_l2_book_tool, get_candle_snapshot_tool,
    get_open_orders_tool, get_user_fills_tool, get_user_fills_by_time_tool, get_portfolio_tool,
    place_order_tool, place_trigger_order_tool, cancel_order_tool, cancel_all_orders_tool,
]

# Map tool names to handlers
TOOL_HANDLERS = {
    "get_all_mids": handle_get_all_mids,
    "get_l2_book": handle_get_l2_book,
    "get_candle_snapshot": handle_get_candle_snapshot,
    "get_open_orders": handle_get_open_orders,
    "get_user_fills": handle_get_user_fills,
    "get_user_fills_by_time": handle_get_user_fills_by_time,
    "get_portfolio": handle_get_portfolio,
    "place_order": handle_place_order,
    "place_trigger_order": handle_place_trigger_order,
    "cancel_order": handle_cancel_order,
    "cancel_all_orders": handle_cancel_all_orders,
}


@http_app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "hyperliquid-mcp-server",
        "version": "1.0.0",
        "testnet": config.is_testnet,
        "wallet_configured": bool(config.private_key)
    }


@http_app.get("/tools")
async def list_tools():
    """List all available MCP tools."""
    try:
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in ALL_TOOLS
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@http_app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, arguments: Dict[str, Any] = Body(default={})):
    """Call a specific MCP tool."""
    try:
        if tool_name not in TOOL_HANDLERS:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

        handler = TOOL_HANDLERS[tool_name]
        result = await handler(client, arguments)

        return {
            "tool": tool_name,
            "arguments": arguments,
            "result": [
                {
                    "type": content.type,
                    "text": content.text
                }
                for content in result["content"]
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@http_app.get("/docs")
async def get_docs():
    """Get API documentation."""
    return {
        "service": "Hyperliquid MCP Server",
        "description": "HTTP API for Hyperliquid trading operations",
        "endpoints": {
            "GET /": "Health check",
            "GET /tools": "List all available tools",
            "POST /tools/{tool_name}": "Execute a tool with arguments",
            "GET /docs": "This documentation"
        },
        "available_tools": [
            "get_all_mids - Get current prices",
            "get_l2_book - Get order book",
            "get_candle_snapshot - Get price history",
            "get_open_orders - Get open orders",
            "get_user_fills - Get trading history",
            "get_portfolio - Get portfolio info",
            "place_order - Place limit order",
            "place_trigger_order - Place stop/take profit",
            "cancel_order - Cancel specific order",
            "cancel_all_orders - Cancel all orders"
        ],
        "example_usage": {
            "get_prices": "POST /tools/get_all_mids",
            "get_orderbook": "POST /tools/get_l2_book with {'coin': 'BTC'}",
            "place_order": "POST /tools/place_order with order parameters"
        }
    }


def main():
    """Run HTTP server."""
    port = int(os.environ.get("PORT", 8000))
    run(http_app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()