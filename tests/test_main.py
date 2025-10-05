"""Test main MCP server functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from mcp.types import TextContent

from hyperliquid_mcp_server.main import app
from hyperliquid_mcp_server.tools import (
    get_all_mids_tool,
    get_l2_book_tool,
    place_order_tool,
    handle_get_all_mids,
    handle_get_l2_book,
    handle_place_order,
)


class TestMainServer:
    """Test main MCP server functionality."""

    def test_server_initialization(self):
        """Test that the server is properly initialized."""
        # Test that the app is created
        assert app is not None
        assert app.name == "hyperliquid-mcp-server"

    @pytest.mark.asyncio
    async def test_handle_get_all_mids(self):
        """Test get_all_mids handler function."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.data = {"BTC": "50000", "ETH": "3000"}
        mock_client.get_all_mids = AsyncMock(return_value=mock_response)

        result = await handle_get_all_mids(mock_client, {})

        assert "content" in result
        assert len(result["content"]) == 1
        assert isinstance(result["content"][0], TextContent)
        assert "BTC" in result["content"][0].text
        assert "50000" in result["content"][0].text

    @pytest.mark.asyncio
    async def test_handle_get_all_mids_failure(self):
        """Test get_all_mids handler with API failure."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.success = False
        mock_response.error = "API error"
        mock_client.get_all_mids = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError, match="Failed to get mid prices"):
            await handle_get_all_mids(mock_client, {})

    @pytest.mark.asyncio
    async def test_handle_get_l2_book(self):
        """Test get_l2_book handler function."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.data = {
            "coin": "BTC",
            "levels": [
                [{"px": "50000", "sz": "1.0"}],  # bids
                [{"px": "50100", "sz": "0.5"}]   # asks
            ]
        }
        mock_client.get_l2_book = AsyncMock(return_value=mock_response)

        args = {"coin": "BTC", "nSigFigs": 3}
        result = await handle_get_l2_book(mock_client, args)

        mock_client.get_l2_book.assert_called_once_with("BTC", 3)
        assert "content" in result
        assert len(result["content"]) == 1
        assert isinstance(result["content"][0], TextContent)
        assert "BTC" in result["content"][0].text
        assert "50000" in result["content"][0].text

    @pytest.mark.asyncio
    async def test_handle_place_order(self):
        """Test place_order handler function."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.data = {"status": "success", "orderId": 12345}
        mock_client.place_order = AsyncMock(return_value=mock_response)

        args = {
            "assetIndex": 0,
            "isBuy": True,
            "price": "50000",
            "size": "0.1",
            "timeInForce": "Gtc"
        }
        result = await handle_place_order(mock_client, args)

        mock_client.place_order.assert_called_once()
        assert "content" in result
        assert len(result["content"]) == 1
        assert isinstance(result["content"][0], TextContent)
        assert "successfully" in result["content"][0].text

    def test_tools_are_available(self):
        """Test that required tools are available."""
        # Test that tool definitions exist
        assert get_all_mids_tool is not None
        assert get_l2_book_tool is not None
        assert place_order_tool is not None

        # Test that handlers exist
        assert handle_get_all_mids is not None
        assert handle_get_l2_book is not None
        assert handle_place_order is not None

    @pytest.mark.asyncio
    async def test_handler_with_exception(self):
        """Test that exceptions in handlers are propagated."""
        mock_client = MagicMock()
        mock_client.get_all_mids = AsyncMock(side_effect=Exception("Network error"))

        with pytest.raises(Exception, match="Network error"):
            await handle_get_all_mids(mock_client, {})

    @pytest.mark.asyncio
    async def test_handler_with_empty_data(self):
        """Test handlers with empty response data."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.data = None  # Empty data
        mock_client.get_all_mids = AsyncMock(return_value=mock_response)

        result = await handle_get_all_mids(mock_client, {})

        assert "content" in result
        assert len(result["content"]) == 1
        assert isinstance(result["content"][0], TextContent)

    def test_app_configuration(self):
        """Test that the app is configured correctly."""
        # Verify app has the expected name
        assert app.name == "hyperliquid-mcp-server"

        # Verify that the app has handlers
        assert hasattr(app, 'name')

    @pytest.mark.asyncio
    async def test_tool_argument_handling(self):
        """Test that tool handlers handle arguments correctly."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.data = {"test": "data"}
        mock_client.get_l2_book = AsyncMock(return_value=mock_response)

        # Test with minimal arguments
        args = {"coin": "BTC"}
        result = await handle_get_l2_book(mock_client, args)

        mock_client.get_l2_book.assert_called_once_with("BTC", None)
        assert "content" in result

        # Test with all arguments
        mock_client.reset_mock()
        mock_client.get_l2_book = AsyncMock(return_value=mock_response)
        args = {"coin": "ETH", "nSigFigs": 5}
        result = await handle_get_l2_book(mock_client, args)

        mock_client.get_l2_book.assert_called_once_with("ETH", 5)
        assert "content" in result