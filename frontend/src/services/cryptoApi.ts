import axios from 'axios';

// Extend Window interface to include ethereum (MetaMask)
declare global {
  interface Window {
    ethereum?: any;
  }
}

// Create axios instance for crypto API
const API_BASE_URL = 'http://localhost:8082/api/v1';

// Types and Interfaces
export interface WalletData {
  address: string;
  totalValue: number;
  dailyChange: number;
  gasPrice: number;
  activeTrades: number;
  tokens: TokenBalance[];
}

export interface TokenBalance {
  symbol: string;
  name: string;
  balance: string;
  value: string;
  change: number;
  price: number;
}

export interface TradeData {
  token: string;
  amount: number;
  type: 'buy' | 'sell';
  slippage: number;
  gasLimit?: number;
}

export interface FriendWallet {
  address: string;
  name?: string;
  totalValue: number;
  dailyChange: number;
  weeklyChange: number;
  monthlyChange: number;
  topTokens?: TopToken[];
  recentTrades?: RecentTrade[];
  aiInsight: string;
}

export interface TopToken {
  symbol: string;
  name: string;
  value: string;
  percentage: string;
  change: number;
}

export interface RecentTrade {
  token: string;
  type: 'buy' | 'sell';
  amount: string;
  timeAgo: string;
  profit?: number;
}

export interface MarketData {
  symbol: string;
  name: string;
  price: number;
  change24h: number;
  volume24h: number;
  marketCap: number;
  trend: 'bullish' | 'bearish' | 'neutral';
}

export interface TradeAlert {
  id: string;
  token: string;
  type: 'price' | 'volume' | 'volatility';
  condition: string;
  target: number;
  active: boolean;
}

// Mining-related interfaces
export interface HardwareInfo {
  gpus: GPU[];
  cpu: CPU;
  totalMemory: number;
  powerSupply: number;
}

export interface GPU {
  id: number;
  name: string;
  memory: number;
  powerLimit: number;
  temperature: number;
  fanSpeed: number;
  coreClockMHz: number;
  memoryClockMHz: number;
  driverVersion: string;
}

export interface CPU {
  name: string;
  cores: number;
  threads: number;
  baseClock: number;
  temperature: number;
}

export interface MiningStatus {
  isRunning: boolean;
  coin: string;
  algorithm: string;
  pool: string;
  hashrate: number;
  targetHashrate: number;
  powerConsumption: number;
  efficiency: number;
  temperature: number;
  fanSpeed: number;
  acceptedShares: number;
  rejectedShares: number;
  uptime: string;
  history?: PerformanceHistory[];
}

export interface PerformanceHistory {
  timestamp: string;
  hashrate: number;
  temperature: number;
  power: number;
}

export interface MiningEarnings {
  daily: number;
  weekly: number;
  monthly: number;
  total: number;
  dailyCoin: number;
  currency: string;
}

export interface MiningPool {
  name: string;
  url: string;
  port: number;
  fee: number;
  miners: number;
  hashrate: number;
  luck: number;
  lastBlock: string;
  algorithm: string;
}

export interface AIRecommendation {
  type: 'optimization' | 'profitability' | 'warning';
  message: string;
  confidence?: number;
  action?: string;
}

export interface MiningSchedule {
  enabled: boolean;
  startTime: string;
  endTime: string;
  days: string[];
  coin: string;
  lowPowerMode: boolean;
}

export interface Pool {
  id: string;
  name: string;
  size: number;
  returnPct: number;
  members: number;
  privacy: string;
  split_mode: string;
}

export interface BoostStatus {
  boost: number;
  boost_active: boolean;
  boost_ends_in: number;
  countdown: number;
}

// Mock data for development (replace with real API calls)
const generateMockWalletData = (): WalletData => ({
  address: '0x742d35Cc6634C0532925a3b8D4040af1',
  totalValue: 45672.89,
  dailyChange: 3.47,
  gasPrice: 23,
  activeTrades: 2,
  tokens: [
    {
      symbol: 'ETH',
      name: 'Ethereum',
      balance: '12.4567',
      value: '25,430.12',
      change: 2.34,
      price: 2042.67
    },
    {
      symbol: 'BTC',
      name: 'Bitcoin',
      balance: '0.4821',
      value: '18,920.45',
      change: -1.23,
      price: 39248.90
    },
    {
      symbol: 'SOL',
      name: 'Solana',
      balance: '89.234',
      value: '1,322.32',
      change: 7.89,
      price: 14.82
    }
  ]
});

