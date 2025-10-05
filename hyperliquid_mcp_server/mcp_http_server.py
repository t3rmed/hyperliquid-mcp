"""Proper MCP JSON-RPC HTTP server for n8n and other MCP clients."""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
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
mcp_app = FastAPI(
    title="Hyperliquid MCP Server (JSON-RPC)",
    description="MCP JSON-RPC server for Hyperliquid trading",
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


class MCPResponse:
    """MCP JSON-RPC response builder."""

    @staticmethod
    def success(id: Any, result: Any) -> Dict:
        return {
            "jsonrpc": "2.0",
            "id": id,
            "result": result
        }

    @staticmethod
    def error(id: Any, code: int, message: str, data: Any = None) -> Dict:
        error_obj = {"code": code, "message": message}
        if data is not None:
            error_obj["data"] = data
        return {
            "jsonrpc": "2.0",
            "id": id,
            "error": error_obj
        }


@mcp_app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "hyperliquid-mcp-server",
        "version": "1.0.0",
        "protocol": "MCP JSON-RPC 2.0",
        "testnet": config.is_testnet,
        "wallet_configured": bool(config.private_key)
    }


@mcp_app.post("/")
async def mcp_handler(request: Request):
    """Main MCP JSON-RPC endpoint."""
    try:
        body = await request.json()

        # Validate JSON-RPC request
        if not isinstance(body, dict):
            return JSONResponse(
                MCPResponse.error(None, -32600, "Invalid Request: not a JSON object"),
                status_code=400
            )

        if body.get("jsonrpc") != "2.0":
            return JSONResponse(
                MCPResponse.error(body.get("id"), -32600, "Invalid Request: missing or invalid jsonrpc"),
                status_code=400
            )

        method = body.get("method")
        if not method:
            return JSONResponse(
                MCPResponse.error(body.get("id"), -32600, "Invalid Request: missing method"),
                status_code=400
            )

        request_id = body.get("id")
        params = body.get("params", {})

        # Handle MCP methods
        if method == "initialize":
            return JSONResponse(MCPResponse.success(request_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                },
                "serverInfo": {
                    "name": "hyperliquid-mcp-server",
                    "version": "1.0.0"
                }
            }))

        elif method == "initialized":
            # Notification - no response needed
            return JSONResponse({"jsonrpc": "2.0"})

        elif method == "tools/list":
            tools_list = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in ALL_TOOLS
            ]
            return JSONResponse(MCPResponse.success(request_id, {"tools": tools_list}))

        elif method == "tools/call":
            tool_name = params.get("name")
            if not tool_name:
                return JSONResponse(
                    MCPResponse.error(request_id, -32602, "Invalid params: missing tool name"),
                    status_code=400
                )

            if tool_name not in TOOL_HANDLERS:
                return JSONResponse(
                    MCPResponse.error(request_id, -32601, f"Method not found: tool '{tool_name}' not available"),
                    status_code=404
                )

            try:
                handler = TOOL_HANDLERS[tool_name]
                arguments = params.get("arguments", {})
                result = await handler(client, arguments)

                return JSONResponse(MCPResponse.success(request_id, {
                    "content": result["content"]
                }))

            except Exception as e:
                return JSONResponse(
                    MCPResponse.error(request_id, -32603, f"Internal error: {str(e)}"),
                    status_code=500
                )

        else:
            return JSONResponse(
                MCPResponse.error(request_id, -32601, f"Method not found: {method}"),
                status_code=404
            )

    except json.JSONDecodeError:
        return JSONResponse(
            MCPResponse.error(None, -32700, "Parse error: invalid JSON"),
            status_code=400
        )
    except Exception as e:
        return JSONResponse(
            MCPResponse.error(None, -32603, f"Internal error: {str(e)}"),
            status_code=500
        )


@mcp_app.get("/tools")
async def list_tools_rest():
    """REST endpoint for tools list (for debugging)."""
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


@mcp_app.get("/sse")
async def sse_endpoint(request: Request):
    """Server-Sent Events MCP endpoint for n8n."""
    async def mcp_sse_stream():
        try:
            # Send MCP server info immediately upon connection
            server_info = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "hyperliquid-mcp-server",
                        "version": "1.0.0"
                    }
                }
            }
            yield f"data: {json.dumps(server_info)}\n\n"

            # Send tools list
            tools_list = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in ALL_TOOLS
            ]

            tools_response = {
                "jsonrpc": "2.0",
                "method": "notifications/tools/list",
                "params": {"tools": tools_list}
            }
            yield f"data: {json.dumps(tools_response)}\n\n"

            # Keep connection alive with heartbeat
            while True:
                await asyncio.sleep(30)
                heartbeat = {
                    "jsonrpc": "2.0",
                    "method": "notifications/ping",
                    "params": {"timestamp": int(asyncio.get_event_loop().time())}
                }
                yield f"data: {json.dumps(heartbeat)}\n\n"

        except asyncio.CancelledError:
            # Client disconnected
            break
        except Exception as e:
            error_msg = {
                "jsonrpc": "2.0",
                "method": "notifications/error",
                "params": {"error": str(e)}
            }
            yield f"data: {json.dumps(error_msg)}\n\n"

    return StreamingResponse(
        mcp_sse_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control, Accept, Accept-Encoding, Authorization",
            "Access-Control-Allow-Methods": "GET, OPTIONS"
        }
    )


