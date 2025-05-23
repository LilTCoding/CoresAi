import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ChatBubbleLeftRightIcon,
  MagnifyingGlassIcon,
  PaintBrushIcon,
  CubeTransparentIcon,
  ServerIcon,
  CpuChipIcon,
  EyeIcon,
  WrenchScrewdriverIcon
} from '@heroicons/react/24/outline';
import { getHealthDetails, HealthResponse } from '../services/api.ts';
import { motion } from 'framer-motion';

const features = [
  {
    title: 'AI Chat',
    description: 'Intelligent conversation with context awareness and advanced reasoning',
    icon: ChatBubbleLeftRightIcon,
    href: '/chat',
    color: 'from-blue-500 to-cyan-500'
  },
  {
    title: 'Web Search',
    description: 'Real-time web search with AI-powered summaries and insights',
    icon: MagnifyingGlassIcon,
    href: '/search',
    color: 'from-green-500 to-emerald-500'
  },
  {
    title: 'Creative Software',
    description: 'Expert knowledge for Photoshop, Blender, and VEGAS Pro',
    icon: PaintBrushIcon,
    href: '/creative',
    color: 'from-purple-500 to-pink-500'
  },
  {
    title: 'Structured Streaming',
    description: 'Advanced streaming responses with multiple output modes',
    icon: CubeTransparentIcon,
    href: '/streaming',
    color: 'from-orange-500 to-red-500'
  }
];

const systemFeatures = [
  {
    title: 'Face Detection',
    description: 'Real-time face tracking with OpenCV',
    icon: EyeIcon
  },
  {
    title: 'Multi-Backend',
    description: 'Production and streaming backends',
    icon: ServerIcon
  },
  {
    title: 'AI Processing',
    description: 'Advanced language model capabilities',
    icon: CpuChipIcon
  },
  {
    title: 'Game Server Management',
    description: 'Integrated server management tools',
    icon: WrenchScrewdriverIcon
  }
];

const Dashboard: React.FC = () => {
  const [productionHealth, setProductionHealth] = useState<HealthResponse | null>(null);
  const [streamingHealth, setStreamingHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    const fetchHealthData = async () => {
      try {
        const [prodHealth, streamHealth] = await Promise.all([
          getHealthDetails('production'),
          getHealthDetails('streaming')
        ]);
        setProductionHealth(prodHealth);
        setStreamingHealth(streamHealth);
      } catch (error) {
        console.error('Error fetching health data:', error);
      }
    };

    fetchHealthData();
  }, []);

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <motion.div 
        className="text-center py-12"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <h1 className="text-5xl font-bold gradient-text mb-6">
          Welcome to CoresAI
        </h1>
        <p className="text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed">
          Advanced AI System with Web Search, Structured Streaming, Face Detection, 
          Creative Software Knowledge, and Multi-Backend Architecture
        </p>
        <div className="mt-8 flex justify-center">
          <div className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-lg text-white font-medium">
            <span className="mr-2">🚀</span>
            Version 4.1.0 - Production Ready
          </div>
        </div>
      </motion.div>

      {/* Features Grid */}
      <motion.div 
        className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
      >
        {features.map((feature, index) => (
          <Link
            key={feature.title}
            to={feature.href}
            className="group block"
          >
            <motion.div 
              className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 hover:border-slate-600 transition-all duration-300 hover:scale-105"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <div className={`inline-flex p-3 rounded-lg bg-gradient-to-r ${feature.color} mb-4`}>
                <feature.icon className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-cyan-400 transition-colors">
                {feature.title}
              </h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          </Link>
        ))}
      </motion.div>

      {/* System Status */}
      <motion.div 
        className="grid md:grid-cols-2 gap-8 mb-12"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.4 }}
      >
        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <ServerIcon className="h-5 w-5 mr-2 text-cyan-400" />
            Production Backend
          </h3>
          {productionHealth ? (
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Status:</span>
                <span className="text-green-400">{productionHealth.status}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Version:</span>
                <span className="text-slate-300">{productionHealth.version || 'N/A'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Port:</span>
                <span className="text-slate-300">8080</span>
              </div>
              {productionHealth.features && (
                <div className="mt-4">
                  <span className="text-slate-400 text-sm">Features:</span>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {productionHealth.features.map((feature) => (
                      <span key={feature} className="px-2 py-1 bg-slate-700 text-slate-300 text-xs rounded">
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-red-400">Backend Offline</div>
          )}
        </div>

        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <CubeTransparentIcon className="h-5 w-5 mr-2 text-purple-400" />
            Streaming Backend
          </h3>
          {streamingHealth ? (
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Status:</span>
                <span className="text-green-400">{streamingHealth.status}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Version:</span>
                <span className="text-slate-300">{streamingHealth.version || 'N/A'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Port:</span>
                <span className="text-slate-300">8081</span>
              </div>
              {streamingHealth.features && (
                <div className="mt-4">
                  <span className="text-slate-400 text-sm">Features:</span>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {streamingHealth.features.map((feature) => (
                      <span key={feature} className="px-2 py-1 bg-slate-700 text-slate-300 text-xs rounded">
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-red-400">Backend Offline</div>
          )}
        </div>
      </motion.div>

      {/* System Features */}
      <motion.div 
        className="bg-slate-800/30 backdrop-blur-sm border border-slate-700 rounded-xl p-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.6 }}
      >
        <h2 className="text-2xl font-bold text-white mb-6 text-center">System Features</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {systemFeatures.map((feature, index) => (
            <motion.div 
              key={feature.title}
              className="text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.8 + index * 0.1 }}
            >
              <div className="inline-flex p-4 rounded-full bg-slate-700/50 mb-4">
                <feature.icon className="h-8 w-8 text-cyan-400" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-slate-400 text-sm">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard; 