const generateMockFriendWallet = (address: string): FriendWallet => ({
  address,
  name: `Friend ${Math.floor(Math.random() * 100)}`,
  totalValue: Math.floor(Math.random() * 100000) + 5000,
  dailyChange: (Math.random() - 0.5) * 20,
  weeklyChange: (Math.random() - 0.5) * 50,
  monthlyChange: (Math.random() - 0.5) * 100,
  topTokens: [
    {
      symbol: 'ETH',
      name: 'Ethereum',
      value: '12,430',
      percentage: '45.2',
      change: 2.34
    },
    {
      symbol: 'BTC',
      name: 'Bitcoin',
      value: '8,920',
      percentage: '32.1',
      change: -1.23
    },
    {
      symbol: 'SOL',
      name: 'Solana',
      value: '3,450',
      percentage: '12.4',
      change: 7.89
    }
  ],
  recentTrades: [
    {
      token: 'ETH',
      type: 'buy',
      amount: '2,340',
      timeAgo: '2h ago',
      profit: 5.67
    },
    {
      token: 'SOL',
      type: 'sell',
      amount: '890',
      timeAgo: '1d ago',
      profit: -2.34
    }
  ],
  aiInsight: Math.random() > 0.5 
    ? 'This wallet shows strong DeFi farming activity with consistent yield generation'
    : 'High-frequency trading pattern detected with focus on meme coins and quick profits'
});

const generateMockMarketData = (): MarketData[] => [
  {
    symbol: 'BTC',
    name: 'Bitcoin',
    price: 43420.67,
    change24h: 2.34,
    volume24h: 28500000000,
    marketCap: 850000000000,
    trend: 'bullish'
  },
  {
    symbol: 'ETH',
    name: 'Ethereum',
    price: 2567.89,
    change24h: 4.12,
    volume24h: 15200000000,
    marketCap: 308000000000,
    trend: 'bullish'
  },
  {
    symbol: 'BNB',
    name: 'BNB',
    price: 245.67,
    change24h: -1.23,
    volume24h: 890000000,
    marketCap: 37800000000,
    trend: 'neutral'
  },
  {
    symbol: 'SOL',
    name: 'Solana',
    price: 67.89,
    change24h: 8.45,
    volume24h: 2340000000,
    marketCap: 29200000000,
    trend: 'bullish'
  }
];

// Mining mock data generators
const generateMockHardwareInfo = (): HardwareInfo => ({
  gpus: [
    {
      id: 0,
      name: 'NVIDIA GeForce RTX 4080',
      memory: 16,
      powerLimit: 320,
      temperature: 67,
      fanSpeed: 65,
      coreClockMHz: 2505,
      memoryClockMHz: 22400,
      driverVersion: '531.68'
    },
    {
      id: 1,
      name: 'NVIDIA GeForce RTX 4070',
      memory: 12,
      powerLimit: 200,
      temperature: 62,
      fanSpeed: 58,
      coreClockMHz: 2475,
      memoryClockMHz: 21000,
      driverVersion: '531.68'
    }
  ],
  cpu: {
    name: 'AMD Ryzen 9 7950X',
    cores: 16,
    threads: 32,
    baseClock: 4.5,
    temperature: 45
  },
  totalMemory: 32,
  powerSupply: 850
});

const generateMockMiningStatus = (): MiningStatus => ({
  isRunning: false,
  coin: '',
  algorithm: '',
  pool: '',
  hashrate: 0,
  targetHashrate: 0,
  powerConsumption: 0,
  efficiency: 0,
  temperature: 0,
  fanSpeed: 0,
  acceptedShares: 0,
  rejectedShares: 0,
  uptime: '00:00:00'
});

const generateMockMiningEarnings = (): MiningEarnings => ({
  daily: 12.45,
  weekly: 87.15,
  monthly: 373.50,
  total: 1247.89,
  dailyCoin: 0.0034,
  currency: 'USD'
});

