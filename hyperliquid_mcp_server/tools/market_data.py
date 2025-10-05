"""Market data tools for Hyperliquid MCP server."""

import json
from typing import Any, Dict

from mcp.types import Tool, TextContent

from ..utils.hyperliquid_client import HyperliquidClient


get_all_mids_tool = Tool(
    name="get_all_mids",
    description="Get current mid prices for all coins on Hyperliquid",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": [],
    },
)

get_l2_book_tool = Tool(
    name="get_l2_book",
    description="Get L2 order book snapshot for a specific coin",
    inputSchema={
        "type": "object",
        "properties": {
            "coin": {
                "type": "string",
                "description": "The coin symbol (e.g., BTC, ETH, SOL)",
            },
            "nSigFigs": {
                "type": "number",
                "description": "Number of significant figures for price aggregation (optional)",
                "minimum": 1,
                "maximum": 5,
            },
        },
        "required": ["coin"],
    },
)

get_candle_snapshot_tool = Tool(
    name="get_candle_snapshot",
    description="Get historical candle data for a specific coin",
    inputSchema={
        "type": "object",
        "properties": {
            "coin": {
                "type": "string",
                "description": "The coin symbol (e.g., BTC, ETH, SOL)",
            },
            "interval": {
                "type": "string",
                "description": "Candle interval",
                "enum": ["1m", "5m", "15m", "1h", "4h", "1d", "1w", "1M"],
            },
            "startTime": {
                "type": "number",
                "description": "Start time in milliseconds (optional)",
            },
            "endTime": {
                "type": "number",
                "description": "End time in milliseconds (optional)",
            },
        },
        "required": ["coin", "interval"],
    },
)


async def handle_get_all_mids(client: HyperliquidClient, args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get all mids request."""
    result = await client.get_all_mids()

    if not result.success:
        raise ValueError(f"Failed to get mid prices: {result.error}")

    return {
        "content": [
            TextContent(
                type="text",
                text=f"Mid prices for all coins:\n{json.dumps(result.data, indent=2)}",
            )
        ]
    }


async def handle_get_l2_book(client: HyperliquidClient, args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get L2 book request."""
    coin = args["coin"]
    n_sig_figs = args.get("nSigFigs")

    result = await client.get_l2_book(coin, n_sig_figs)

    if not result.success:
        raise ValueError(f"Failed to get L2 book for {coin}: {result.error}")

    book = result.data
    bids = book.get("levels", [[], []])[0] if book else []
    asks = book.get("levels", [[], []])[1] if book else []

    bids_text = "\n".join(f"{b['px']} @ {b['sz']}" for b in bids)
    asks_text = "\n".join(f"{a['px']} @ {a['sz']}" for a in asks)

    return {
        "content": [
            TextContent(
                type="text",
                text=f"L2 Order Book for {coin}:\n\nBids ({len(bids)} levels):\n{bids_text}\n\nAsks ({len(asks)} levels):\n{asks_text}",
            )
        ]
    }


async def handle_get_candle_snapshot(client: HyperliquidClient, args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get candle snapshot request."""
    coin = args["coin"]
    interval = args["interval"]
    start_time = args.get("startTime")
    end_time = args.get("endTime")

    result = await client.get_candle_snapshot(coin, interval, start_time, end_time)

    if not result.success:
        raise ValueError(f"Failed to get candle data for {coin}: {result.error}")

    candles = result.data.get("candles", []) if result.data else []

    candle_text = "\n".join(
        f"{candle['t']}: O:{candle['o']} H:{candle['h']} L:{candle['l']} C:{candle['c']} V:{candle['v']}"
        for candle in candles
    )

    return {
        "content": [
            TextContent(
                type="text",
                text=f"Candle data for {coin} ({interval}):\n{candle_text}",
            )
        ]
    }