import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { HyperliquidClient } from '../utils/hyperliquid-client.js';

export const getOpenOrdersTool: Tool = {
  name: 'get_open_orders',
  description: 'Get all open orders for the configured wallet or a specific user',
  inputSchema: {
    type: 'object',
    properties: {
      user: {
        type: 'string',
        description: 'User wallet address (optional, defaults to configured wallet)'
      }
    },
    required: []
  }
};

export const getUserFillsTool: Tool = {
  name: 'get_user_fills',
  description: 'Get trading history (fills) for the configured wallet or a specific user',
  inputSchema: {
    type: 'object',
    properties: {
      user: {
        type: 'string',
        description: 'User wallet address (optional, defaults to configured wallet)'
      }
    },
    required: []
  }
};

export const getUserFillsByTimeTool: Tool = {
  name: 'get_user_fills_by_time',
  description: 'Get trading history (fills) for a specific time range',
  inputSchema: {
    type: 'object',
    properties: {
      user: {
        type: 'string',
        description: 'User wallet address (optional, defaults to configured wallet)'
      },
      startTime: {
        type: 'number',
        description: 'Start time in milliseconds'
      },
      endTime: {
        type: 'number',
        description: 'End time in milliseconds'
      }
    },
    required: []
  }
};

export const getPortfolioTool: Tool = {
  name: 'get_portfolio',
  description: 'Get portfolio information including positions, PnL, and margin usage',
  inputSchema: {
    type: 'object',
    properties: {
      user: {
        type: 'string',
        description: 'User wallet address (optional, defaults to configured wallet)'
      }
    },
    required: []
  }
};

export async function handleGetOpenOrders(client: HyperliquidClient, args: any) {
  const { user } = args;
  const result = await client.getOpenOrders(user);

  if (!result.success) {
    throw new Error(`Failed to get open orders: ${result.error}`);
  }

  const orders = result.data || [];

  if (orders.length === 0) {
    return {
      content: [
        {
          type: 'text',
          text: 'No open orders found.'
        }
      ]
    };
  }

  return {
    content: [
      {
        type: 'text',
        text: `Open Orders (${orders.length}):\n\n${orders.map(order =>
          `${order.coin} ${order.side === 'B' ? 'BUY' : 'SELL'} ${order.sz} @ ${order.px} (ID: ${order.oid})`
        ).join('\n')}`
      }
    ]
  };
}

export async function handleGetUserFills(client: HyperliquidClient, args: any) {
  const { user } = args;
  const result = await client.getUserFills(user);

  if (!result.success) {
    throw new Error(`Failed to get user fills: ${result.error}`);
  }

  const fills = result.data || [];

  if (fills.length === 0) {
    return {
      content: [
        {
          type: 'text',
          text: 'No trading history found.'
        }
      ]
    };
  }

  return {
    content: [
      {
        type: 'text',
        text: `Trading History (${fills.length} fills):\n\n${fills.slice(0, 20).map(fill =>
          `${new Date(fill.time).toISOString()}: ${fill.coin} ${fill.side === 'B' ? 'BUY' : 'SELL'} ${fill.sz} @ ${fill.px} (Fee: ${fill.fee})`
        ).join('\n')}${fills.length > 20 ? '\n... and more' : ''}`
      }
    ]
  };
}

export async function handleGetUserFillsByTime(client: HyperliquidClient, args: any) {
  const { user, startTime, endTime } = args;
  const result = await client.getUserFillsByTime(user, startTime, endTime);

  if (!result.success) {
    throw new Error(`Failed to get user fills by time: ${result.error}`);
  }

  const fills = result.data || [];

  if (fills.length === 0) {
    return {
      content: [
        {
          type: 'text',
          text: 'No trading history found for the specified time range.'
        }
      ]
    };
  }

  return {
    content: [
      {
        type: 'text',
        text: `Trading History (${fills.length} fills):\n\n${fills.map(fill =>
          `${new Date(fill.time).toISOString()}: ${fill.coin} ${fill.side === 'B' ? 'BUY' : 'SELL'} ${fill.sz} @ ${fill.px} (Fee: ${fill.fee})`
        ).join('\n')}`
      }
    ]
  };
}

export async function handleGetPortfolio(client: HyperliquidClient, args: any) {
  const { user } = args;
  const result = await client.getPortfolio(user);

  if (!result.success) {
    throw new Error(`Failed to get portfolio: ${result.error}`);
  }

  const portfolio = result.data;

  return {
    content: [
      {
        type: 'text',
        text: `Portfolio Summary:\n\nTotal Notional Position: $${portfolio?.totalNtlPos || '0'}\nTotal Unrealized PnL: $${portfolio?.totalUnrealizedPnl || '0'}\nTotal Margin Used: $${portfolio?.totalMarginUsed || '0'}\nLast Updated: ${portfolio?.time ? new Date(portfolio.time).toISOString() : 'N/A'}`
      }
    ]
  };
}