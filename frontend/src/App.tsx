import React, { useEffect, useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar.tsx';
import Dashboard from './pages/Dashboard.tsx';
import Chat from './pages/Chat.tsx';
import StreamingDemo from './pages/StreamingDemo.tsx';
import CreativeSoftware from './pages/CreativeSoftware.tsx';
import WebSearch from './pages/WebSearch.tsx';
import CryptoTrading from './pages/CryptoTrading.tsx';
import BackendStatus from './components/BackendStatus.tsx';
import { checkBackendHealth } from './services/api.ts';

interface BackendHealth {
  production: boolean;
  streaming: boolean;
}

function App() {
  const [backendHealth, setBackendHealth] = useState<BackendHealth>({
    production: false,
    streaming: false
  });

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const productionHealth = await checkBackendHealth('production');
        const streamingHealth = await checkBackendHealth('streaming');
        
        setBackendHealth({
          production: productionHealth,
          streaming: streamingHealth
        });
      } catch (error) {
        console.error('Error checking backend health:', error);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <Navbar />
      <BackendStatus health={backendHealth} />
      
      <main className="container mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/streaming" element={<StreamingDemo />} />
          <Route path="/creative" element={<CreativeSoftware />} />
          <Route path="/search" element={<WebSearch />} />
          <Route path="/crypto" element={<CryptoTrading />} />
        </Routes>
      </main>

      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#1e293b',
            color: '#f1f5f9',
            border: '1px solid #475569'
          }
        }}
      />
    </div>
  );
}

export default App; 