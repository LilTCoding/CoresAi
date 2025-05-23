import React, { useState, useEffect } from 'react';
import cryptoApi, { Pool, BoostStatus } from '../services/cryptoApi';
import BoostSpinner from './BoostSpinner';
import './CryptoPoolsDashboard.css';

const mockPools = [
  { name: 'Alpha Pool', size: 12000, returnPct: 18.2, members: 5, id: '1' },
  { name: 'Beta Syndicate', size: 5400, returnPct: 7.9, members: 3, id: '2' },
];

const mockFeed = [
  { action: 'Trade', desc: 'Buy 2.5 ETH', time: '2m ago' },
  { action: 'Deposit', desc: '1,000 USDC', time: '10m ago' },
  { action: 'Withdraw', desc: '0.5 ETH', time: '1h ago' },
];

const mockMembers = [
  { name: '0xA1...B2', status: 'active', payout: 3200 },
  { name: '0xC3...D4', status: 'idle', payout: 2100 },
  { name: '0xE5...F6', status: 'active', payout: 1800 },
];

interface CryptoPoolsDashboardProps {
  marketData: any;
}

const CryptoPoolsDashboard: React.FC<CryptoPoolsDashboardProps> = ({ marketData }) => {
  const [pools, setPools] = useState<Pool[]>([]);
  const [selectedPool, setSelectedPool] = useState<string | null>(null);
  const [boostStatus, setBoostStatus] = useState<BoostStatus>({
    boost: 0,
    boost_active: false,
    boost_ends_in: 0,
    countdown: 0
  });

  const handleBoostSpin = async () => {
    if (!selectedPool) return;
    try {
      const result = await cryptoApi.spinBoost({ poolId: selectedPool });
      setBoostStatus(result);
    } catch (error) {
      console.error('Failed to spin boost:', error);
    }
  };

  const handlePoolSelect = async (poolId: string) => {
    setSelectedPool(poolId);
    try {
      const status = await cryptoApi.getBoostStatus(poolId);
      setBoostStatus(status);
    } catch (error) {
      console.error('Failed to get boost status:', error);
    }
  };

  return (
    <div className="crypto-pools-dashboard">
      <div className="dashboard-header">
        <h1>Crypto Pools Dashboard</h1>
        <div className="market-summary">
          <h3>Market Overview</h3>
          {marketData && (
            <div className="market-stats">
              <span>BTC: ${marketData.btc_price}</span>
              <span>ETH: ${marketData.eth_price}</span>
              <span>24h Volume: ${marketData.volume_24h}</span>
            </div>
          )}
        </div>
      </div>

      <div className="dashboard-content">
        <div className="pools-list">
          <h2>Your Pools</h2>
          {pools.map((pool) => (
            <div
              key={pool.id}
              className={`pool-card ${selectedPool === pool.id ? 'selected' : ''}`}
              onClick={() => handlePoolSelect(pool.id)}
            >
              <h3>{pool.name}</h3>
              <div className="pool-stats">
                <p>Size: ${pool.size}</p>
                <p>Return: {pool.returnPct}%</p>
                <p>Members: {pool.members}</p>
                <p>Privacy: {pool.privacy}</p>
                <p>Split Mode: {pool.split_mode}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="boost-section">
          <h2>Boost Spinner</h2>
          <BoostSpinner
            active={boostStatus.boost_active}
            boost={boostStatus.boost}
            countdown={boostStatus.countdown}
            onSpin={handleBoostSpin}
          />
          {boostStatus.boost_active && (
            <div className="boost-info">
              <p>Current Boost: {boostStatus.boost}x</p>
              <p>Ends in: {boostStatus.boost_ends_in}s</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CryptoPoolsDashboard; 