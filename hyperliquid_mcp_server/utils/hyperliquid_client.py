"""Hyperliquid API client."""

import json
import time
from typing import Any, Dict, List, Optional

import httpx
from eth_account import Account
from eth_hash.auto import keccak

from ..types.hyperliquid import (
    AllMidsResponse,
    ApiResponse,
    CancelOrderAction,
    CandleSnapshotResponse,
    HyperliquidConfig,
    L2BookResponse,
    OpenOrder,
    PlaceOrderAction,
    Portfolio,
    UserFill,
)


class HyperliquidClient:
    """Client for interacting with Hyperliquid API."""

    def __init__(self, config: HyperliquidConfig) -> None:
        """Initialize the client with configuration."""
        self.config = config
        self.config.api_url = (
            "https://api.hyperliquid-testnet.xyz"
            if config.is_testnet
            else "https://api.hyperliquid.xyz"
        )

        self.client = httpx.AsyncClient(
            base_url=self.config.api_url,
            timeout=30.0,
            headers={"Content-Type": "application/json"},
        )

        self.account: Optional[Account] = None
        if self.config.private_key:
            self.account = Account.from_key(self.config.private_key)

    def _generate_nonce(self) -> int:
        """Generate nonce (current timestamp in milliseconds)."""
        return int(time.time() * 1000)

    async def _sign_action(self, action: Dict[str, Any], nonce: int) -> str:
        """Sign action for exchange endpoint."""
        if not self.account:
            raise ValueError("Private key required for trading operations")

        message_dict = {
            "action": action,
            "nonce": nonce,
            "vaultAddress": self.config.wallet_address,
        }

        message = json.dumps(message_dict, separators=(",", ":"))
        message_hash = keccak(message.encode("utf-8"))
        signature = self.account.signHash(message_hash)
        return signature.signature.hex()

    async def get_all_mids(self) -> ApiResponse[AllMidsResponse]:
        """Get current mid prices for all coins."""
        try:
            response = await self.client.post("/info", json={"type": "allMids"})
            response.raise_for_status()
            return ApiResponse(success=True, data=response.json())
        except Exception as e:
            return ApiResponse(success=False, error=str(e))

    async def get_l2_book(
        self, coin: str, n_sig_figs: Optional[int] = None
    ) -> ApiResponse[L2BookResponse]:
        """Get L2 order book snapshot for a specific coin."""
        try:
            payload = {"type": "l2Book", "coin": coin}
            if n_sig_figs is not None:
                payload["nSigFigs"] = n_sig_figs

            response = await self.client.post("/info", json=payload)
            response.raise_for_status()
            return ApiResponse(success=True, data=response.json())
        except Exception as e:
            return ApiResponse(success=False, error=str(e))

    async def get_candle_snapshot(
        self,
        coin: str,
        interval: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> ApiResponse[CandleSnapshotResponse]:
        """Get historical candle data."""
        try:
            req_data = {"coin": coin, "interval": interval}
            if start_time is not None:
                req_data["startTime"] = start_time
            if end_time is not None:
                req_data["endTime"] = end_time

            payload = {"type": "candleSnapshot", "req": req_data}

            response = await self.client.post("/info", json=payload)
            response.raise_for_status()
            return ApiResponse(success=True, data=response.json())
        except Exception as e:
            return ApiResponse(success=False, error=str(e))

    async def get_open_orders(
        self, user: Optional[str] = None
    ) -> ApiResponse[List[OpenOrder]]:
        """Get all open orders."""
        try:
            payload = {
                "type": "openOrders",
                "user": user or self.config.wallet_address,
            }

            response = await self.client.post("/info", json=payload)
            response.raise_for_status()
            return ApiResponse(success=True, data=response.json())
        except Exception as e:
            return ApiResponse(success=False, error=str(e))

    async def get_user_fills(
        self, user: Optional[str] = None
    ) -> ApiResponse[List[UserFill]]:
        """Get trading history (fills)."""
        try:
            payload = {
                "type": "userFills",
                "user": user or self.config.wallet_address,
            }

            response = await self.client.post("/info", json=payload)
            response.raise_for_status()
            return ApiResponse(success=True, data=response.json())
        except Exception as e:
            return ApiResponse(success=False, error=str(e))

    async def get_user_fills_by_time(
        self,
        user: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> ApiResponse[List[UserFill]]:
        """Get trading history for a specific time range."""
        try:
            payload = {
                "type": "userFillsByTime",
                "user": user or self.config.wallet_address,
            }
            if start_time is not None:
                payload["startTime"] = start_time
            if end_time is not None:
                payload["endTime"] = end_time

            response = await self.client.post("/info", json=payload)
            response.raise_for_status()
            return ApiResponse(success=True, data=response.json())
        except Exception as e:
            return ApiResponse(success=False, error=str(e))

    async def get_portfolio(self, user: Optional[str] = None) -> ApiResponse[Portfolio]:
        """Get portfolio information."""
        try:
            payload = {
                "type": "clearinghouseState",
                "user": user or self.config.wallet_address,
            }

            response = await self.client.post("/info", json=payload)
            response.raise_for_status()
            return ApiResponse(success=True, data=response.json())
        except Exception as e:
            return ApiResponse(success=False, error=str(e))

    async def place_order(self, action: PlaceOrderAction) -> ApiResponse[Any]:
        """Place an order."""
        try:
            if not self.account:
                raise ValueError("Private key required for trading operations")

            nonce = self._generate_nonce()
            signature = await self._sign_action(action.model_dump(), nonce)

            payload = {
                "action": action.model_dump(),
                "nonce": nonce,
                "signature": signature,
                "vaultAddress": self.config.wallet_address,
            }

            response = await self.client.post("/exchange", json=payload)
            response.raise_for_status()
            return ApiResponse(success=True, data=response.json())
        except Exception as e:
            return ApiResponse(success=False, error=str(e))

    async def cancel_order(self, action: CancelOrderAction) -> ApiResponse[Any]:
        """Cancel an order."""
        try:
            if not self.account:
                raise ValueError("Private key required for trading operations")

            nonce = self._generate_nonce()
            signature = await self._sign_action(action.model_dump(), nonce)

            payload = {
                "action": action.model_dump(),
                "nonce": nonce,
                "signature": signature,
                "vaultAddress": self.config.wallet_address,
            }

            response = await self.client.post("/exchange", json=payload)
            response.raise_for_status()
            return ApiResponse(success=True, data=response.json())
        except Exception as e:
            return ApiResponse(success=False, error=str(e))

    async def cancel_all_orders(self) -> ApiResponse[Any]:
        """Cancel all orders."""
        try:
            if not self.account:
                raise ValueError("Private key required for trading operations")

            action = {"type": "cancelByCloid", "cancels": []}
            nonce = self._generate_nonce()
            signature = await self._sign_action(action, nonce)

            payload = {
                "action": action,
                "nonce": nonce,
                "signature": signature,
                "vaultAddress": self.config.wallet_address,
            }

            response = await self.client.post("/exchange", json=payload)
            response.raise_for_status()
            return ApiResponse(success=True, data=response.json())
        except Exception as e:
            return ApiResponse(success=False, error=str(e))

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()