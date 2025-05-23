import React from 'react';
import './BoostSpinner.css';

interface BoostSpinnerProps {
  active: boolean;
  boost: number;
  countdown: number;
  onSpin: () => Promise<void>;
}

const BoostSpinner: React.FC<BoostSpinnerProps> = ({
  active,
  boost,
  countdown,
  onSpin
}) => {
  return (
    <div className="boost-spinner">
      <div className={`spinner-wheel ${active ? 'active' : ''}`}>
        <div className="spinner-center">
          {active ? (
            <div className="boost-active">
              <span className="boost-value">{boost}x</span>
              <span className="boost-label">BOOST</span>
            </div>
          ) : (
            <button
              className="spin-button"
              onClick={onSpin}
              disabled={active}
            >
              SPIN
            </button>
          )}
        </div>
      </div>
      <div className="countdown-timer">
        Next spin in: {Math.floor(countdown / 3600)}h {Math.floor((countdown % 3600) / 60)}m
      </div>
    </div>
  );
};

export default BoostSpinner; 