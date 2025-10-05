"""Test configuration management."""

import os
import pytest
from unittest.mock import patch

from hyperliquid_mcp_server.utils.config import get_config, validate_config
from hyperliquid_mcp_server.types.hyperliquid import HyperliquidConfig


class TestConfig:
    """Test configuration functionality."""

    def test_default_config(self):
        """Test default configuration values."""
        with patch.dict(os.environ, {}, clear=True):
            config = get_config()

            assert config.api_url == "https://api.hyperliquid.xyz"
            assert config.private_key is None
            assert config.wallet_address is None
            assert config.is_testnet is False

    def test_testnet_config(self):
        """Test testnet configuration."""
        with patch.dict(os.environ, {"HYPERLIQUID_TESTNET": "true"}):
            config = get_config()

            assert config.api_url == "https://api.hyperliquid-testnet.xyz"
            assert config.is_testnet is True

    def test_full_config(self):
        """Test configuration with all values set."""
        env_vars = {
            "HYPERLIQUID_PRIVATE_KEY": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "HYPERLIQUID_WALLET_ADDRESS": "0xabcdef1234567890abcdef1234567890abcdef12",
            "HYPERLIQUID_TESTNET": "true"
        }

        with patch.dict(os.environ, env_vars):
            config = get_config()

            assert config.private_key == env_vars["HYPERLIQUID_PRIVATE_KEY"]
            assert config.wallet_address == env_vars["HYPERLIQUID_WALLET_ADDRESS"]
            assert config.is_testnet is True
            assert config.api_url == "https://api.hyperliquid-testnet.xyz"

    def test_validate_config_valid(self):
        """Test validation of valid configuration."""
        config = HyperliquidConfig(
            api_url="https://api.hyperliquid.xyz",
            private_key="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            wallet_address="0xabcdef1234567890abcdef1234567890abcdef12"
        )

        errors = validate_config(config)
        assert len(errors) == 0

    def test_validate_config_invalid_private_key(self):
        """Test validation with invalid private key."""
        config = HyperliquidConfig(
            api_url="https://api.hyperliquid.xyz",
            private_key="1234567890abcdef",  # Missing 0x prefix
        )

        errors = validate_config(config)
        assert len(errors) == 1
        assert "Private key must start with 0x" in errors[0]

    def test_validate_config_invalid_wallet_address(self):
        """Test validation with invalid wallet address."""
        config = HyperliquidConfig(
            api_url="https://api.hyperliquid.xyz",
            wallet_address="abcdef1234567890",  # Missing 0x prefix
        )

        errors = validate_config(config)
        assert len(errors) == 1
        assert "Wallet address must start with 0x" in errors[0]

    def test_validate_config_no_api_url(self):
        """Test validation with missing API URL."""
        config = HyperliquidConfig(api_url="")

        errors = validate_config(config)
        assert len(errors) == 1
        assert "API URL is required" in errors[0]

    def test_testnet_false_values(self):
        """Test that various false values for testnet work correctly."""
        false_values = ["false", "False", "FALSE", "0", ""]

        for value in false_values:
            with patch.dict(os.environ, {"HYPERLIQUID_TESTNET": value}):
                config = get_config()
                assert config.is_testnet is False
                assert config.api_url == "https://api.hyperliquid.xyz"