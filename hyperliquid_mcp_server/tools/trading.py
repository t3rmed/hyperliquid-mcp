"""Trading tools for Hyperliquid MCP server."""

import json
from typing import Any, Dict

from mcp.types import Tool, TextContent

from ..types.hyperliquid import (
    CancelOrderAction,
    CancelOrderItem,
    LimitOrderType,
    OrderRequest,
    PlaceOrderAction,
    TriggerOrderType,
)
from ..utils.hyperliquid_client import HyperliquidClient


place_order_tool = Tool(
    name="place_order",
    description="Place a limit or trigger order on Hyperliquid",
    inputSchema={
        "type": "object",
        "properties": {
            "assetIndex": {
                "type": "number",
                "description": "Asset index for the coin (0 for BTC, 1 for ETH, etc.)",
            },
            "isBuy": {
                "type": "boolean",
                "description": "True for buy order, false for sell order",
            },
            "price": {
                "type": "string",
                "description": "Order price as string",
            },
            "size": {
                "type": "string",
                "description": "Order size as string",
            },
            "reduceOnly": {
                "type": "boolean",
                "description": "Whether this is a reduce-only order (optional, default false)",
            },
            "timeInForce": {
                "type": "string",
                "description": "Time in force",
                "enum": ["Gtc", "Ioc", "Alo"],
            },
            "clientOrderId": {
                "type": "string",
                "description": "Client order ID (optional)",
            },
        },
        "required": ["assetIndex", "isBuy", "price", "size", "timeInForce"],
    },
)

place_trigger_order_tool = Tool(
    name="place_trigger_order",
    description="Place a trigger order (stop-loss or take-profit) on Hyperliquid",
    inputSchema={
        "type": "object",
        "properties": {
            "assetIndex": {
                "type": "number",
                "description": "Asset index for the coin (0 for BTC, 1 for ETH, etc.)",
            },
            "isBuy": {
                "type": "boolean",
                "description": "True for buy order, false for sell order",
            },
            "size": {
                "type": "string",
                "description": "Order size as string",
            },
            "triggerPrice": {
                "type": "string",
                "description": "Trigger price as string",
            },
            "isMarket": {
                "type": "boolean",
                "description": "Whether to execute as market order when triggered",
            },
            "triggerType": {
                "type": "string",
                "description": "Trigger type",
                "enum": ["tp", "sl"],
            },
            "reduceOnly": {
                "type": "boolean",
                "description": "Whether this is a reduce-only order (optional, default false)",
            },
            "clientOrderId": {
                "type": "string",
                "description": "Client order ID (optional)",
            },
        },
        "required": ["assetIndex", "isBuy", "size", "triggerPrice", "isMarket", "triggerType"],
    },
)

cancel_order_tool = Tool(
    name="cancel_order",
    description="Cancel a specific order by order ID or client order ID",
    inputSchema={
        "type": "object",
        "properties": {
            "assetIndex": {
                "type": "number",
                "description": "Asset index for the coin",
            },
            "orderId": {
                "type": "number",
                "description": "Order ID to cancel (use either orderId or clientOrderId)",
            },
            "clientOrderId": {
                "type": "string",
                "description": "Client order ID to cancel (use either orderId or clientOrderId)",
            },
        },
        "required": ["assetIndex"],
    },
)

cancel_all_orders_tool = Tool(
    name="cancel_all_orders",
    description="Cancel all open orders",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": [],
    },
)


async def handle_place_order(client: HyperliquidClient, args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle place order request."""
    asset_index = args["assetIndex"]
    is_buy = args["isBuy"]
    price = args["price"]
    size = args["size"]
    reduce_only = args.get("reduceOnly", False)
    time_in_force = args["timeInForce"]
    client_order_id = args.get("clientOrderId")

    order = OrderRequest(
        a=asset_index,
        b=is_buy,
        p=price,
        s=size,
        r=reduce_only,
        t={"limit": LimitOrderType(tif=time_in_force)},
    )

    if client_order_id:
        order.c = client_order_id

    action = PlaceOrderAction(orders=[order])
    result = await client.place_order(action)

    if not result.success:
        raise ValueError(f"Failed to place order: {result.error}")

    return {
        "content": [
            TextContent(
                type="text",
                text=f"Order placed successfully!\n\n{json.dumps(result.data, indent=2)}",
            )
        ]
    }


async def handle_place_trigger_order(client: HyperliquidClient, args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle place trigger order request."""
    asset_index = args["assetIndex"]
    is_buy = args["isBuy"]
    size = args["size"]
    trigger_price = args["triggerPrice"]
    is_market = args["isMarket"]
    trigger_type = args["triggerType"]
    reduce_only = args.get("reduceOnly", False)
    client_order_id = args.get("clientOrderId")

    order = OrderRequest(
        a=asset_index,
        b=is_buy,
        p="0",  # Not used for trigger orders
        s=size,
        r=reduce_only,
        t={
            "trigger": TriggerOrderType(
                triggerPx=trigger_price,
                isMarket=is_market,
                tpsl=trigger_type,
            )
        },
    )

    if client_order_id:
        order.c = client_order_id

    action = PlaceOrderAction(orders=[order])
    result = await client.place_order(action)

    if not result.success:
        raise ValueError(f"Failed to place trigger order: {result.error}")

    return {
        "content": [
            TextContent(
                type="text",
                text=f"Trigger order placed successfully!\n\n{json.dumps(result.data, indent=2)}",
            )
        ]
    }


async def handle_cancel_order(client: HyperliquidClient, args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle cancel order request."""
    asset_index = args["assetIndex"]
    order_id = args.get("orderId")
    client_order_id = args.get("clientOrderId")

    if not order_id and not client_order_id:
        raise ValueError("Either orderId or clientOrderId must be provided")

    cancel_item = CancelOrderItem(a=asset_index)
    if order_id:
        cancel_item.o = order_id
    else:
        cancel_item.c = client_order_id

    action = CancelOrderAction(cancels=[cancel_item])
    result = await client.cancel_order(action)

    if not result.success:
        raise ValueError(f"Failed to cancel order: {result.error}")

    return {
        "content": [
            TextContent(
                type="text",
                text=f"Order cancelled successfully!\n\n{json.dumps(result.data, indent=2)}",
            )
        ]
    }


async def handle_cancel_all_orders(client: HyperliquidClient, args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle cancel all orders request."""
    result = await client.cancel_all_orders()

    if not result.success:
        raise ValueError(f"Failed to cancel all orders: {result.error}")

    return {
        "content": [
            TextContent(
                type="text",
                text=f"All orders cancelled successfully!\n\n{json.dumps(result.data, indent=2)}",
            )
        ]
    }