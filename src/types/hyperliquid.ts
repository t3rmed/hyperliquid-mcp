// Hyperliquid API Types

export interface HyperliquidConfig {
  apiUrl: string;
  privateKey?: string;
  walletAddress?: string;
  isTestnet?: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// Market Data Types
export interface AllMidsResponse {
  [coin: string]: string;
}

export interface L2BookLevel {
  px: string; // price
  sz: string; // size
}

export interface L2BookResponse {
  coin: string;
  levels: [L2BookLevel[], L2BookLevel[]]; // [bids, asks]
  time: number;
}

export interface CandleData {
  t: number; // timestamp
  T: number; // close timestamp
  s: string; // coin
  i: string; // interval
  o: string; // open
  c: string; // close
  h: string; // high
  l: string; // low
  v: string; // volume
  n: number; // number of trades
}

export interface CandleSnapshotResponse {
  coin: string;
  candles: CandleData[];
}

// Trading Types
export interface OrderRequest {
  a: number; // asset index
  b: boolean; // is buy
  p: string; // price
  s: string; // size
  r?: boolean; // reduce only
  t: {
    limit?: {
      tif: 'Alo' | 'Ioc' | 'Gtc';
    };
    trigger?: {
      triggerPx: string;
      isMarket: boolean;
      tpsl: 'tp' | 'sl';
    };
  };
  c?: string; // client order id
}

export interface PlaceOrderAction {
  type: 'order';
  orders: OrderRequest[];
}

export interface CancelOrderAction {
  type: 'cancel';
  cancels: Array<{
    a: number; // asset index
    o: number; // order id
  } | {
    a: number; // asset index
    c: string; // client order id
  }>;
}

export interface OpenOrder {
  coin: string;
  side: 'B' | 'A';
  sz: string;
  px: string;
  oid: number;
  timestamp: number;
  origSz: string;
  cloid?: string;
}

export interface UserFill {
  coin: string;
  px: string;
  sz: string;
  side: 'B' | 'A';
  time: number;
  oid: number;
  crossed: boolean;
  fee: string;
  tid: number;
}

export interface Portfolio {
  totalNtlPos: string;
  totalUnrealizedPnl: string;
  totalMarginUsed: string;
  time: number;
}