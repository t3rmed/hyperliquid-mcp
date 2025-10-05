"""Configuration management for Hyperliquid MCP server."""

import os
from typing import List

from ..types.hyperliquid import HyperliquidConfig


def get_config() -> HyperliquidConfig:
    """Get configuration from environment variables."""
    config = HyperliquidConfig(
        api_url=os.getenv("HYPERLIQUID_API_URL", "https://api.hyperliquid.xyz"),
        private_key=os.getenv("HYPERLIQUID_PRIVATE_KEY"),
        wallet_address=os.getenv("HYPERLIQUID_WALLET_ADDRESS"),
        is_testnet=os.getenv("HYPERLIQUID_TESTNET", "").lower() == "true"
    )

    # Override with testnet URL if testnet is enabled
    if config.is_testnet:
        config.api_url = "https://api.hyperliquid-testnet.xyz"

    return config


def validate_config(config: HyperliquidConfig) -> List[str]:
    """Validate configuration and return list of errors."""
    errors: List[str] = []

    if not config.api_url:
        errors.append("API URL is required")

    # Private key is optional for read-only operations
    if config.private_key and not config.private_key.startswith("0x"):
        errors.append("Private key must start with 0x")

    if config.wallet_address and not config.wallet_address.startswith("0x"):
        errors.append("Wallet address must start with 0x")

    return errors