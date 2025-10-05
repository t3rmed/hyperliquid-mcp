import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { HyperliquidClient } from '../utils/hyperliquid-client.js';
import { OrderRequest, PlaceOrderAction, CancelOrderAction } from '../types/hyperliquid.js';

export const placeOrderTool: Tool = {
  name: 'place_order',
  description: 'Place a limit or trigger order on Hyperliquid',
  inputSchema: {
    type: 'object',
    properties: {
      assetIndex: {
        type: 'number',
        description: 'Asset index for the coin (0 for BTC, 1 for ETH, etc.)'
      },
      isBuy: {
        type: 'boolean',
        description: 'True for buy order, false for sell order'
      },
      price: {
        type: 'string',
        description: 'Order price as string'
      },
      size: {
        type: 'string',
        description: 'Order size as string'
      },
      reduceOnly: {
        type: 'boolean',
        description: 'Whether this is a reduce-only order (optional, default false)'
      },
      timeInForce: {
        type: 'string',
        description: 'Time in force',
        enum: ['Gtc', 'Ioc', 'Alo']
      },
      clientOrderId: {
        type: 'string',
        description: 'Client order ID (optional)'
      }
    },
    required: ['assetIndex', 'isBuy', 'price', 'size', 'timeInForce']
  }
};

export const placeTriggerOrderTool: Tool = {
  name: 'place_trigger_order',
  description: 'Place a trigger order (stop-loss or take-profit) on Hyperliquid',
  inputSchema: {
    type: 'object',
    properties: {
      assetIndex: {
        type: 'number',
        description: 'Asset index for the coin (0 for BTC, 1 for ETH, etc.)'
      },
      isBuy: {
        type: 'boolean',
        description: 'True for buy order, false for sell order'
      },
      size: {
        type: 'string',
        description: 'Order size as string'
      },
      triggerPrice: {
        type: 'string',
        description: 'Trigger price as string'
      },
      isMarket: {
        type: 'boolean',
        description: 'Whether to execute as market order when triggered'
      },
      triggerType: {
        type: 'string',
        description: 'Trigger type',
        enum: ['tp', 'sl']
      },
      reduceOnly: {
        type: 'boolean',
        description: 'Whether this is a reduce-only order (optional, default false)'
      },
      clientOrderId: {
        type: 'string',
        description: 'Client order ID (optional)'
      }
    },
    required: ['assetIndex', 'isBuy', 'size', 'triggerPrice', 'isMarket', 'triggerType']
  }
};

export const cancelOrderTool: Tool = {
  name: 'cancel_order',
  description: 'Cancel a specific order by order ID or client order ID',
  inputSchema: {
    type: 'object',
    properties: {
      assetIndex: {
        type: 'number',
        description: 'Asset index for the coin'
      },
      orderId: {
        type: 'number',
        description: 'Order ID to cancel (use either orderId or clientOrderId)'
      },
      clientOrderId: {
        type: 'string',
        description: 'Client order ID to cancel (use either orderId or clientOrderId)'
      }
    },
    required: ['assetIndex']
  }
};

export const cancelAllOrdersTool: Tool = {
  name: 'cancel_all_orders',
  description: 'Cancel all open orders',
  inputSchema: {
    type: 'object',
    properties: {},
    required: []
  }
};

export async function handlePlaceOrder(client: HyperliquidClient, args: any) {
  const {
    assetIndex,
    isBuy,
    price,
    size,
    reduceOnly = false,
    timeInForce,
    clientOrderId
  } = args;

  const order: OrderRequest = {
    a: assetIndex,
    b: isBuy,
    p: price,
    s: size,
    r: reduceOnly,
    t: {
      limit: {
        tif: timeInForce
      }
    }
  };

  if (clientOrderId) {
    order.c = clientOrderId;
  }

  const action: PlaceOrderAction = {
    type: 'order',
    orders: [order]
  };

  const result = await client.placeOrder(action);

  if (!result.success) {
    throw new Error(`Failed to place order: ${result.error}`);
  }

  return {
    content: [
      {
        type: 'text',
        text: `Order placed successfully!\n\n${JSON.stringify(result.data, null, 2)}`
      }
    ]
  };
}

export async function handlePlaceTriggerOrder(client: HyperliquidClient, args: any) {
  const {
    assetIndex,
    isBuy,
    size,
    triggerPrice,
    isMarket,
    triggerType,
    reduceOnly = false,
    clientOrderId
  } = args;

  const order: OrderRequest = {
    a: assetIndex,
    b: isBuy,
    p: '0', // Not used for trigger orders
    s: size,
    r: reduceOnly,
    t: {
      trigger: {
        triggerPx: triggerPrice,
        isMarket,
        tpsl: triggerType
      }
    }
  };

  if (clientOrderId) {
    order.c = clientOrderId;
  }

  const action: PlaceOrderAction = {
    type: 'order',
    orders: [order]
  };

  const result = await client.placeOrder(action);

  if (!result.success) {
    throw new Error(`Failed to place trigger order: ${result.error}`);
  }

  return {
    content: [
      {
        type: 'text',
        text: `Trigger order placed successfully!\n\n${JSON.stringify(result.data, null, 2)}`
      }
    ]
  };
}

export async function handleCancelOrder(client: HyperliquidClient, args: any) {
  const { assetIndex, orderId, clientOrderId } = args;

  if (!orderId && !clientOrderId) {
    throw new Error('Either orderId or clientOrderId must be provided');
  }

  const cancel: any = { a: assetIndex };

  if (orderId) {
    cancel.o = orderId;
  } else {
    cancel.c = clientOrderId;
  }

  const action: CancelOrderAction = {
    type: 'cancel',
    cancels: [cancel]
  };

  const result = await client.cancelOrder(action);

  if (!result.success) {
    throw new Error(`Failed to cancel order: ${result.error}`);
  }

  return {
    content: [
      {
        type: 'text',
        text: `Order cancelled successfully!\n\n${JSON.stringify(result.data, null, 2)}`
      }
    ]
  };
}

export async function handleCancelAllOrders(client: HyperliquidClient, args: any) {
  const result = await client.cancelAllOrders();

  if (!result.success) {
    throw new Error(`Failed to cancel all orders: ${result.error}`);
  }

  return {
    content: [
      {
        type: 'text',
        text: `All orders cancelled successfully!\n\n${JSON.stringify(result.data, null, 2)}`
      }
    ]
  };
}