import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  CurrencyDollarIcon,
  ChartBarIcon,
  WalletIcon,
  UsersIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  BoltIcon,
  ShieldCheckIcon,
  ClockIcon,
  EyeIcon,
  PlusIcon,
  TrashIcon,
  CogIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  FireIcon,
  StarIcon,
  CpuChipIcon,
  PlayIcon,
  StopIcon,
  PresentationChartLineIcon,
  BeakerIcon,
  Cog6ToothIcon,
  BanknotesIcon,
  LightBulbIcon,
  PowerIcon,
  ComputerDesktopIcon
} from '@heroicons/react/24/outline';
import {
  connectWallet,
  getWalletBalances,
  performTrade,
  getFriendWalletData,
  getMarketData,
  setTradeAlert,
  WalletData,
  TradeData,
  FriendWallet,
  MarketData,
  TradeAlert,
  // Mining API functions
  detectHardware,
  startMining,
  stopMining,
  getMiningStatus,
  getMiningEarnings,
  getMiningPools,
  benchmarkHardware,
  getAIMiningRecommendations,
  setMiningSchedule,
  HardwareInfo,
  MiningStatus,
  MiningEarnings,
  MiningPool,
  AIRecommendation
} from '../services/cryptoApi';
import CryptoPoolsDashboard from '../components/CryptoPoolsDashboard';

interface ActiveTab {
  tab: 'trading' | 'friends' | 'mining' | 'pools';
}

