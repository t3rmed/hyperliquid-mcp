#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

import { HyperliquidClient } from './utils/hyperliquid-client.js';
import { getConfig, validateConfig } from './utils/config.js';

// Market data tools
import {
  getAllMidsTool,
  getL2BookTool,
  getCandleSnapshotTool,
  handleGetAllMids,
  handleGetL2Book,
  handleGetCandleSnapshot
} from './tools/market-data.js';

// Account info tools
import {
  getOpenOrdersTool,
  getUserFillsTool,
  getUserFillsByTimeTool,
  getPortfolioTool,
  handleGetOpenOrders,
  handleGetUserFills,
  handleGetUserFillsByTime,
  handleGetPortfolio
} from './tools/account-info.js';

// Trading tools
import {
  placeOrderTool,
  placeTriggerOrderTool,
  cancelOrderTool,
  cancelAllOrdersTool,
  handlePlaceOrder,
  handlePlaceTriggerOrder,
  handleCancelOrder,
  handleCancelAllOrders
} from './tools/trading.js';

// Initialize configuration and client
const config = getConfig();
const configErrors = validateConfig(config);

if (configErrors.length > 0) {
  console.error('Configuration errors:');
  configErrors.forEach(error => console.error(`- ${error}`));
  console.error('\nPlease set the following environment variables:');
  console.error('- HYPERLIQUID_PRIVATE_KEY (optional, required for trading)');
  console.error('- HYPERLIQUID_WALLET_ADDRESS (optional, defaults to derived from private key)');
  console.error('- HYPERLIQUID_TESTNET=true (optional, defaults to mainnet)');
}

const client = new HyperliquidClient(config);

const server = new Server(
  {
    name: 'hyperliquid-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List all available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      // Market data tools
      getAllMidsTool,
      getL2BookTool,
      getCandleSnapshotTool,
      // Account info tools
      getOpenOrdersTool,
      getUserFillsTool,
      getUserFillsByTimeTool,
      getPortfolioTool,
      // Trading tools
      placeOrderTool,
      placeTriggerOrderTool,
      cancelOrderTool,
      cancelAllOrdersTool,
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const { name, arguments: args } = request.params;

    switch (name) {
      // Market data handlers
      case 'get_all_mids':
        return await handleGetAllMids(client, args);
      case 'get_l2_book':
        return await handleGetL2Book(client, args);
      case 'get_candle_snapshot':
        return await handleGetCandleSnapshot(client, args);

      // Account info handlers
      case 'get_open_orders':
        return await handleGetOpenOrders(client, args);
      case 'get_user_fills':
        return await handleGetUserFills(client, args);
      case 'get_user_fills_by_time':
        return await handleGetUserFillsByTime(client, args);
      case 'get_portfolio':
        return await handleGetPortfolio(client, args);

      // Trading handlers
      case 'place_order':
        return await handlePlaceOrder(client, args);
      case 'place_trigger_order':
        return await handlePlaceTriggerOrder(client, args);
      case 'cancel_order':
        return await handleCancelOrder(client, args);
      case 'cancel_all_orders':
        return await handleCancelAllOrders(client, args);

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${errorMessage}`
        }
      ],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Hyperliquid MCP server running on stdio');
  console.error(`Configuration: ${config.isTestnet ? 'Testnet' : 'Mainnet'}`);
  console.error(`Wallet configured: ${!!config.privateKey}`);
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});