const generateMockMiningPools = (): MiningPool[] => [
  {
    name: 'Ethermine',
    url: 'eth-us-east1.nanopool.org',
    port: 9999,
    fee: 1.0,
    miners: 234567,
    hashrate: 245.7,
    luck: 103,
    lastBlock: '2h 34m ago',
    algorithm: 'Ethash'
  },
  {
    name: '2Miners',
    url: 'eth.2miners.com',
    port: 2020,
    fee: 1.0,
    miners: 187432,
    hashrate: 198.3,
    luck: 97,
    lastBlock: '1h 12m ago',
    algorithm: 'Ethash'
  },
  {
    name: 'F2Pool',
    url: 'eth.f2pool.com',
    port: 6688,
    fee: 2.5,
    miners: 156789,
    hashrate: 167.9,
    luck: 108,
    lastBlock: '3h 45m ago',
    algorithm: 'Ethash'
  },
  {
    name: 'NiceHash',
    url: 'stratum+tcp://daggerhashimoto.usa.nicehash.com',
    port: 3353,
    fee: 2.0,
    miners: 98765,
    hashrate: 123.4,
    luck: 94,
    lastBlock: '45m ago',
    algorithm: 'DaggerHashimoto'
  }
];

const generateMockAIRecommendations = (): AIRecommendation[] => [
  {
    type: 'optimization',
    message: 'Reduce GPU core clock by 50MHz to improve efficiency by 8%',
    confidence: 87,
    action: 'optimize_clocks'
  },
  {
    type: 'profitability',
    message: 'Switch to Ravencoin mining for 15% higher profitability this week',
    confidence: 92,
    action: 'switch_coin'
  },
  {
    type: 'warning',
    message: 'GPU temperature approaching 80°C, increase fan speed',
    confidence: 95,
    action: 'adjust_cooling'
  }
];

// Wallet Connection Functions
export const connectWallet = async (): Promise<void> => {
  try {
    // Check if MetaMask is installed
    if (typeof window.ethereum === 'undefined') {
      throw new Error('MetaMask is not installed');
    }

    // Request account access
    const accounts = await window.ethereum.request({
      method: 'eth_requestAccounts',
    });

    if (accounts.length === 0) {
      throw new Error('No accounts found');
    }

    // Store wallet address
    localStorage.setItem('walletAddress', accounts[0]);
    localStorage.setItem('walletConnected', 'true');

    console.log('Wallet connected:', accounts[0]);
  } catch (error) {
    console.error('Wallet connection failed:', error);
    throw error;
  }
};

export const disconnectWallet = (): void => {
  localStorage.removeItem('walletAddress');
  localStorage.removeItem('walletConnected');
};

export const isWalletConnected = (): boolean => {
  return localStorage.getItem('walletConnected') === 'true';
};

export const getWalletAddress = (): string | null => {
  return localStorage.getItem('walletAddress');
};

// Wallet Data Functions
export const getWalletBalances = async (): Promise<WalletData> => {
  try {
    // In production, this would make real API calls to blockchain APIs
    // For now, return mock data
    const walletAddress = getWalletAddress();
    if (!walletAddress) {
      throw new Error('No wallet connected');
    }

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    return generateMockWalletData();
  } catch (error) {
    console.error('Failed to get wallet balances:', error);
    throw error;
  }
};

// Trading Functions
export const performTrade = async (tradeData: TradeData): Promise<any> => {
  try {
    // In production, this would interact with DEX/CEX APIs
    console.log('Performing trade:', tradeData);

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Mock successful trade response
    return {
      success: true,
      transactionHash: '0x' + Math.random().toString(16).substr(2, 64),
      timestamp: new Date().toISOString(),
      ...tradeData
    };
  } catch (error) {
    console.error('Trade failed:', error);
    throw error;
  }
};

export const getGasPrice = async (): Promise<number> => {
  try {
    // In production, get real gas prices from Ethereum network
    return Math.floor(Math.random() * 50) + 15; // Random between 15-65 gwei
  } catch (error) {
    console.error('Failed to get gas price:', error);
    return 25; // Default fallback
  }
};

