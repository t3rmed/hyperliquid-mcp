"""Test MCP tools definitions."""

import pytest
from mcp.types import Tool

from hyperliquid_mcp_server.tools.market_data import (
    get_all_mids_tool,
    get_l2_book_tool,
    get_candle_snapshot_tool,
)
from hyperliquid_mcp_server.tools.account_info import (
    get_open_orders_tool,
    get_user_fills_tool,
    get_portfolio_tool,
)
from hyperliquid_mcp_server.tools.trading import (
    place_order_tool,
    cancel_order_tool,
    cancel_all_orders_tool,
)


class TestToolDefinitions:
    """Test MCP tool definitions."""

    def test_all_tools_are_tool_instances(self):
        """Test that all tool definitions are proper Tool instances."""
        tools = [
            get_all_mids_tool,
            get_l2_book_tool,
            get_candle_snapshot_tool,
            get_open_orders_tool,
            get_user_fills_tool,
            get_portfolio_tool,
            place_order_tool,
            cancel_order_tool,
            cancel_all_orders_tool,
        ]

        for tool in tools:
            assert isinstance(tool, Tool)
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'inputSchema')

    def test_tool_names_are_unique(self):
        """Test that all tool names are unique."""
        tools = [
            get_all_mids_tool,
            get_l2_book_tool,
            get_candle_snapshot_tool,
            get_open_orders_tool,
            get_user_fills_tool,
            get_portfolio_tool,
            place_order_tool,
            cancel_order_tool,
            cancel_all_orders_tool,
        ]

        names = [tool.name for tool in tools]
        assert len(names) == len(set(names)), "Tool names must be unique"

    def test_get_all_mids_tool(self):
        """Test get_all_mids tool definition."""
        tool = get_all_mids_tool

        assert tool.name == "get_all_mids"
        assert "mid prices" in tool.description.lower()
        assert tool.inputSchema["type"] == "object"
        assert tool.inputSchema["required"] == []

    def test_get_l2_book_tool(self):
        """Test get_l2_book tool definition."""
        tool = get_l2_book_tool

        assert tool.name == "get_l2_book"
        assert "order book" in tool.description.lower()
        assert "coin" in tool.inputSchema["properties"]
        assert "coin" in tool.inputSchema["required"]
        assert "nSigFigs" in tool.inputSchema["properties"]

    def test_get_candle_snapshot_tool(self):
        """Test get_candle_snapshot tool definition."""
        tool = get_candle_snapshot_tool

        assert tool.name == "get_candle_snapshot"
        assert "candle" in tool.description.lower()
        assert "coin" in tool.inputSchema["properties"]
        assert "interval" in tool.inputSchema["properties"]
        assert "coin" in tool.inputSchema["required"]
        assert "interval" in tool.inputSchema["required"]

        # Check interval enum values
        interval_enum = tool.inputSchema["properties"]["interval"]["enum"]
        expected_intervals = ["1m", "5m", "15m", "1h", "4h", "1d", "1w", "1M"]
        for interval in expected_intervals:
            assert interval in interval_enum

    def test_place_order_tool(self):
        """Test place_order tool definition."""
        tool = place_order_tool

        assert tool.name == "place_order"
        assert "place" in tool.description.lower()
        assert "order" in tool.description.lower()

        required_fields = tool.inputSchema["required"]
        assert "assetIndex" in required_fields
        assert "isBuy" in required_fields
        assert "price" in required_fields
        assert "size" in required_fields
        assert "timeInForce" in required_fields

        # Check timeInForce enum
        tif_enum = tool.inputSchema["properties"]["timeInForce"]["enum"]
        assert "Gtc" in tif_enum
        assert "Ioc" in tif_enum
        assert "Alo" in tif_enum

    def test_cancel_order_tool(self):
        """Test cancel_order tool definition."""
        tool = cancel_order_tool

        assert tool.name == "cancel_order"
        assert "cancel" in tool.description.lower()

        required_fields = tool.inputSchema["required"]
        assert "assetIndex" in required_fields

        # Should have either orderId or clientOrderId
        properties = tool.inputSchema["properties"]
        assert "orderId" in properties
        assert "clientOrderId" in properties

    def test_cancel_all_orders_tool(self):
        """Test cancel_all_orders tool definition."""
        tool = cancel_all_orders_tool

        assert tool.name == "cancel_all_orders"
        assert "cancel" in tool.description.lower()
        assert "all" in tool.description.lower()
        assert tool.inputSchema["required"] == []  # No parameters required

    def test_account_tools_have_optional_user_param(self):
        """Test that account info tools have optional user parameter."""
        account_tools = [
            get_open_orders_tool,
            get_user_fills_tool,
            get_portfolio_tool,
        ]

        for tool in account_tools:
            properties = tool.inputSchema["properties"]
            if "user" in properties:
                # If user param exists, it should be optional
                assert "user" not in tool.inputSchema["required"]
                assert properties["user"]["type"] == "string"

    def test_trading_tools_have_asset_index(self):
        """Test that trading tools have assetIndex parameter."""
        trading_tools = [place_order_tool, cancel_order_tool]

        for tool in trading_tools:
            properties = tool.inputSchema["properties"]
            assert "assetIndex" in properties
            assert properties["assetIndex"]["type"] == "number"

    def test_tool_descriptions_are_descriptive(self):
        """Test that tool descriptions are meaningful."""
        tools = [
            get_all_mids_tool,
            get_l2_book_tool,
            get_candle_snapshot_tool,
            get_open_orders_tool,
            get_user_fills_tool,
            get_portfolio_tool,
            place_order_tool,
            cancel_order_tool,
            cancel_all_orders_tool,
        ]

        for tool in tools:
            # Description should be at least 10 characters and contain relevant keywords
            assert len(tool.description) >= 10
            assert any(keyword in tool.description.lower() for keyword in [
                "get", "place", "cancel", "order", "price", "book", "candle", "fill", "portfolio"
            ])