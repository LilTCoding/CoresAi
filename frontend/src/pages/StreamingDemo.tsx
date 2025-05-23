import React, { useState } from 'react';
import { CubeTransparentIcon, PlayIcon, StopIcon } from '@heroicons/react/24/outline';
import { streamObject, detectSchema, StreamingRequest } from '../services/api.ts';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';

interface StreamingData {
  chunk_type: string;
  data: any;
  chunk_index: number;
  is_final: boolean;
}

const StreamingDemo: React.FC = () => {
  const [query, setQuery] = useState('');
  const [outputMode, setOutputMode] = useState<'object' | 'array' | 'no-schema'>('object');
  const [schemaType, setSchemaType] = useState<string>('general');
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingData, setStreamingData] = useState<StreamingData[]>([]);
  const [finalResult, setFinalResult] = useState<any>(null);

  const handleDetectSchema = async () => {
    if (!query.trim()) return;

    try {
      const detection = await detectSchema(query);
      setSchemaType(detection.detected_schema);
      toast.success(`Schema detected: ${detection.detected_schema}`);
    } catch (error) {
      console.error('Schema detection error:', error);
      toast.error('Schema detection failed. Please check if the streaming backend is running.');
    }
  };

  const handleStartStreaming = async () => {
    if (!query.trim() || isStreaming) return;

    setIsStreaming(true);
    setStreamingData([]);
    setFinalResult(null);

    const request: StreamingRequest = {
      messages: [{ role: 'user', content: query.trim() }],
      output_mode: outputMode,
      schema_type: schemaType,
    };

    try {
      await streamObject(
        request,
        (chunk: StreamingData) => {
          setStreamingData(prev => [...prev, chunk]);
        },
        () => {
          setIsStreaming(false);
          toast.success('Streaming completed!');
        },
        (error: any) => {
          console.error('Streaming error:', error);
          toast.error('Streaming failed. Please check if the streaming backend is running.');
          setIsStreaming(false);
        }
      );
    } catch (error) {
      console.error('Stream start error:', error);
      toast.error('Failed to start streaming.');
      setIsStreaming(false);
    }
  };

  const handleStopStreaming = () => {
    setIsStreaming(false);
    toast.info('Streaming stopped.');
  };

  const quickQueries = [
    'Search for recent AI developments',
    'Create a task list for building a web app',
    'Analyze the benefits of remote work',
    'Photoshop tools for photo editing',
    'Notify me about important updates'
  ];

  return (
    <div className="max-w-6xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-4">Structured Streaming</h1>
          <p className="text-xl text-slate-300">
            Advanced streaming responses with real-time object building and schema detection
          </p>
        </div>

        {/* Controls */}
        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 mb-8">
          <div className="space-y-6">
            {/* Query Input */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Query
              </label>
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter your query here..."
                className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent resize-none"
                rows={3}
                disabled={isStreaming}
              />
            </div>

            {/* Settings */}
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Output Mode
                </label>
                <select
                  value={outputMode}
                  onChange={(e) => setOutputMode(e.target.value as any)}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  disabled={isStreaming}
                >
                  <option value="object">Object Mode</option>
                  <option value="array">Array Mode</option>
                  <option value="no-schema">No Schema Mode</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Schema Type
                </label>
                <select
                  value={schemaType}
                  onChange={(e) => setSchemaType(e.target.value)}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  disabled={isStreaming}
                >
                  <option value="general">General</option>
                  <option value="search">Search</option>
                  <option value="notifications">Notifications</option>
                  <option value="tasks">Tasks</option>
                  <option value="analysis">Analysis</option>
                  <option value="creative_software">Creative Software</option>
                </select>
              </div>
            </div>

            {/* Quick Queries */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Quick Queries
              </label>
              <div className="flex flex-wrap gap-2">
                {quickQueries.map((quickQuery) => (
                  <button
                    key={quickQuery}
                    onClick={() => setQuery(quickQuery)}
                    className="px-3 py-1 bg-slate-700/50 text-slate-300 text-sm rounded-full hover:bg-slate-600/50 transition-colors"
                    disabled={isStreaming}
                  >
                    {quickQuery}
                  </button>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-4">
              <button
                onClick={handleDetectSchema}
                disabled={!query.trim() || isStreaming}
                className="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              >
                Auto-Detect Schema
              </button>

              {!isStreaming ? (
                <button
                  onClick={handleStartStreaming}
                  disabled={!query.trim()}
                  className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-purple-600 text-white rounded-lg hover:from-cyan-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center space-x-2"
                >
                  <PlayIcon className="h-4 w-4" />
                  <span>Start Streaming</span>
                </button>
              ) : (
                <button
                  onClick={handleStopStreaming}
                  className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 transition-all duration-200 flex items-center space-x-2"
                >
                  <StopIcon className="h-4 w-4" />
                  <span>Stop Streaming</span>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Streaming Output */}
        <AnimatePresence>
          {(streamingData.length > 0 || isStreaming) && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
              className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6"
            >
              <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                <CubeTransparentIcon className="h-5 w-5 mr-2 text-cyan-400" />
                Streaming Output
                {isStreaming && (
                  <div className="ml-2 flex space-x-1">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                )}
              </h2>

              <div className="space-y-4 max-h-96 overflow-y-auto">
                {streamingData.map((chunk, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3 }}
                    className="bg-slate-700/30 rounded-lg p-4 border-l-4 border-cyan-400"
                  >
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-slate-300">
                        Chunk #{chunk.chunk_index}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        chunk.chunk_type === 'complete' ? 'bg-green-600' :
                        chunk.chunk_type === 'partial' ? 'bg-yellow-600' :
                        'bg-red-600'
                      }`}>
                        {chunk.chunk_type}
                      </span>
                    </div>
                    <pre className="text-sm text-slate-200 overflow-x-auto whitespace-pre-wrap">
                      {JSON.stringify(chunk.data, null, 2)}
                    </pre>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Empty State */}
        {streamingData.length === 0 && !isStreaming && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <CubeTransparentIcon className="h-16 w-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-300 mb-2">
              Ready to Stream
            </h3>
            <p className="text-slate-400">
              Enter a query above and start streaming to see structured responses in real-time
            </p>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
};

export default StreamingDemo; 