// Market Data Functions
export const getMarketData = async (): Promise<MarketData[]> => {
  try {
    // In production, fetch from CoinGecko, CoinMarketCap, etc.
    await new Promise(resolve => setTimeout(resolve, 500));
    return generateMockMarketData();
  } catch (error) {
    console.error('Failed to get market data:', error);
    throw error;
  }
};

export const getTokenPrice = async (symbol: string): Promise<number> => {
  try {
    const marketData = await getMarketData();
    const token = marketData.find(t => t.symbol === symbol);
    return token?.price || 0;
  } catch (error) {
    console.error(`Failed to get price for ${symbol}:`, error);
    return 0;
  }
};

// Friend Wallet Functions
export const getFriendWalletData = async (address: string): Promise<FriendWallet> => {
  try {
    // In production, this would query blockchain APIs for the address
    console.log('Fetching friend wallet data for:', address);

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500));

    return generateMockFriendWallet(address);
  } catch (error) {
    console.error('Failed to get friend wallet data:', error);
    throw error;
  }
};

export const trackWalletAddress = async (address: string): Promise<void> => {
  try {
    // Validate address format
    if (!address.match(/^0x[a-fA-F0-9]{40}$/)) {
      throw new Error('Invalid wallet address format');
    }

    // In production, add to tracking database
    console.log('Started tracking wallet:', address);
  } catch (error) {
    console.error('Failed to track wallet:', error);
    throw error;
  }
};

// Alert Functions
export const setTradeAlert = async (alert: Omit<TradeAlert, 'id'>): Promise<TradeAlert> => {
  try {
    const newAlert: TradeAlert = {
      id: Math.random().toString(36).substr(2, 9),
      ...alert
    };

    // In production, save to database
    console.log('Created trade alert:', newAlert);

    return newAlert;
  } catch (error) {
    console.error('Failed to create alert:', error);
    throw error;
  }
};

export const getTradeAlerts = async (): Promise<TradeAlert[]> => {
  try {
    // In production, fetch from database
    return [];
  } catch (error) {
    console.error('Failed to get alerts:', error);
    return [];
  }
};

// Security Functions
export const enableTwoFactor = async (): Promise<boolean> => {
  try {
    // In production, implement 2FA setup
    return true;
  } catch (error) {
    console.error('Failed to enable 2FA:', error);
    return false;
  }
};

export const verifyTransaction = async (txHash: string): Promise<boolean> => {
  try {
    // In production, verify transaction on blockchain
    console.log('Verifying transaction:', txHash);
    return true;
  } catch (error) {
    console.error('Transaction verification failed:', error);
    return false;
  }
};

// DeFi Integration Functions
export const getYieldFarmingOpportunities = async (): Promise<any[]> => {
  try {
    // In production, fetch from DeFi protocols
    return [
      {
        protocol: 'Uniswap V3',
        pair: 'ETH/USDC',
        apy: 12.4,
        tvl: 450000000,
        risk: 'medium'
      },
      {
        protocol: 'Curve',
        pair: 'stETH/ETH',
        apy: 8.7,
        tvl: 890000000,
        risk: 'low'
      }
    ];
  } catch (error) {
    console.error('Failed to get yield farming opportunities:', error);
    return [];
  }
};

// AI Analysis Functions
export const getAITradingSignals = async (): Promise<any[]> => {
  try {
    // In production, fetch from AI analysis service
    return [
      {
        token: 'ETH',
        signal: 'strong_buy',
        confidence: 89,
        reasoning: 'Bullish momentum with strong volume support',
        timeframe: '4h'
      },
      {
        token: 'SOL',
        signal: 'buy',
        confidence: 72,
        reasoning: 'Breaking resistance with ecosystem growth',
        timeframe: '1d'
      }
    ];
  } catch (error) {
    console.error('Failed to get AI signals:', error);
    return [];
  }
};

