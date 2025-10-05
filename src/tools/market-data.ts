import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { HyperliquidClient } from '../utils/hyperliquid-client.js';

export const getAllMidsTool: Tool = {
  name: 'get_all_mids',
  description: 'Get current mid prices for all coins on Hyperliquid',
  inputSchema: {
    type: 'object',
    properties: {},
    required: []
  }
};

export const getL2BookTool: Tool = {
  name: 'get_l2_book',
  description: 'Get L2 order book snapshot for a specific coin',
  inputSchema: {
    type: 'object',
    properties: {
      coin: {
        type: 'string',
        description: 'The coin symbol (e.g., BTC, ETH, SOL)'
      },
      nSigFigs: {
        type: 'number',
        description: 'Number of significant figures for price aggregation (optional)',
        minimum: 1,
        maximum: 5
      }
    },
    required: ['coin']
  }
};

export const getCandleSnapshotTool: Tool = {
  name: 'get_candle_snapshot',
  description: 'Get historical candle data for a specific coin',
  inputSchema: {
    type: 'object',
    properties: {
      coin: {
        type: 'string',
        description: 'The coin symbol (e.g., BTC, ETH, SOL)'
      },
      interval: {
        type: 'string',
        description: 'Candle interval',
        enum: ['1m', '5m', '15m', '1h', '4h', '1d', '1w', '1M']
      },
      startTime: {
        type: 'number',
        description: 'Start time in milliseconds (optional)'
      },
      endTime: {
        type: 'number',
        description: 'End time in milliseconds (optional)'
      }
    },
    required: ['coin', 'interval']
  }
};

export async function handleGetAllMids(client: HyperliquidClient, args: any) {
  const result = await client.getAllMids();

  if (!result.success) {
    throw new Error(`Failed to get mid prices: ${result.error}`);
  }

  return {
    content: [
      {
        type: 'text',
        text: `Mid prices for all coins:\n${JSON.stringify(result.data, null, 2)}`
      }
    ]
  };
}

export async function handleGetL2Book(client: HyperliquidClient, args: any) {
  const { coin, nSigFigs } = args;
  const result = await client.getL2Book(coin, nSigFigs);

  if (!result.success) {
    throw new Error(`Failed to get L2 book for ${coin}: ${result.error}`);
  }

  const book = result.data;
  const bids = book?.levels?.[0] || [];
  const asks = book?.levels?.[1] || [];

  return {
    content: [
      {
        type: 'text',
        text: `L2 Order Book for ${coin}:\n\nBids (${bids.length} levels):\n${bids.map(b => `${b.px} @ ${b.sz}`).join('\n')}\n\nAsks (${asks.length} levels):\n${asks.map(a => `${a.px} @ ${a.sz}`).join('\n')}`
      }
    ]
  };
}

export async function handleGetCandleSnapshot(client: HyperliquidClient, args: any) {
  const { coin, interval, startTime, endTime } = args;
  const result = await client.getCandleSnapshot(coin, interval, startTime, endTime);

  if (!result.success) {
    throw new Error(`Failed to get candle data for ${coin}: ${result.error}`);
  }

  const candles = result.data?.candles || [];

  return {
    content: [
      {
        type: 'text',
        text: `Candle data for ${coin} (${interval}):\n${candles.map(c =>
          `${new Date(c.t).toISOString()}: O:${c.o} H:${c.h} L:${c.l} C:${c.c} V:${c.v}`
        ).join('\n')}`
      }
    ]
  };
}