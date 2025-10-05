import axios, { AxiosInstance } from 'axios';
import { ethers } from 'ethers';
import {
  HyperliquidConfig,
  ApiResponse,
  AllMidsResponse,
  L2BookResponse,
  CandleSnapshotResponse,
  OpenOrder,
  UserFill,
  Portfolio,
  PlaceOrderAction,
  CancelOrderAction
} from '../types/hyperliquid.js';

export class HyperliquidClient {
  private config: HyperliquidConfig;
  private axios: AxiosInstance;
  private wallet?: ethers.Wallet;

  constructor(config: HyperliquidConfig) {
    this.config = {
      ...config,
      apiUrl: config.isTestnet
        ? 'https://api.hyperliquid-testnet.xyz'
        : 'https://api.hyperliquid.xyz'
    };

    this.axios = axios.create({
      baseURL: this.config.apiUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (this.config.privateKey) {
      this.wallet = new ethers.Wallet(this.config.privateKey);
    }
  }

  // Generate nonce (current timestamp in milliseconds)
  private generateNonce(): number {
    return Date.now();
  }

  // Sign action for exchange endpoint
  private async signAction(action: any, nonce: number): Promise<string> {
    if (!this.wallet) {
      throw new Error('Private key required for trading operations');
    }

    const message = JSON.stringify({
      action,
      nonce,
      vaultAddress: this.config.walletAddress || null,
    });

    const messageHash = ethers.keccak256(ethers.toUtf8Bytes(message));
    const signature = await this.wallet.signMessage(ethers.getBytes(messageHash));
    return signature;
  }

  // Info endpoint methods (no authentication required)
  async getAllMids(): Promise<ApiResponse<AllMidsResponse>> {
    try {
      const response = await this.axios.post('/info', {
        type: 'allMids'
      });
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      };
    }
  }

  async getL2Book(coin: string, nSigFigs?: number): Promise<ApiResponse<L2BookResponse>> {
    try {
      const response = await this.axios.post('/info', {
        type: 'l2Book',
        coin,
        nSigFigs
      });
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      };
    }
  }

  async getCandleSnapshot(
    coin: string,
    interval: string,
    startTime?: number,
    endTime?: number
  ): Promise<ApiResponse<CandleSnapshotResponse>> {
    try {
      const response = await this.axios.post('/info', {
        type: 'candleSnapshot',
        req: {
          coin,
          interval,
          startTime,
          endTime
        }
      });
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      };
    }
  }

  async getOpenOrders(user?: string): Promise<ApiResponse<OpenOrder[]>> {
    try {
      const response = await this.axios.post('/info', {
        type: 'openOrders',
        user: user || this.config.walletAddress
      });
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      };
    }
  }

  async getUserFills(user?: string): Promise<ApiResponse<UserFill[]>> {
    try {
      const response = await this.axios.post('/info', {
        type: 'userFills',
        user: user || this.config.walletAddress
      });
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      };
    }
  }

  async getUserFillsByTime(
    user?: string,
    startTime?: number,
    endTime?: number
  ): Promise<ApiResponse<UserFill[]>> {
    try {
      const response = await this.axios.post('/info', {
        type: 'userFillsByTime',
        user: user || this.config.walletAddress,
        startTime,
        endTime
      });
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      };
    }
  }

  async getPortfolio(user?: string): Promise<ApiResponse<Portfolio>> {
    try {
      const response = await this.axios.post('/info', {
        type: 'clearinghouseState',
        user: user || this.config.walletAddress
      });
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      };
    }
  }

  // Exchange endpoint methods (require authentication)
  async placeOrder(action: PlaceOrderAction): Promise<ApiResponse<any>> {
    try {
      if (!this.wallet) {
        throw new Error('Private key required for trading operations');
      }

      const nonce = this.generateNonce();
      const signature = await this.signAction(action, nonce);

      const response = await this.axios.post('/exchange', {
        action,
        nonce,
        signature,
        vaultAddress: this.config.walletAddress || null,
      });

      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      };
    }
  }

  async cancelOrder(action: CancelOrderAction): Promise<ApiResponse<any>> {
    try {
      if (!this.wallet) {
        throw new Error('Private key required for trading operations');
      }

      const nonce = this.generateNonce();
      const signature = await this.signAction(action, nonce);

      const response = await this.axios.post('/exchange', {
        action,
        nonce,
        signature,
        vaultAddress: this.config.walletAddress || null,
      });

      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      };
    }
  }

  async cancelAllOrders(): Promise<ApiResponse<any>> {
    try {
      if (!this.wallet) {
        throw new Error('Private key required for trading operations');
      }

      const action = { type: 'cancelByCloid', cancels: [] };
      const nonce = this.generateNonce();
      const signature = await this.signAction(action, nonce);

      const response = await this.axios.post('/exchange', {
        action,
        nonce,
        signature,
        vaultAddress: this.config.walletAddress || null,
      });

      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || error.message
      };
    }
  }
}