const CryptoTrading: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'trading' | 'friends' | 'mining' | 'pools'>('trading');
  const [walletConnected, setWalletConnected] = useState(false);
  const [walletData, setWalletData] = useState<WalletData | null>(null);
  const [friendWallets, setFriendWallets] = useState<FriendWallet[]>([]);
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [tradeAlerts, setTradeAlerts] = useState<TradeAlert[]>([]);
  const [loading, setLoading] = useState(false);
  const [newFriendAddress, setNewFriendAddress] = useState('');
  const [selectedToken, setSelectedToken] = useState('');
  const [tradeAmount, setTradeAmount] = useState('');
  const [tradeType, setTradeType] = useState<'buy' | 'sell'>('buy');

  // Mining state
  const [hardwareInfo, setHardwareInfo] = useState<HardwareInfo | null>(null);
  const [miningStatus, setMiningStatus] = useState<MiningStatus | null>(null);
  const [miningEarnings, setMiningEarnings] = useState<MiningEarnings | null>(null);
  const [miningPools, setMiningPools] = useState<MiningPool[]>([]);
  const [aiRecommendations, setAiRecommendations] = useState<AIRecommendation[]>([]);
  const [selectedCoin, setSelectedCoin] = useState('');
  const [selectedPool, setSelectedPool] = useState('');
  const [miningRunning, setMiningRunning] = useState(false);
  const [benchmarkRunning, setBenchmarkRunning] = useState(false);

  // Pool state
  const [userPools, setUserPools] = useState<CryptoPool[]>([]);
  const [discoveredPools, setDiscoveredPools] = useState<CryptoPool[]>([]);
  const [selectedCryptoPool, setSelectedCryptoPool] = useState<CryptoPool | null>(null);
  const [poolCreateMode, setPoolCreateMode] = useState(false);
  const [newPoolName, setNewPoolName] = useState('');
  const [newPoolPrivacy, setNewPoolPrivacy] = useState<'private' | 'public'>('private');
  const [newPoolSplitMode, setNewPoolSplitMode] = useState<'equal' | 'proportional'>('equal');
  const [inviteAddress, setInviteAddress] = useState('');
  const [depositAmount, setDepositAmount] = useState('');
  const [depositToken, setDepositToken] = useState('USDC');
  const [boostSpinning, setBoostSpinning] = useState(false);
  const [boostResult, setBoostResult] = useState<number | null>(null);
  const [showBoostResult, setShowBoostResult] = useState(false);

  useEffect(() => {
    loadMarketData();
    if (walletConnected) {
      loadWalletData();
    }
    loadFriendWallets();
    if (activeTab === 'mining') {
      loadMiningData();
    }
  }, [walletConnected, activeTab]);

  // Mining data loading functions
  const loadMiningData = async () => {
    try {
      setLoading(true);
      const [hardware, status, earnings, pools, recommendations] = await Promise.all([
        detectHardware(),
        getMiningStatus(),
        getMiningEarnings(),
        getMiningPools(),
        getAIMiningRecommendations()
      ]);
      
      setHardwareInfo(hardware);
      setMiningStatus(status);
      setMiningEarnings(earnings);
      setMiningPools(pools);
      setAiRecommendations(recommendations);
      setMiningRunning(status.isRunning);
    } catch (error) {
      console.error('Failed to load mining data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartMining = async () => {
    if (!selectedCoin || !selectedPool) return;
    
    try {
      setLoading(true);
      await startMining(selectedCoin, selectedPool);
      setMiningRunning(true);
      await loadMiningData();
    } catch (error) {
      console.error('Failed to start mining:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStopMining = async () => {
    try {
      setLoading(true);
      await stopMining();
      setMiningRunning(false);
      await loadMiningData();
    } catch (error) {
      console.error('Failed to stop mining:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBenchmark = async () => {
    try {
      setBenchmarkRunning(true);
      await benchmarkHardware();
      await loadMiningData();
    } catch (error) {
      console.error('Benchmark failed:', error);
    } finally {
      setBenchmarkRunning(false);
    }
  };

  const loadMarketData = async () => {
    try {
      const data = await getMarketData();
      setMarketData(data);
    } catch (error) {
      console.error('Failed to load market data:', error);
    }
  };

  const loadWalletData = async () => {
    try {
      setLoading(true);
      const data = await getWalletBalances();
      setWalletData(data);
    } catch (error) {
      console.error('Failed to load wallet data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadFriendWallets = async () => {
    try {
      const saved = localStorage.getItem('friendWallets');
      if (saved) {
        const addresses = JSON.parse(saved);
        const walletData = await Promise.all(
          addresses.map(async (addr: string) => await getFriendWalletData(addr))
        );
        setFriendWallets(walletData);
      }
    } catch (error) {
      console.error('Failed to load friend wallets:', error);
    }
  };

  const handleConnectWallet = async () => {
    try {
      setLoading(true);
      await connectWallet();
      setWalletConnected(true);
      await loadWalletData();
    } catch (error) {
      console.error('Failed to connect wallet:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTrade = async () => {
    if (!selectedToken || !tradeAmount) return;
    
    try {
      setLoading(true);
      await performTrade({
        token: selectedToken,
        amount: parseFloat(tradeAmount),
        type: tradeType,
        slippage: 0.5
      });
      await loadWalletData();
      setTradeAmount('');
    } catch (error) {
      console.error('Trade failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const addFriendWallet = async () => {
    if (!newFriendAddress) return;
    
    try {
      setLoading(true);
      const walletData = await getFriendWalletData(newFriendAddress);
      setFriendWallets(prev => [...prev, walletData]);
      
      const saved = localStorage.getItem('friendWallets');
      const addresses = saved ? JSON.parse(saved) : [];
      addresses.push(newFriendAddress);
      localStorage.setItem('friendWallets', JSON.stringify(addresses));
      
      setNewFriendAddress('');
    } catch (error) {
      console.error('Failed to add friend wallet:', error);
    } finally {
      setLoading(false);
    }
  };

  const removeFriendWallet = (address: string) => {
    setFriendWallets(prev => prev.filter(w => w.address !== address));
    const saved = localStorage.getItem('friendWallets');
    if (saved) {
      const addresses = JSON.parse(saved).filter((addr: string) => addr !== address);
      localStorage.setItem('friendWallets', JSON.stringify(addresses));
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <motion.div 
        className="text-center py-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <h1 className="text-4xl font-bold gradient-text mb-4">
          CoresAi Crypto Trading Assistant
        </h1>
        <p className="text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed">
          Advanced AI-powered crypto trading, social analytics, and intelligent mining optimization
        </p>
      </motion.div>

      {/* Navigation Tabs */}
      <motion.div 
        className="flex justify-center mb-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.1 }}
      >
        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-2 flex">
          <button
            onClick={() => setActiveTab('trading')}
            className={`px-6 py-3 rounded-lg font-medium transition-all duration-300 flex items-center space-x-2 ${
              activeTab === 'trading'
                ? 'bg-gradient-to-r from-cyan-500 to-purple-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <ChartBarIcon className="h-5 w-5" />
            <span>Live Trading</span>
          </button>
          <button
            onClick={() => setActiveTab('friends')}
            className={`px-6 py-3 rounded-lg font-medium transition-all duration-300 flex items-center space-x-2 ${
              activeTab === 'friends'
                ? 'bg-gradient-to-r from-cyan-500 to-purple-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <UsersIcon className="h-5 w-5" />
            <span>Friend Tracker</span>
          </button>
          <button
            onClick={() => setActiveTab('mining')}
            className={`px-6 py-3 rounded-lg font-medium transition-all duration-300 flex items-center space-x-2 ${
              activeTab === 'mining'
                ? 'bg-gradient-to-r from-cyan-500 to-purple-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <CpuChipIcon className="h-5 w-5" />
            <span>AI Miner</span>
          </button>
          <button
            onClick={() => setActiveTab('pools')}
            className={`px-6 py-3 rounded-lg font-medium transition-all duration-300 flex items-center space-x-2 ${
              activeTab === 'pools'
                ? 'bg-gradient-to-r from-cyan-500 to-purple-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <CogIcon className="h-5 w-5" />
            <span>Crypto Pools</span>
          </button>
        </div>
      </motion.div>

      {/* AI Mining Tab */}
      {activeTab === 'mining' && (
        <motion.div 
          className="space-y-8"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* AI Status Monitor */}
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-white flex items-center">
                <LightBulbIcon className="h-6 w-6 mr-3 text-cyan-400" />
                CoresAi Mining Intelligence
              </h2>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                miningRunning 
                  ? 'bg-green-500/20 text-green-400' 
                  : 'bg-slate-700/50 text-slate-400'
              }`}>
                {miningRunning ? 'AI Optimizing' : 'Standby'}
              </div>
            </div>
            <p className="text-slate-300 text-lg">
              {miningRunning 
                ? "CoresAi is actively optimizing mining based on power usage, temperature, and market trends."
                : "CoresAi ready to optimize your mining operation. Connect hardware to begin."}
            </p>
          </div>

          {/* Hardware Detection & Control Panel */}
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Mining Control Panel - Left */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
              <h3 className="text-xl font-bold text-white mb-6 flex items-center">
                <ComputerDesktopIcon className="h-5 w-5 mr-2 text-cyan-400" />
                Mining Control
              </h3>

              {/* Hardware Info */}
              {hardwareInfo && (
                <div className="mb-6">
                  <h4 className="text-slate-400 text-sm font-medium mb-3">Detected Hardware</h4>
                  <div className="space-y-2">
                    {hardwareInfo.gpus.map((gpu, index) => (
                      <div key={index} className="bg-slate-700/30 rounded-lg p-3">
                        <div className="text-white font-medium text-sm">{gpu.name}</div>
                        <div className="text-slate-400 text-xs">
                          {gpu.memory}GB VRAM • {gpu.powerLimit}W TDP
                        </div>
                      </div>
                    ))}
                    <div className="bg-slate-700/30 rounded-lg p-3">
                      <div className="text-white font-medium text-sm">CPU</div>
                      <div className="text-slate-400 text-xs">
                        {hardwareInfo.cpu.name} • {hardwareInfo.cpu.cores} cores
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Coin Selection */}
              <div className="mb-4">
                <label className="block text-slate-400 text-sm mb-2">Mining Coin</label>
                <select
                  value={selectedCoin}
                  onChange={(e) => setSelectedCoin(e.target.value)}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white focus:border-cyan-400 focus:outline-none"
                >
                  <option value="">Auto-Select (AI Recommended)</option>
                  <option value="ETC">Ethereum Classic (ETC)</option>
                  <option value="RVN">Ravencoin (RVN)</option>
                  <option value="XMR">Monero (XMR)</option>
                  <option value="BTC">Bitcoin (BTC)</option>
                  <option value="LTC">Litecoin (LTC)</option>
                </select>
              </div>

              {/* Pool Selection */}
              <div className="mb-6">
                <label className="block text-slate-400 text-sm mb-2">Mining Pool</label>
                <select
                  value={selectedPool}
                  onChange={(e) => setSelectedPool(e.target.value)}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white focus:border-cyan-400 focus:outline-none"
                >
                  <option value="">Select Pool</option>
                  {miningPools.map((pool, index) => (
                    <option key={index} value={pool.name}>
                      {pool.name} ({pool.fee}% fee)
                    </option>
                  ))}
                </select>
              </div>

              {/* Control Buttons */}
              <div className="space-y-3">
                {!miningRunning ? (
                  <button
                    onClick={handleStartMining}
                    disabled={loading || !selectedCoin || !selectedPool}
                    className="w-full py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold rounded-lg hover:from-green-600 hover:to-emerald-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    <PlayIcon className="h-5 w-5" />
                    <span>{loading ? 'Starting...' : 'Start Mining'}</span>
                  </button>
                ) : (
                  <button
                    onClick={handleStopMining}
                    disabled={loading}
                    className="w-full py-3 bg-gradient-to-r from-red-500 to-rose-600 text-white font-bold rounded-lg hover:from-red-600 hover:to-rose-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    <StopIcon className="h-5 w-5" />
                    <span>{loading ? 'Stopping...' : 'Stop Mining'}</span>
                  </button>
                )}

                <button
                  onClick={handleBenchmark}
                  disabled={benchmarkRunning || miningRunning}
                  className="w-full py-2 bg-slate-700/50 text-slate-300 font-medium rounded-lg hover:bg-slate-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  <BeakerIcon className="h-4 w-4" />
                  <span>{benchmarkRunning ? 'Benchmarking...' : 'Benchmark Hardware'}</span>
                </button>

                <button
                  className="w-full py-2 bg-slate-700/50 text-slate-300 font-medium rounded-lg hover:bg-slate-700 transition-all duration-300 flex items-center justify-center space-x-2"
                >
                  <Cog6ToothIcon className="h-4 w-4" />
                  <span>Settings</span>
                </button>
              </div>
            </div>

            {/* Live Stats - Center */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
              <h3 className="text-xl font-bold text-white mb-6 flex items-center">
                <PresentationChartLineIcon className="h-5 w-5 mr-2 text-cyan-400" />
                Live Performance
              </h3>

              {miningStatus && (
                <div className="space-y-4">
                  {/* Hashrate */}
                  <div className="bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/20 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-blue-400 text-sm font-medium">Hashrate</span>
                      <BoltIcon className="h-4 w-4 text-blue-400" />
                    </div>
                    <div className="text-2xl font-bold text-white">
                      {miningStatus.hashrate} MH/s
                    </div>
                    <div className="text-blue-400 text-sm">
                      Target: {miningStatus.targetHashrate} MH/s
                    </div>
                  </div>

                  {/* Power Consumption */}
                  <div className="bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border border-yellow-500/20 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-yellow-400 text-sm font-medium">Power Usage</span>
                      <PowerIcon className="h-4 w-4 text-yellow-400" />
                    </div>
                    <div className="text-2xl font-bold text-white">
                      {miningStatus.powerConsumption}W
                    </div>
                    <div className="text-yellow-400 text-sm">
                      Efficiency: {miningStatus.efficiency} MH/W
                    </div>
                  </div>

                  {/* Temperature */}
                  <div className="bg-gradient-to-r from-red-500/10 to-pink-500/10 border border-red-500/20 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-red-400 text-sm font-medium">Temperature</span>
                      <FireIcon className="h-4 w-4 text-red-400" />
                    </div>
                    <div className="text-2xl font-bold text-white">
                      {miningStatus.temperature}°C
                    </div>
                    <div className="text-red-400 text-sm">
                      Fan: {miningStatus.fanSpeed}%
                    </div>
                  </div>

                  {/* Shares */}
                  <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-green-400 text-sm font-medium">Shares</span>
                      <CheckCircleIcon className="h-4 w-4 text-green-400" />
                    </div>
                    <div className="text-2xl font-bold text-white">
                      {miningStatus.acceptedShares}
                    </div>
                    <div className="text-green-400 text-sm">
                      Rejected: {miningStatus.rejectedShares}
                    </div>
                  </div>
                </div>
              )}

              {!miningRunning && (
                <div className="text-center py-12">
                  <div className="inline-flex p-4 rounded-full bg-slate-700/50 mb-4">
                    <CpuChipIcon className="h-12 w-12 text-slate-400" />
                  </div>
                  <h4 className="text-lg font-semibold text-white mb-2">Mining Stopped</h4>
                  <p className="text-slate-400">Start mining to see live performance data</p>
                </div>
              )}
            </div>

            {/* Earnings & AI Recommendations - Right */}
            <div className="space-y-6">
              {/* Earnings */}
              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
                <h3 className="text-xl font-bold text-white mb-6 flex items-center">
                  <BanknotesIcon className="h-5 w-5 mr-2 text-cyan-400" />
                  Earnings
                </h3>

                {miningEarnings && (
                  <div className="space-y-4">
                    <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-lg p-4">
                      <div className="text-center">
                        <div className="text-green-400 text-sm font-medium mb-1">Today</div>
                        <div className="text-2xl font-bold text-white">
                          ${miningEarnings.daily.toFixed(2)}
                        </div>
                        <div className="text-green-400 text-xs">
                          {miningEarnings.dailyCoin} {selectedCoin}
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center">
                        <div className="text-slate-400 text-sm">Weekly</div>
                        <div className="text-white font-bold">${miningEarnings.weekly.toFixed(2)}</div>
                      </div>
                      <div className="text-center">
                        <div className="text-slate-400 text-sm">Monthly</div>
                        <div className="text-white font-bold">${miningEarnings.monthly.toFixed(2)}</div>
                      </div>
                    </div>

                    <div className="text-center">
                      <div className="text-slate-400 text-sm">Total Mined</div>
                      <div className="text-white font-bold text-lg">${miningEarnings.total.toFixed(2)}</div>
                    </div>
                  </div>
                )}

                {!miningEarnings && (
                  <div className="text-center py-8">
                    <div className="text-slate-400">No earnings data yet</div>
                    <div className="text-slate-500 text-sm">Start mining to track earnings</div>
                  </div>
                )}
              </div>

              {/* AI Recommendations */}
              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
                <h3 className="text-xl font-bold text-white mb-6 flex items-center">
                  <StarIcon className="h-5 w-5 mr-2 text-purple-400" />
                  AI Recommendations
                </h3>

                <div className="space-y-3">
                  {aiRecommendations.map((rec, index) => (
                    <div key={index} className={`p-4 rounded-lg border ${
                      rec.type === 'optimization' 
                        ? 'bg-blue-500/10 border-blue-500/20' 
                        : rec.type === 'profitability'
                        ? 'bg-green-500/10 border-green-500/20'
                        : 'bg-yellow-500/10 border-yellow-500/20'
                    }`}>
                      <div className="flex items-center mb-2">
                        <LightBulbIcon className={`h-4 w-4 mr-2 ${
                          rec.type === 'optimization' ? 'text-blue-400' : 
                          rec.type === 'profitability' ? 'text-green-400' : 'text-yellow-400'
                        }`} />
                        <span className={`text-sm font-medium ${
                          rec.type === 'optimization' ? 'text-blue-400' : 
                          rec.type === 'profitability' ? 'text-green-400' : 'text-yellow-400'
                        }`}>
                          {rec.type === 'optimization' ? 'Optimization' : 
                           rec.type === 'profitability' ? 'Profitability' : 'Warning'}
                        </span>
                      </div>
                      <p className="text-slate-300 text-sm">{rec.message}</p>
                      {rec.confidence && (
                        <div className="text-xs text-slate-400 mt-2">
                          Confidence: {rec.confidence}%
                        </div>
                      )}
                    </div>
                  ))}

                  {aiRecommendations.length === 0 && (
                    <div className="text-center py-8">
                      <div className="text-slate-400">No recommendations yet</div>
                      <div className="text-slate-500 text-sm">AI will analyze your mining setup</div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Pool Stats & Performance History */}
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Pool Statistics */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
              <h3 className="text-xl font-bold text-white mb-6 flex items-center">
                <CogIcon className="h-5 w-5 mr-2 text-cyan-400" />
                Pool Statistics
              </h3>

              {selectedPool && miningPools.length > 0 && (
                <div className="space-y-4">
                  {(() => {
                    const pool = miningPools.find(p => p.name === selectedPool);
                    return pool ? (
                      <>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="text-center">
                            <div className="text-slate-400 text-sm">Pool Fee</div>
                            <div className="text-white font-bold">{pool.fee}%</div>
                          </div>
                          <div className="text-center">
                            <div className="text-slate-400 text-sm">Miners</div>
                            <div className="text-white font-bold">{pool.miners.toLocaleString()}</div>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                          <div className="text-center">
                            <div className="text-slate-400 text-sm">Pool Hashrate</div>
                            <div className="text-white font-bold">{pool.hashrate} TH/s</div>
                          </div>
                          <div className="text-center">
                            <div className="text-slate-400 text-sm">Luck</div>
                            <div className={`font-bold ${pool.luck >= 100 ? 'text-green-400' : 'text-yellow-400'}`}>
                              {pool.luck}%
                            </div>
                          </div>
                        </div>

                        <div className="text-center">
                          <div className="text-slate-400 text-sm">Last Block</div>
                          <div className="text-white font-bold">{pool.lastBlock}</div>
                        </div>
                      </>
                    ) : null;
                  })()}
                </div>
              )}

              {!selectedPool && (
                <div className="text-center py-8">
                  <div className="text-slate-400">No pool selected</div>
                  <div className="text-slate-500 text-sm">Select a mining pool to view statistics</div>
                </div>
              )}
            </div>

            {/* Performance History Chart */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
              <h3 className="text-xl font-bold text-white mb-6 flex items-center">
                <PresentationChartLineIcon className="h-5 w-5 mr-2 text-cyan-400" />
                Performance History
              </h3>

              {miningStatus && miningStatus.history && (
                <div className="h-48">
                  {/* Simple chart placeholder - in production, use recharts or similar */}
                  <div className="w-full h-full bg-slate-700/30 rounded-lg flex items-center justify-center">
                    <div className="text-center">
                      <PresentationChartLineIcon className="h-12 w-12 text-slate-400 mx-auto mb-2" />
                      <div className="text-slate-400">Chart Visualization</div>
                      <div className="text-slate-500 text-sm">Hashrate over time</div>
                    </div>
                  </div>
                </div>
              )}

              {!miningStatus?.history && (
                <div className="h-48 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-slate-400">No performance data</div>
                    <div className="text-slate-500 text-sm">Start mining to track performance</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* Live Trading Tab */}
      {activeTab === 'trading' && (
        <motion.div 
          className="space-y-8"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Wallet Connection */}
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
              <WalletIcon className="h-6 w-6 mr-3 text-cyan-400" />
              Wallet Connection
            </h2>
            
            {!walletConnected ? (
              <div className="text-center py-8">
                <div className="mb-6">
                  <div className="inline-flex p-4 rounded-full bg-slate-700/50 mb-4">
                    <WalletIcon className="h-12 w-12 text-cyan-400" />
                  </div>
                  <p className="text-slate-400 mb-6">Connect your wallet to start trading</p>
                  <div className="flex flex-wrap justify-center gap-4 mb-6">
                    <div className="flex items-center space-x-2 text-sm text-slate-300">
                      <ShieldCheckIcon className="h-4 w-4 text-green-400" />
                      <span>MetaMask</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-slate-300">
                      <ShieldCheckIcon className="h-4 w-4 text-green-400" />
                      <span>WalletConnect</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-slate-300">
                      <ShieldCheckIcon className="h-4 w-4 text-green-400" />
                      <span>Ledger</span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={handleConnectWallet}
                  disabled={loading}
                  className="px-8 py-3 bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-bold rounded-lg hover:from-cyan-600 hover:to-purple-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Connecting...' : 'Connect Wallet'}
                </button>
              </div>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Portfolio Value */}
                <div className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <CurrencyDollarIcon className="h-6 w-6 text-green-400" />
                    <span className="text-green-400 text-sm font-medium">Total Value</span>
                  </div>
                  <div className="text-2xl font-bold text-white">
                    ${walletData?.totalValue.toLocaleString() || '0.00'}
                  </div>
                  <div className="text-green-400 text-sm">
                    +{walletData?.dailyChange || '0.00'}% (24h)
                  </div>
                </div>

                {/* Gas Tracker */}
                <div className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/20 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <BoltIcon className="h-6 w-6 text-blue-400" />
                    <span className="text-blue-400 text-sm font-medium">Gas Price</span>
                  </div>
                  <div className="text-2xl font-bold text-white">
                    {walletData?.gasPrice || '0'} gwei
                  </div>
                  <div className="text-blue-400 text-sm">ETH Network</div>
                </div>

                {/* Active Trades */}
                <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <ClockIcon className="h-6 w-6 text-purple-400" />
                    <span className="text-purple-400 text-sm font-medium">Active Trades</span>
                  </div>
                  <div className="text-2xl font-bold text-white">
                    {walletData?.activeTrades || 0}
                  </div>
                  <div className="text-purple-400 text-sm">Orders Pending</div>
                </div>

                {/* Security Status */}
                <div className="bg-gradient-to-br from-orange-500/10 to-red-500/10 border border-orange-500/20 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <ShieldCheckIcon className="h-6 w-6 text-orange-400" />
                    <span className="text-orange-400 text-sm font-medium">Security</span>
                  </div>
                  <div className="text-2xl font-bold text-white">Secure</div>
                  <div className="text-orange-400 text-sm">2FA Enabled</div>
                </div>
              </div>
            )}
          </div>

          {/* Trading Interface */}
          {walletConnected && (
            <div className="grid lg:grid-cols-2 gap-8">
              {/* Quick Trade */}
              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
                <h3 className="text-xl font-bold text-white mb-6 flex items-center">
                  <ArrowTrendingUpIcon className="h-5 w-5 mr-2 text-cyan-400" />
                  Quick Trade
                </h3>
                
                <div className="space-y-4">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setTradeType('buy')}
                      className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all duration-300 ${
                        tradeType === 'buy'
                          ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                          : 'bg-slate-700/50 text-slate-400 border border-slate-600'
                      }`}
                    >
                      Buy
                    </button>
                    <button
                      onClick={() => setTradeType('sell')}
                      className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all duration-300 ${
                        tradeType === 'sell'
                          ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                          : 'bg-slate-700/50 text-slate-400 border border-slate-600'
                      }`}
                    >
                      Sell
                    </button>
                  </div>

                  <div>
                    <label className="block text-slate-400 text-sm mb-2">Token</label>
                    <select
                      value={selectedToken}
                      onChange={(e) => setSelectedToken(e.target.value)}
                      className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white focus:border-cyan-400 focus:outline-none"
                    >
                      <option value="">Select Token</option>
                      <option value="ETH">Ethereum (ETH)</option>
                      <option value="BTC">Bitcoin (BTC)</option>
                      <option value="BNB">BNB</option>
                      <option value="SOL">Solana (SOL)</option>
                      <option value="MATIC">Polygon (MATIC)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-400 text-sm mb-2">Amount</label>
                    <input
                      type="number"
                      value={tradeAmount}
                      onChange={(e) => setTradeAmount(e.target.value)}
                      placeholder="0.00"
                      className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white focus:border-cyan-400 focus:outline-none"
                    />
                  </div>

                  <button
                    onClick={handleTrade}
                    disabled={loading || !selectedToken || !tradeAmount}
                    className={`w-full py-3 rounded-lg font-bold transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed ${
                      tradeType === 'buy'
                        ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:from-green-600 hover:to-emerald-700'
                        : 'bg-gradient-to-r from-red-500 to-rose-600 text-white hover:from-red-600 hover:to-rose-700'
                    }`}
                  >
                    {loading ? 'Processing...' : `${tradeType === 'buy' ? 'Buy' : 'Sell'} ${selectedToken}`}
                  </button>
                </div>
              </div>

              {/* AI Insights */}
              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
                <h3 className="text-xl font-bold text-white mb-6 flex items-center">
                  <FireIcon className="h-5 w-5 mr-2 text-purple-400" />
                  AI Trading Insights
                </h3>
                
                <div className="space-y-4">
                  <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-lg p-4">
                    <div className="flex items-center mb-2">
                      <ArrowTrendingUpIcon className="h-4 w-4 text-green-400 mr-2" />
                      <span className="text-green-400 font-medium">Strong Buy Signal</span>
                    </div>
                    <p className="text-slate-300 text-sm">ETH showing bullish momentum with 89% confidence</p>
                  </div>

                  <div className="bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/20 rounded-lg p-4">
                    <div className="flex items-center mb-2">
                      <EyeIcon className="h-4 w-4 text-blue-400 mr-2" />
                      <span className="text-blue-400 font-medium">Market Watch</span>
                    </div>
                    <p className="text-slate-300 text-sm">SOL volume increased 234% in last 4 hours</p>
                  </div>

                  <div className="bg-gradient-to-r from-orange-500/10 to-red-500/10 border border-orange-500/20 rounded-lg p-4">
                    <div className="flex items-center mb-2">
                      <ExclamationTriangleIcon className="h-4 w-4 text-orange-400 mr-2" />
                      <span className="text-orange-400 font-medium">Risk Alert</span>
                    </div>
                    <p className="text-slate-300 text-sm">High volatility detected in meme coin sector</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Holdings & Performance */}
          {walletConnected && walletData && (
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
              <h3 className="text-xl font-bold text-white mb-6 flex items-center">
                <ChartBarIcon className="h-5 w-5 mr-2 text-cyan-400" />
                Portfolio Holdings
              </h3>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-600">
                      <th className="text-left py-3 px-4 text-slate-400 font-medium">Token</th>
                      <th className="text-left py-3 px-4 text-slate-400 font-medium">Balance</th>
                      <th className="text-left py-3 px-4 text-slate-400 font-medium">Value</th>
                      <th className="text-left py-3 px-4 text-slate-400 font-medium">24h Change</th>
                      <th className="text-left py-3 px-4 text-slate-400 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {walletData.tokens?.map((token, index) => (
                      <tr key={index} className="border-b border-slate-700/50">
                        <td className="py-4 px-4">
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-cyan-400 to-purple-600 flex items-center justify-center">
                              <span className="text-white text-xs font-bold">{token.symbol.slice(0, 2)}</span>
                            </div>
                            <div>
                              <div className="text-white font-medium">{token.symbol}</div>
                              <div className="text-slate-400 text-sm">{token.name}</div>
                            </div>
                          </div>
                        </td>
                        <td className="py-4 px-4 text-white">{token.balance}</td>
                        <td className="py-4 px-4 text-white">${token.value}</td>
                        <td className="py-4 px-4">
                          <span className={`flex items-center ${token.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {token.change >= 0 ? (
                              <ArrowTrendingUpIcon className="h-4 w-4 mr-1" />
                            ) : (
                              <ArrowTrendingDownIcon className="h-4 w-4 mr-1" />
                            )}
                            {Math.abs(token.change)}%
                          </span>
                        </td>
                        <td className="py-4 px-4">
                          <div className="flex space-x-2">
                            <button className="px-3 py-1 bg-green-500/20 text-green-400 rounded text-sm hover:bg-green-500/30 transition-colors">
                              Buy
                            </button>
                            <button className="px-3 py-1 bg-red-500/20 text-red-400 rounded text-sm hover:bg-red-500/30 transition-colors">
                              Sell
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </motion.div>
      )}

      {/* Friend Tracker Tab */}
      {activeTab === 'friends' && (
        <motion.div 
          className="space-y-8"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Add Friend Wallet */}
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
              <PlusIcon className="h-6 w-6 mr-3 text-cyan-400" />
              Add Friend Wallet
            </h2>
            
            <div className="flex space-x-4">
              <input
                type="text"
                value={newFriendAddress}
                onChange={(e) => setNewFriendAddress(e.target.value)}
                placeholder="Enter wallet address or ENS name"
                className="flex-1 bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white focus:border-cyan-400 focus:outline-none"
              />
              <button
                onClick={addFriendWallet}
                disabled={loading || !newFriendAddress}
                className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-bold rounded-lg hover:from-cyan-600 hover:to-purple-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Adding...' : 'Add Wallet'}
              </button>
            </div>
          </div>

          {/* Friend Wallets Grid */}
          <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
            {friendWallets.map((wallet, index) => (
              <motion.div
                key={wallet.address}
                className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 hover:border-slate-600 transition-all duration-300"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                {/* Wallet Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-cyan-400 to-purple-600 flex items-center justify-center">
                      <span className="text-white font-bold text-sm">
                        {wallet.name ? wallet.name[0].toUpperCase() : wallet.address.slice(0, 2)}
                      </span>
                    </div>
                    <div>
                      <div className="text-white font-medium">
                        {wallet.name || `Wallet ${index + 1}`}
                      </div>
                      <div className="text-slate-400 text-sm">
                        {wallet.address.slice(0, 6)}...{wallet.address.slice(-4)}
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => removeFriendWallet(wallet.address)}
                    className="text-slate-400 hover:text-red-400 transition-colors"
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                </div>

                {/* Wallet Stats */}
                <div className="space-y-4">
                  <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-green-400 text-sm font-medium">Total Value</span>
                      <CurrencyDollarIcon className="h-4 w-4 text-green-400" />
                    </div>
                    <div className="text-xl font-bold text-white">
                      ${wallet.totalValue.toLocaleString()}
                    </div>
                    <div className={`text-sm ${wallet.dailyChange >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {wallet.dailyChange >= 0 ? '+' : ''}{wallet.dailyChange}% (24h)
                    </div>
                  </div>

                  {/* Top Holdings */}
                  <div>
                    <h4 className="text-slate-400 text-sm font-medium mb-3">Top Holdings</h4>
                    <div className="space-y-2">
                      {wallet.topTokens?.slice(0, 3).map((token, tokenIndex) => (
                        <div key={tokenIndex} className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <div className="w-6 h-6 rounded-full bg-gradient-to-r from-cyan-400 to-purple-600 flex items-center justify-center">
                              <span className="text-white text-xs font-bold">{token.symbol.slice(0, 1)}</span>
                            </div>
                            <span className="text-slate-300 text-sm">{token.symbol}</span>
                          </div>
                          <div className="text-right">
                            <div className="text-white text-sm">${token.value}</div>
                            <div className="text-slate-400 text-xs">{token.percentage}%</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* AI Insights */}
                  <div className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20 rounded-lg p-3">
                    <div className="flex items-center mb-2">
                      <StarIcon className="h-4 w-4 text-purple-400 mr-2" />
                      <span className="text-purple-400 text-sm font-medium">AI Insight</span>
                    </div>
                    <p className="text-slate-300 text-xs">{wallet.aiInsight}</p>
                  </div>

                  {/* Recent Activity */}
                  <div>
                    <h4 className="text-slate-400 text-sm font-medium mb-3">Recent Activity</h4>
                    <div className="space-y-2">
                      {wallet.recentTrades?.slice(0, 2).map((trade, tradeIndex) => (
                        <div key={tradeIndex} className="flex items-center justify-between text-sm">
                          <div className="flex items-center space-x-2">
                            <div className={`w-2 h-2 rounded-full ${trade.type === 'buy' ? 'bg-green-400' : 'bg-red-400'}`} />
                            <span className="text-slate-300">{trade.type.toUpperCase()} {trade.token}</span>
                          </div>
                          <div className="text-right">
                            <div className="text-white">${trade.amount}</div>
                            <div className="text-slate-400 text-xs">{trade.timeAgo}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Empty State */}
          {friendWallets.length === 0 && (
            <div className="text-center py-12">
              <div className="inline-flex p-4 rounded-full bg-slate-700/50 mb-4">
                <UsersIcon className="h-12 w-12 text-slate-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">No Friend Wallets Added</h3>
              <p className="text-slate-400 mb-6">Start tracking your friends' crypto earnings by adding their wallet addresses</p>
            </div>
          )}
        </motion.div>
      )}

      {/* Crypto Pools Tab */}
      {activeTab === 'pools' && (
        <CryptoPoolsDashboard />
      )}
    </div>
  );
};

export default CryptoTrading; 