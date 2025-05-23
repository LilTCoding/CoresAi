import React from 'react';
import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';

interface BackendHealth {
  production: boolean;
  streaming: boolean;
}

interface BackendStatusProps {
  health: BackendHealth;
}

const BackendStatus: React.FC<BackendStatusProps> = ({ health }) => {
  return (
    <div className="bg-slate-800/50 border-b border-slate-700 px-4 py-2">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-6">
          {/* Production Backend Status */}
          <div className="flex items-center space-x-2">
            {health.production ? (
              <CheckCircleIcon className="h-4 w-4 text-green-400" />
            ) : (
              <XCircleIcon className="h-4 w-4 text-red-400" />
            )}
            <span className="text-sm text-slate-300">
              Production: 
              <span className={health.production ? 'text-green-400 ml-1' : 'text-red-400 ml-1'}>
                {health.production ? 'Online' : 'Offline'}
              </span>
            </span>
          </div>

          {/* Streaming Backend Status */}
          <div className="flex items-center space-x-2">
            {health.streaming ? (
              <CheckCircleIcon className="h-4 w-4 text-green-400" />
            ) : (
              <XCircleIcon className="h-4 w-4 text-red-400" />
            )}
            <span className="text-sm text-slate-300">
              Streaming:
              <span className={health.streaming ? 'text-green-400 ml-1' : 'text-red-400 ml-1'}>
                {health.streaming ? 'Online' : 'Offline'}
              </span>
            </span>
          </div>
        </div>

        {/* Overall Status */}
        <div className="hidden sm:block">
          <span className="text-xs text-slate-400">
            System Status: 
            <span className={
              health.production && health.streaming 
                ? 'text-green-400 ml-1' 
                : health.production || health.streaming 
                  ? 'text-yellow-400 ml-1' 
                  : 'text-red-400 ml-1'
            }>
              {health.production && health.streaming 
                ? 'All Systems Operational' 
                : health.production || health.streaming 
                  ? 'Partial Service' 
                  : 'Service Unavailable'
              }
            </span>
          </span>
        </div>
      </div>
    </div>
  );
};

export default BackendStatus; 