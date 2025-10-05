"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import MagicMock

from hyperliquid_mcp_server.types.hyperliquid import HyperliquidConfig
from hyperliquid_mcp_server.utils.hyperliquid_client import HyperliquidClient


@pytest.fixture
def default_config():
    """Provide a default test configuration."""
    return HyperliquidConfig(
        api_url="https://api.hyperliquid-testnet.xyz",
        is_testnet=True
    )


@pytest.fixture
def config_with_private_key():
    """Provide a test configuration with private key."""
    return HyperliquidConfig(
        api_url="https://api.hyperliquid-testnet.xyz",
        private_key="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        wallet_address="0xabcdef1234567890abcdef1234567890abcdef12",
        is_testnet=True
    )


@pytest.fixture
def mock_client(default_config):
    """Provide a mock Hyperliquid client for testing."""
    client = HyperliquidClient(default_config)
    client.client = MagicMock()
    return client


@pytest.fixture
def sample_api_response():
    """Provide sample API response data for testing."""
    return {
        "all_mids": {"BTC": "50000", "ETH": "3000", "SOL": "100"},
        "l2_book": {
            "coin": "BTC",
            "levels": [
                [{"px": "49999", "sz": "1.0"}, {"px": "49998", "sz": "0.5"}],  # bids
                [{"px": "50001", "sz": "0.8"}, {"px": "50002", "sz": "1.2"}]   # asks
            ],
            "time": 1640995200000
        },
        "candles": {
            "coin": "BTC",
            "candles": [
                {
                    "t": 1640995200000,
                    "T": 1640998800000,
                    "s": "BTC",
                    "i": "1h",
                    "o": "49000",
                    "c": "50000",
                    "h": "50500",
                    "l": "48500",
                    "v": "100.5",
                    "n": 1234
                }
            ]
        },
        "open_orders": [
            {
                "coin": "BTC",
                "side": "B",
                "sz": "0.1",
                "px": "49000",
                "oid": 12345,
                "timestamp": 1640995200000,
                "origSz": "0.1"
            }
        ],
        "user_fills": [
            {
                "coin": "BTC",
                "px": "50000",
                "sz": "0.05",
                "side": "B",
                "time": 1640995200000,
                "oid": 12345,
                "crossed": True,
                "fee": "2.5",
                "tid": 67890
            }
        ],
        "portfolio": {
            "totalNtlPos": "5000.00",
            "totalUnrealizedPnl": "250.00",
            "totalMarginUsed": "1000.00",
            "time": 1640995200000
        }
    }


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables before each test."""
    import os
    original_env = os.environ.copy()

    # Clear Hyperliquid-related environment variables
    env_vars_to_clear = [
        "HYPERLIQUID_PRIVATE_KEY",
        "HYPERLIQUID_WALLET_ADDRESS",
        "HYPERLIQUID_TESTNET",
        "HYPERLIQUID_API_URL"
    ]

    for var in env_vars_to_clear:
        if var in os.environ:
            del os.environ[var]

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_successful_response():
    """Mock a successful HTTP response."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"status": "success"}
    return mock_response


@pytest.fixture
def mock_error_response():
    """Mock an error HTTP response."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("HTTP Error")
    return mock_response


# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)