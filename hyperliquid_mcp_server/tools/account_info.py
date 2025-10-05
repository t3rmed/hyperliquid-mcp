"""Account information tools for Hyperliquid MCP server."""

from datetime import datetime
from typing import Any, Dict

from mcp.types import Tool, TextContent

from ..utils.hyperliquid_client import HyperliquidClient


get_open_orders_tool = Tool(
    name="get_open_orders",
    description="Get all open orders for the configured wallet or a specific user",
    inputSchema={
        "type": "object",
        "properties": {
            "user": {
                "type": "string",
                "description": "User wallet address (optional, defaults to configured wallet)",
            }
        },
        "required": [],
    },
)

get_user_fills_tool = Tool(
    name="get_user_fills",
    description="Get trading history (fills) for the configured wallet or a specific user",
    inputSchema={
        "type": "object",
        "properties": {
            "user": {
                "type": "string",
                "description": "User wallet address (optional, defaults to configured wallet)",
            }
        },
        "required": [],
    },
)

get_user_fills_by_time_tool = Tool(
    name="get_user_fills_by_time",
    description="Get trading history (fills) for a specific time range",
    inputSchema={
        "type": "object",
        "properties": {
            "user": {
                "type": "string",
                "description": "User wallet address (optional, defaults to configured wallet)",
            },
            "startTime": {
                "type": "number",
                "description": "Start time in milliseconds",
            },
            "endTime": {
                "type": "number",
                "description": "End time in milliseconds",
            },
        },
        "required": [],
    },
)

get_portfolio_tool = Tool(
    name="get_portfolio",
    description="Get portfolio information including positions, PnL, and margin usage",
    inputSchema={
        "type": "object",
        "properties": {
            "user": {
                "type": "string",
                "description": "User wallet address (optional, defaults to configured wallet)",
            }
        },
        "required": [],
    },
)


async def handle_get_open_orders(client: HyperliquidClient, args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get open orders request."""
    user = args.get("user")
    result = await client.get_open_orders(user)

    if not result.success:
        raise ValueError(f"Failed to get open orders: {result.error}")

    orders = result.data or []

    if not orders:
        return {
            "content": [
                TextContent(
                    type="text",
                    text="No open orders found.",
                )
            ]
        }

    orders_text = "\n".join(
        f"{order['coin']} {'BUY' if order['side'] == 'B' else 'SELL'} {order['sz']} @ {order['px']} (ID: {order['oid']})"
        for order in orders
    )

    return {
        "content": [
            TextContent(
                type="text",
                text=f"Open Orders ({len(orders)}):\n\n{orders_text}",
            )
        ]
    }


async def handle_get_user_fills(client: HyperliquidClient, args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get user fills request."""
    user = args.get("user")
    result = await client.get_user_fills(user)

    if not result.success:
        raise ValueError(f"Failed to get user fills: {result.error}")

    fills = result.data or []

    if not fills:
        return {
            "content": [
                TextContent(
                    type="text",
                    text="No trading history found.",
                )
            ]
        }

    # Show first 20 fills
    display_fills = fills[:20]
    fills_text = "\n".join(
        f"{datetime.fromtimestamp(fill['time'] / 1000).isoformat()}: {fill['coin']} {'BUY' if fill['side'] == 'B' else 'SELL'} {fill['sz']} @ {fill['px']} (Fee: {fill['fee']})"
        for fill in display_fills
    )

    more_text = f"\n... and {len(fills) - 20} more" if len(fills) > 20 else ""

    return {
        "content": [
            TextContent(
                type="text",
                text=f"Trading History ({len(fills)} fills):\n\n{fills_text}{more_text}",
            )
        ]
    }


async def handle_get_user_fills_by_time(client: HyperliquidClient, args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get user fills by time request."""
    user = args.get("user")
    start_time = args.get("startTime")
    end_time = args.get("endTime")

    result = await client.get_user_fills_by_time(user, start_time, end_time)

    if not result.success:
        raise ValueError(f"Failed to get user fills by time: {result.error}")

    fills = result.data or []

    if not fills:
        return {
            "content": [
                TextContent(
                    type="text",
                    text="No trading history found for the specified time range.",
                )
            ]
        }

    fills_text = "\n".join(
        f"{datetime.fromtimestamp(fill['time'] / 1000).isoformat()}: {fill['coin']} {'BUY' if fill['side'] == 'B' else 'SELL'} {fill['sz']} @ {fill['px']} (Fee: {fill['fee']})"
        for fill in fills
    )

    return {
        "content": [
            TextContent(
                type="text",
                text=f"Trading History ({len(fills)} fills):\n\n{fills_text}",
            )
        ]
    }


async def handle_get_portfolio(client: HyperliquidClient, args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get portfolio request."""
    user = args.get("user")
    result = await client.get_portfolio(user)

    if not result.success:
        raise ValueError(f"Failed to get portfolio: {result.error}")

    portfolio = result.data

    if not portfolio:
        return {
            "content": [
                TextContent(
                    type="text",
                    text="No portfolio data found.",
                )
            ]
        }

    last_updated = (
        datetime.fromtimestamp(portfolio["time"] / 1000).isoformat()
        if portfolio.get("time")
        else "N/A"
    )

    return {
        "content": [
            TextContent(
                type="text",
                text=f"Portfolio Summary:\n\nTotal Notional Position: ${portfolio.get('totalNtlPos', '0')}\nTotal Unrealized PnL: ${portfolio.get('totalUnrealizedPnl', '0')}\nTotal Margin Used: ${portfolio.get('totalMarginUsed', '0')}\nLast Updated: {last_updated}",
            )
        ]
    }