@mcp_app.post("/sse/execute")
async def sse_tool_execute(request: Request):
    """Execute tool for SSE clients."""
    try:
        body = await request.json()

        tool_name = body.get("tool")
        arguments = body.get("arguments", {})
        request_id = body.get("id", "sse-request")

        if not tool_name:
            return JSONResponse(
                {"error": "Missing tool name"},
                status_code=400,
                headers={"Access-Control-Allow-Origin": "*"}
            )

        if tool_name not in TOOL_HANDLERS:
            return JSONResponse(
                {"error": f"Tool '{tool_name}' not found"},
                status_code=404,
                headers={"Access-Control-Allow-Origin": "*"}
            )

        # Execute the tool
        handler = TOOL_HANDLERS[tool_name]
        result = await handler(client, arguments)

        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": result["content"]
            }
        }

        return JSONResponse(
            response,
            headers={"Access-Control-Allow-Origin": "*"}
        )

    except Exception as e:
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": body.get("id", "sse-request") if 'body' in locals() else "unknown",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            },
            status_code=500,
            headers={"Access-Control-Allow-Origin": "*"}
        )


@mcp_app.options("/")
@mcp_app.options("/sse")
@mcp_app.options("/sse/execute")
@mcp_app.options("/stream")
async def cors_preflight():
    """Handle CORS preflight requests."""
    return JSONResponse(
        {},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Cache-Control, Accept, Accept-Encoding",
            "Access-Control-Max-Age": "86400"
        }
    )


@mcp_app.post("/stream")
async def mcp_stream_handler(request: Request):
    """Streaming MCP handler for httpStreamable transport."""
    try:
        body = await request.json()

        # Process the same way as regular MCP handler
        if not isinstance(body, dict):
            return JSONResponse(
                MCPResponse.error(None, -32600, "Invalid Request: not a JSON object"),
                status_code=400,
                headers={"Access-Control-Allow-Origin": "*"}
            )

        if body.get("jsonrpc") != "2.0":
            return JSONResponse(
                MCPResponse.error(body.get("id"), -32600, "Invalid Request: missing or invalid jsonrpc"),
                status_code=400,
                headers={"Access-Control-Allow-Origin": "*"}
            )

        method = body.get("method")
        if not method:
            return JSONResponse(
                MCPResponse.error(body.get("id"), -32600, "Invalid Request: missing method"),
                status_code=400,
                headers={"Access-Control-Allow-Origin": "*"}
            )

        request_id = body.get("id")
        params = body.get("params", {})

        # Handle MCP methods (same logic as main handler)
        if method == "initialize":
            response = MCPResponse.success(request_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                },
                "serverInfo": {
                    "name": "hyperliquid-mcp-server",
                    "version": "1.0.0"
                }
            })
            return JSONResponse(response, headers={"Access-Control-Allow-Origin": "*"})

        elif method == "initialized":
            return JSONResponse({"jsonrpc": "2.0"}, headers={"Access-Control-Allow-Origin": "*"})

        elif method == "tools/list":
            tools_list = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in ALL_TOOLS
            ]
            response = MCPResponse.success(request_id, {"tools": tools_list})
            return JSONResponse(response, headers={"Access-Control-Allow-Origin": "*"})

        elif method == "tools/call":
            tool_name = params.get("name")
            if not tool_name:
                return JSONResponse(
                    MCPResponse.error(request_id, -32602, "Invalid params: missing tool name"),
                    status_code=400,
                    headers={"Access-Control-Allow-Origin": "*"}
                )

            if tool_name not in TOOL_HANDLERS:
                return JSONResponse(
                    MCPResponse.error(request_id, -32601, f"Method not found: tool '{tool_name}' not available"),
                    status_code=404,
                    headers={"Access-Control-Allow-Origin": "*"}
                )

            try:
                handler = TOOL_HANDLERS[tool_name]
                arguments = params.get("arguments", {})
                result = await handler(client, arguments)

                response = MCPResponse.success(request_id, {
                    "content": result["content"]
                })
                return JSONResponse(response, headers={"Access-Control-Allow-Origin": "*"})

            except Exception as e:
                return JSONResponse(
                    MCPResponse.error(request_id, -32603, f"Internal error: {str(e)}"),
                    status_code=500,
                    headers={"Access-Control-Allow-Origin": "*"}
                )

        else:
            return JSONResponse(
                MCPResponse.error(request_id, -32601, f"Method not found: {method}"),
                status_code=404,
                headers={"Access-Control-Allow-Origin": "*"}
            )

    except json.JSONDecodeError:
        return JSONResponse(
            MCPResponse.error(None, -32700, "Parse error: invalid JSON"),
            status_code=400,
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except Exception as e:
        return JSONResponse(
            MCPResponse.error(None, -32603, f"Internal error: {str(e)}"),
            status_code=500,
            headers={"Access-Control-Allow-Origin": "*"}
        )


def main():
    """Run MCP HTTP server."""
    port = int(os.environ.get("PORT", 8000))
    run(mcp_app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()