export const analyzeWalletBehavior = async (address: string): Promise<string> => {
  try {
    // In production, use AI to analyze wallet patterns
    const patterns = [
      'This wallet shows consistent DeFi yield farming behavior',
      'High-frequency trading pattern with focus on momentum trades',
      'Long-term holder with occasional profit-taking',
      'Active in meme coin trading with quick entries and exits',
      'Conservative portfolio with blue-chip tokens and staking'
    ];

    return patterns[Math.floor(Math.random() * patterns.length)];
  } catch (error) {
    console.error('Failed to analyze wallet behavior:', error);
    return 'Unable to analyze wallet behavior at this time';
  }
};

// Portfolio Analytics
export const getPortfolioAnalytics = async (): Promise<any> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/portfolio/analytics`);
    return response.data;
  } catch (error) {
    console.error('Failed to get portfolio analytics:', error);
    return null;
  }
};

// Mining API Functions
export const detectHardware = async (): Promise<HardwareInfo> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/mining/hardware`);
    return response.data.hardware;
  } catch (error) {
    console.error('Failed to detect hardware:', error);
    // Fallback to mock data if backend is unavailable
    await new Promise(resolve => setTimeout(resolve, 1500));
    return generateMockHardwareInfo();
  }
};

export const startMining = async (coin: string, pool: string): Promise<void> => {
  try {
    const walletAddress = getWalletAddress();
    if (!walletAddress) {
      throw new Error('No wallet connected');
    }

    await axios.post(`${API_BASE_URL}/mining/start`, {
      coin,
      pool,
      wallet_address: walletAddress
    }, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`
      }
    });

    // Store mining configuration locally as backup
    localStorage.setItem('miningConfig', JSON.stringify({ coin, pool, startTime: new Date().toISOString() }));
  } catch (error) {
    console.error('Failed to start mining:', error);
    // Fallback to local storage for demo
    await new Promise(resolve => setTimeout(resolve, 2000));
    localStorage.setItem('miningConfig', JSON.stringify({ coin, pool, startTime: new Date().toISOString() }));
  }
};

export const stopMining = async (): Promise<void> => {
  try {
    await axios.post(`${API_BASE_URL}/mining/stop`, {}, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`
      }
    });

    // Clear local configuration
    localStorage.removeItem('miningConfig');
  } catch (error) {
    console.error('Failed to stop mining:', error);
    // Fallback to local storage for demo
    await new Promise(resolve => setTimeout(resolve, 1000));
    localStorage.removeItem('miningConfig');
  }
};

export const getMiningStatus = async (): Promise<MiningStatus> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/mining/status`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`
      }
    });
    return response.data;
  } catch (error) {
    console.error('Failed to get mining status:', error);
    // Fallback to mock data based on local config
    const config = localStorage.getItem('miningConfig');
    
    if (config) {
      const { coin, pool, startTime } = JSON.parse(config);
      const startDate = new Date(startTime);
      const uptime = Math.floor((Date.now() - startDate.getTime()) / 1000);
      
      return {
        isRunning: true,
        coin,
        algorithm: coin === 'ETC' ? 'Ethash' : coin === 'RVN' ? 'Kawpow' : 'RandomX',
        pool,
        hashrate: 85.6 + Math.random() * 10,
        targetHashrate: 90,
        powerConsumption: 420 + Math.random() * 50,
        efficiency: 0.203,
        temperature: 68 + Math.random() * 8,
        fanSpeed: 65 + Math.random() * 10,
        acceptedShares: Math.floor(uptime / 30),
        rejectedShares: Math.floor(Math.random() * 3),
        uptime: new Date(uptime * 1000).toISOString().substr(11, 8)
      };
    }
    
    return generateMockMiningStatus();
  }
};

export const getMiningEarnings = async (): Promise<MiningEarnings> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/mining/earnings`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`
      }
    });
    return response.data;
  } catch (error) {
    console.error('Failed to get mining earnings:', error);
    // Fallback to mock data
    await new Promise(resolve => setTimeout(resolve, 500));
    return generateMockMiningEarnings();
  }
};

