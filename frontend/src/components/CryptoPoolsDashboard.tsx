import React, { useState } from 'react';
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

const CryptoPoolsDashboard: React.FC = () => {
  const [selectedPool, setSelectedPool] = useState(mockPools[0]);
  const [boostResult, setBoostResult] = useState<number | null>(null);
  const [boostActive, setBoostActive] = useState(false);
  const [boostEndsIn, setBoostEndsIn] = useState(3600); // 1h
  const [countdown, setCountdown] = useState(86400); // 1 day

  // Simulate boost spin
  const handleSpin = async () => {
    const results = [250, 300, 450, 500];
    const result = results[Math.floor(Math.random() * results.length)];
    setBoostResult(result);
    setBoostActive(true);
    setBoostEndsIn(604800); // 7 days
    setCountdown(604800); // lock for 14 days
    return result;
  };

  return (
    <div className="crypto-pools-dashboard">
      <aside className="pools-sidebar">
        <div className="sidebar-title">My Pools</div>
        <ul>
          {mockPools.map(pool => (
            <li
              key={pool.id}
              className={selectedPool.id === pool.id ? 'active' : ''}
              onClick={() => setSelectedPool(pool)}
            >
              {pool.name}
            </li>
          ))}
        </ul>
        <div className="sidebar-title">Discover Pools</div>
        <ul>
          <li>Public Pool X</li>
          <li>Public Pool Y</li>
        </ul>
      </aside>
      <main className="pools-main">
        <div className="pools-top-panel">
          <div className="pool-name">{selectedPool.name}</div>
          <div className="pool-size">${selectedPool.size.toLocaleString()} USD</div>
          <div className="pool-return">Return: {selectedPool.returnPct}%</div>
          <div className="pool-members">Members: {selectedPool.members}</div>
        </div>
        <div className="pools-center-panel">
          <div className="trade-feed">
            <div className="feed-title">Live Trade Feed</div>
            <ul>
              {mockFeed.map((item, i) => (
                <li key={i}><b>{item.action}:</b> {item.desc} <span className="feed-time">{item.time}</span></li>
              ))}
            </ul>
          </div>
          <div className="member-list">
            <div className="member-title">Members</div>
            <ul>
              {mockMembers.map((m, i) => (
                <li key={i} className={m.status}>{m.name} <span className="member-status">{m.status}</span> <span className="member-payout">${m.payout}</span></li>
              ))}
            </ul>
          </div>
        </div>
        <div className="pools-right-panel">
          <div className="earnings-chart">[Earnings Chart Placeholder]</div>
          <div className="member-payouts">[Member Payouts Placeholder]</div>
          <BoostSpinner
            isHost={true}
            canSpin={!boostActive}
            onSpin={handleSpin}
            boostResult={boostResult}
            countdown={countdown}
            boostActive={boostActive}
            boostEndsIn={boostEndsIn}
          />
        </div>
        <div className="pools-bottom-panel">
          <button className="pools-btn">Deposit</button>
          <button className="pools-btn">Trade</button>
          <button className="pools-btn">Withdraw</button>
        </div>
      </main>
    </div>
  );
};

export default CryptoPoolsDashboard; 