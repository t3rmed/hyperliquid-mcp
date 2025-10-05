import { HyperliquidConfig } from '../types/hyperliquid.js';

export function getConfig(): HyperliquidConfig {
  const config: HyperliquidConfig = {
    apiUrl: process.env.HYPERLIQUID_API_URL || 'https://api.hyperliquid.xyz',
    privateKey: process.env.HYPERLIQUID_PRIVATE_KEY,
    walletAddress: process.env.HYPERLIQUID_WALLET_ADDRESS,
    isTestnet: process.env.HYPERLIQUID_TESTNET === 'true'
  };

  // Override with testnet URL if testnet is enabled
  if (config.isTestnet) {
    config.apiUrl = 'https://api.hyperliquid-testnet.xyz';
  }

  return config;
}

export function validateConfig(config: HyperliquidConfig): string[] {
  const errors: string[] = [];

  if (!config.apiUrl) {
    errors.push('API URL is required');
  }

  // Private key is optional for read-only operations
  if (config.privateKey && !config.privateKey.startsWith('0x')) {
    errors.push('Private key must start with 0x');
  }

  if (config.walletAddress && !config.walletAddress.startsWith('0x')) {
    errors.push('Wallet address must start with 0x');
  }

  return errors;
}