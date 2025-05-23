import React, { useState } from 'react';
import { MagnifyingGlassIcon, GlobeAltIcon, LinkIcon } from '@heroicons/react/24/outline';
import { performWebSearch, WebSearchResponse } from '../services/api.ts';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';

const WebSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<WebSearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    setIsLoading(true);
    try {
      const searchResults = await performWebSearch(query.trim());
      setResults(searchResults);
    } catch (error) {
      console.error('Search error:', error);
      toast.error('Search failed. Please check if the production backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickSearch = (searchQuery: string) => {
    setQuery(searchQuery);
  };

  const quickSearches = [
    'Latest AI developments 2024',
    'Machine learning trends',
    'React best practices',
    'Python programming tips',
    'Creative software tutorials',
    'Web development news'
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
          <h1 className="text-4xl font-bold gradient-text mb-4">Web Search</h1>
          <p className="text-xl text-slate-300">
            AI-powered web search with intelligent summaries and insights
          </p>
        </div>

        {/* Search Form */}
        <div className="mb-8">
          <form onSubmit={handleSearch} className="max-w-2xl mx-auto">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-slate-400" />
              </div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search for anything on the web..."
                className="w-full pl-10 pr-4 py-4 bg-slate-800/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!query.trim() || isLoading}
                className="absolute inset-y-0 right-0 px-6 bg-gradient-to-r from-cyan-500 to-purple-600 text-white rounded-r-lg hover:from-cyan-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              >
                {isLoading ? (
                  <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
                ) : (
                  'Search'
                )}
              </button>
            </div>
          </form>

          {/* Quick Search Suggestions */}
          <div className="max-w-2xl mx-auto mt-4">
            <p className="text-sm text-slate-400 mb-3">Quick searches:</p>
            <div className="flex flex-wrap gap-2">
              {quickSearches.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => handleQuickSearch(suggestion)}
                  className="px-3 py-1 bg-slate-700/50 text-slate-300 text-sm rounded-full hover:bg-slate-600/50 transition-colors"
                  disabled={isLoading}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Results */}
        <AnimatePresence>
          {results && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
              className="space-y-6"
            >
              {/* AI Summary */}
              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
                <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                  <GlobeAltIcon className="h-5 w-5 mr-2 text-cyan-400" />
                  AI Summary
                </h2>
                <p className="text-slate-300 leading-relaxed">{results.summary}</p>
              </div>

              {/* Search Results */}
              <div className="space-y-4">
                <h2 className="text-xl font-bold text-white">Search Results</h2>
                {results.results.map((result, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 hover:border-slate-600 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <h3 className="text-lg font-semibold text-white leading-tight">
                        {result.title}
                      </h3>
                      <div className="flex items-center text-xs text-slate-400 ml-4">
                        <span className="bg-slate-700 px-2 py-1 rounded">
                          {Math.round(result.relevance_score * 100)}% relevant
                        </span>
                      </div>
                    </div>
                    
                    <p className="text-slate-300 mb-4 leading-relaxed">
                      {result.snippet}
                    </p>
                    
                    <a
                      href={result.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center text-cyan-400 hover:text-cyan-300 transition-colors"
                    >
                      <LinkIcon className="h-4 w-4 mr-1" />
                      <span className="text-sm truncate max-w-md">{result.url}</span>
                    </a>
                  </motion.div>
                ))}
              </div>

              {/* Results Stats */}
              <div className="text-center text-slate-400 text-sm">
                Found {results.results.length} results for "{results.query}"
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Empty State */}
        {!results && !isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <GlobeAltIcon className="h-16 w-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-300 mb-2">
              Ready to Search
            </h3>
            <p className="text-slate-400">
              Enter a search query above to get AI-powered results and summaries
            </p>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
};

export default WebSearch; 