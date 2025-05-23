import React, { useState, useRef } from 'react';
import './BoostSpinner.css';

interface BoostSpinnerProps {
  isHost: boolean;
  canSpin: boolean;
  onSpin: () => Promise<number>;
  boostResult: number | null;
  countdown: number; // seconds until next spin
  boostActive: boolean;
  boostEndsIn: number; // seconds left for boost
  logo?: React.ReactNode;
}

const BOOST_SEGMENTS = [
  { value: 250, color: '#FFD600' }, // Yellow
  { value: 300, color: '#00B8FF' }, // Blue
  { value: 450, color: '#FF1744' }, // Red
  { value: 500, color: '#B620E0' }, // Purple
];

const BoostSpinner: React.FC<BoostSpinnerProps> = ({
  isHost,
  canSpin,
  onSpin,
  boostResult,
  countdown,
  boostActive,
  boostEndsIn,
  logo,
}) => {
  const [spinning, setSpinning] = useState(false);
  const [angle, setAngle] = useState(0);
  const spinnerRef = useRef<HTMLDivElement>(null);

  const handleSpin = async () => {
    if (!canSpin || spinning) return;
    setSpinning(true);
    // Simulate spin animation
    const result = await onSpin();
    // Find the segment index
    const idx = BOOST_SEGMENTS.findIndex(s => s.value === result);
    const spins = 6; // Full spins before landing
    const segmentAngle = 360 / BOOST_SEGMENTS.length;
    const finalAngle = 360 * spins + idx * segmentAngle + segmentAngle / 2;
    setAngle(finalAngle);
    setTimeout(() => setSpinning(false), 3200);
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="boost-spinner-container">
      <div className="boost-spinner-title">CoresAi Boost Engine</div>
      <div className="boost-spinner-wheel-wrapper">
        <div
          className={`boost-spinner-wheel${spinning ? ' spinning' : ''}`}
          ref={spinnerRef}
          style={{ transform: `rotate(${angle}deg)` }}
        >
          {BOOST_SEGMENTS.map((seg, i) => {
            const start = (i * 360) / BOOST_SEGMENTS.length;
            const end = ((i + 1) * 360) / BOOST_SEGMENTS.length;
            return (
              <div
                key={seg.value}
                className="boost-spinner-segment"
                style={{
                  background: `conic-gradient(${seg.color} 0deg 90deg, transparent 90deg 360deg)`,
                  transform: `rotate(${start}deg)`
                }}
              >
                <span
                  className="boost-spinner-segment-label"
                  style={{ color: seg.color }}
                >
                  +{seg.value}%
                </span>
              </div>
            );
          })}
          <div className="boost-spinner-center">
            {logo || <span className="coresai-logo-text">CoresAi</span>}
          </div>
        </div>
        <div className="boost-spinner-pointer" />
      </div>
      <button
        className="boost-spinner-spin-btn"
        onClick={handleSpin}
        disabled={!canSpin || spinning || !isHost}
      >
        {spinning ? 'Spinning...' : 'Spin for Boost'}
      </button>
      {boostResult !== null && (
        <div className="boost-spinner-result">
          BOOSTED EARNINGS +{boostResult}%
        </div>
      )}
      {boostActive ? (
        <div className="boost-spinner-countdown">
          Boost active! Ends in: {formatTime(boostEndsIn)}
        </div>
      ) : (
        <div className="boost-spinner-countdown">
          Next spin in: {formatTime(countdown)}
        </div>
      )}
    </div>
  );
};

export default BoostSpinner; 