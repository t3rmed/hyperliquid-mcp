"""Test Hyperliquid API client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from hyperliquid_mcp_server.utils.hyperliquid_client import HyperliquidClient
from hyperliquid_mcp_server.types.hyperliquid import HyperliquidConfig


class TestHyperliquidClient:
    """Test Hyperliquid API client functionality."""

    def test_client_initialization_mainnet(self):
        """Test client initialization for mainnet."""
        config = HyperliquidConfig(
            api_url="https://api.hyperliquid.xyz",
            is_testnet=False
        )

        client = HyperliquidClient(config)

        assert client.config.api_url == "https://api.hyperliquid.xyz"
        assert client.config.is_testnet is False
        assert client.account is None

    def test_client_initialization_testnet(self):
        """Test client initialization for testnet."""
        config = HyperliquidConfig(
            api_url="https://api.hyperliquid.xyz",
            is_testnet=True
        )

        client = HyperliquidClient(config)

        assert client.config.api_url == "https://api.hyperliquid-testnet.xyz"
        assert client.config.is_testnet is True

    def test_client_initialization_with_private_key(self):
        """Test client initialization with private key."""
        config = HyperliquidConfig(
            private_key="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        )

        with patch('hyperliquid_mcp_server.utils.hyperliquid_client.Account') as mock_account:
            mock_account.from_key.return_value = MagicMock()
            client = HyperliquidClient(config)

            mock_account.from_key.assert_called_once_with(config.private_key)
            assert client.account is not None

    def test_generate_nonce(self):
        """Test nonce generation."""
        config = HyperliquidConfig()
        client = HyperliquidClient(config)

        nonce1 = client._generate_nonce()
        nonce2 = client._generate_nonce()

        assert isinstance(nonce1, int)
        assert isinstance(nonce2, int)
        assert nonce2 >= nonce1  # Should be increasing

    @pytest.mark.asyncio
    async def test_get_all_mids_success(self):
        """Test successful get_all_mids call."""
        config = HyperliquidConfig()
        client = HyperliquidClient(config)

        mock_response = MagicMock()
        mock_response.json.return_value = {"BTC": "50000", "ETH": "3000"}
        mock_response.raise_for_status.return_value = None

        with patch.object(client.client, 'post', return_value=mock_response) as mock_post:
            result = await client.get_all_mids()

            mock_post.assert_called_once_with("/info", json={"type": "allMids"})
            assert result.success is True
            assert result.data == {"BTC": "50000", "ETH": "3000"}
            assert result.error is None

    @pytest.mark.asyncio
    async def test_get_all_mids_failure(self):
        """Test failed get_all_mids call."""
        config = HyperliquidConfig()
        client = HyperliquidClient(config)

        with patch.object(client.client, 'post', side_effect=Exception("Network error")):
            result = await client.get_all_mids()

            assert result.success is False
            assert result.data is None
            assert "Network error" in result.error

    @pytest.mark.asyncio
    async def test_get_l2_book_with_params(self):
        """Test get_l2_book with parameters."""
        config = HyperliquidConfig()
        client = HyperliquidClient(config)

        mock_response = MagicMock()
        mock_response.json.return_value = {"coin": "BTC", "levels": [[], []]}
        mock_response.raise_for_status.return_value = None

        with patch.object(client.client, 'post', return_value=mock_response) as mock_post:
            result = await client.get_l2_book("BTC", 3)

            expected_payload = {"type": "l2Book", "coin": "BTC", "nSigFigs": 3}
            mock_post.assert_called_once_with("/info", json=expected_payload)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_trading_requires_private_key(self):
        """Test that trading operations require private key."""
        config = HyperliquidConfig()  # No private key
        client = HyperliquidClient(config)

        from hyperliquid_mcp_server.types.hyperliquid import PlaceOrderAction, OrderRequest

        action = PlaceOrderAction(orders=[])

        result = await client.place_order(action)

        assert result.success is False
        assert "Private key required" in result.error

    @pytest.mark.asyncio
    async def test_client_close(self):
        """Test client cleanup."""
        config = HyperliquidConfig()
        client = HyperliquidClient(config)

        with patch.object(client.client, 'aclose') as mock_close:
            await client.close()
            mock_close.assert_called_once()