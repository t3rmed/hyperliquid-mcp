"""HTTP wrapper for Hyperliquid MCP server to enable cloud deployment."""

import asyncio
import json
import os
import sys
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from uvicorn import run

from .main import app as mcp_app
from .utils import get_config

# Create FastAPI app
http_app = FastAPI(
    title="Hyperliquid MCP Server",
    description="HTTP wrapper for Hyperliquid MCP server",
    version="1.0.0"
)

config = get_config()


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
        tools = await mcp_app.list_tools()
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in tools
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@http_app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, arguments: Dict[str, Any] = None):
    """Call a specific MCP tool."""
    try:
        result = await mcp_app.call_tool(tool_name, arguments or {})
        return {
            "tool": tool_name,
            "arguments": arguments,
            "result": [
                {
                    "type": content.type,
                    "text": content.text
                }
                for content in result
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