export const getMiningPools = async (): Promise<MiningPool[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/mining/pools`);
    return response.data.pools;
  } catch (error) {
    console.error('Failed to get mining pools:', error);
    // Fallback to mock data
    await new Promise(resolve => setTimeout(resolve, 300));
    return generateMockMiningPools();
  }
};

export const benchmarkHardware = async (): Promise<void> => {
  try {
    await axios.post(`${API_BASE_URL}/mining/benchmark`, {}, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`
      }
    });
  } catch (error) {
    console.error('Benchmark failed:', error);
    // Fallback to mock benchmark
    console.log('Running mock hardware benchmark...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    const benchmarkResults = {
      timestamp: new Date().toISOString(),
      ethash: 85.6,
      kawpow: 62.3,
      randomx: 18.7,
      completed: true
    };
    
    localStorage.setItem('benchmarkResults', JSON.stringify(benchmarkResults));
  }
};

export const getAIMiningRecommendations = async (): Promise<AIRecommendation[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/mining/ai-recommendations`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`
      }
    });
    return response.data.recommendations;
  } catch (error) {
    console.error('Failed to get AI recommendations:', error);
    // Fallback to mock data
    await new Promise(resolve => setTimeout(resolve, 800));
    return generateMockAIRecommendations();
  }
};

export const setMiningSchedule = async (schedule: MiningSchedule): Promise<void> => {
  try {
    // In production, configure mining schedule
    console.log('Setting mining schedule:', schedule);
    
    localStorage.setItem('miningSchedule', JSON.stringify(schedule));
  } catch (error) {
    console.error('Failed to set mining schedule:', error);
    throw error;
  }
};

export const getMiningSchedule = async (): Promise<MiningSchedule | null> => {
  try {
    const schedule = localStorage.getItem('miningSchedule');
    return schedule ? JSON.parse(schedule) : null;
  } catch (error) {
    console.error('Failed to get mining schedule:', error);
    return null;
  }
};

// --- Crypto Pool System API ---
export const createPool = async (data: any) => {
  const response = await axios.post(`${API_BASE_URL}/pools/create`, data);
  return response.data;
};

export const inviteToPool = async (data: any) => {
  const response = await axios.post(`${API_BASE_URL}/pools/invite`, data);
  return response.data;
};

export const joinPool = async (data: any) => {
  const response = await axios.post(`${API_BASE_URL}/pools/join`, data);
  return response.data;
};

export const getPoolStatus = async (poolId: string) => {
  const response = await axios.get(`${API_BASE_URL}/pools/status/${poolId}`);
  return response.data;
};

export const executePoolTrade = async (data: any) => {
  const response = await axios.post(`${API_BASE_URL}/pools/trade`, data);
  return response.data;
};

export const depositToPool = async (data: any) => {
  const response = await axios.post(`${API_BASE_URL}/pools/deposit`, data);
  return response.data;
};

export const withdrawFromPool = async (data: any) => {
  const response = await axios.post(`${API_BASE_URL}/pools/withdraw`, data);
  return response.data;
};

export const getPoolLogs = async (poolId: string) => {
  const response = await axios.get(`${API_BASE_URL}/pools/logs/${poolId}`);
  return response.data;
};

export const spinBoost = async (data: any): Promise<BoostStatus> => {
  const response = await axios.post(`${API_BASE_URL}/pools/boost/spin`, data);
  return response.data;
};

export const getBoostStatus = async (poolId: string): Promise<BoostStatus> => {
  const response = await axios.get(`${API_BASE_URL}/pools/boost/status/${poolId}`);
  return response.data;
};

export default {
  connectWallet,
  disconnectWallet,
  isWalletConnected,
  getWalletAddress,
  getWalletBalances,
  performTrade,
  getGasPrice,
  getMarketData,
  getTokenPrice,
  getFriendWalletData,
  trackWalletAddress,
  setTradeAlert,
  getTradeAlerts,
  enableTwoFactor,
  verifyTransaction,
  getYieldFarmingOpportunities,
  getAITradingSignals,
  analyzeWalletBehavior,
  getPortfolioAnalytics,
  detectHardware,
  startMining,
  stopMining,
  getMiningStatus,
  getMiningEarnings,
  getMiningPools,
  benchmarkHardware,
  getAIMiningRecommendations,
  setMiningSchedule,
  getMiningSchedule,
  createPool,
  inviteToPool,
  joinPool,
  getPoolStatus,
  executePoolTrade,
  depositToPool,
  withdrawFromPool,
  getPoolLogs,
  spinBoost,
  getBoostStatus
}; 