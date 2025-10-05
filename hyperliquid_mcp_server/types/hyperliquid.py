"""Hyperliquid API type definitions."""

from typing import Any, Dict, List, Literal, Optional, Union, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')


class HyperliquidConfig(BaseModel):
    """Configuration for Hyperliquid client."""
    api_url: str = "https://api.hyperliquid.xyz"
    private_key: Optional[str] = None
    wallet_address: Optional[str] = None
    is_testnet: bool = False


class ApiResponse(BaseModel, Generic[T]):
    """Generic API response wrapper."""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None


# Market Data Types
AllMidsResponse = Dict[str, str]


class L2BookLevel(BaseModel):
    """L2 order book level."""
    px: str  # price
    sz: str  # size


class L2BookResponse(BaseModel):
    """L2 order book response."""
    coin: str
    levels: List[List[L2BookLevel]]  # [bids, asks]
    time: int


class CandleData(BaseModel):
    """Candlestick data."""
    t: int  # timestamp
    T: int  # close timestamp
    s: str  # coin
    i: str  # interval
    o: str  # open
    c: str  # close
    h: str  # high
    l: str  # low
    v: str  # volume
    n: int  # number of trades


class CandleSnapshotResponse(BaseModel):
    """Candle snapshot response."""
    coin: str
    candles: List[CandleData]


# Trading Types
class LimitOrderType(BaseModel):
    """Limit order type."""
    tif: Literal["Alo", "Ioc", "Gtc"]


class TriggerOrderType(BaseModel):
    """Trigger order type."""
    triggerPx: str
    isMarket: bool
    tpsl: Literal["tp", "sl"]


class OrderRequest(BaseModel):
    """Order request."""
    a: int  # asset index
    b: bool  # is buy
    p: str  # price
    s: str  # size
    r: Optional[bool] = None  # reduce only
    t: Union[Dict[str, LimitOrderType], Dict[str, TriggerOrderType]]
    c: Optional[str] = None  # client order id


class PlaceOrderAction(BaseModel):
    """Place order action."""
    type: Literal["order"] = "order"
    orders: List[OrderRequest]


class CancelOrderItem(BaseModel):
    """Cancel order item."""
    a: int  # asset index
    o: Optional[int] = None  # order id
    c: Optional[str] = None  # client order id


class CancelOrderAction(BaseModel):
    """Cancel order action."""
    type: Literal["cancel"] = "cancel"
    cancels: List[CancelOrderItem]


class OpenOrder(BaseModel):
    """Open order."""
    coin: str
    side: Literal["B", "A"]
    sz: str
    px: str
    oid: int
    timestamp: int
    origSz: str
    cloid: Optional[str] = None


class UserFill(BaseModel):
    """User fill."""
    coin: str
    px: str
    sz: str
    side: Literal["B", "A"]
    time: int
    oid: int
    crossed: bool
    fee: str
    tid: int


class Portfolio(BaseModel):
    """Portfolio data."""
    totalNtlPos: str
    totalUnrealizedPnl: str
    totalMarginUsed: str
    time: int