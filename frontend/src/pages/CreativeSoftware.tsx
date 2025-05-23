import React, { useState } from 'react';
import { PaintBrushIcon, WrenchScrewdriverIcon, CubeIcon } from '@heroicons/react/24/outline';
import { getCreativeSoftwareKnowledge } from '../services/api.ts';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';

interface SoftwareTool {
  name: string;
  shortcut?: string;
  function: string;
  how_it_works: string;
  category: string;
}

interface SoftwareWorkspace {
  name: string;
  purpose: string;
  how_it_works: string;
  software: string;
}

interface CreativeTechnique {
  technique: string;
  description: string;
  software: string;
  steps: string[];
  technical_details: string;
}

interface CreativeKnowledgeResponse {
  query: string;
  software_focus: string;
  tools: SoftwareTool[];
  workspaces: SoftwareWorkspace[];
  techniques: CreativeTechnique[];
  common_concepts: string[];
  summary: string;
}

const CreativeSoftware: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<CreativeKnowledgeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'tools' | 'workspaces' | 'techniques' | 'concepts'>('tools');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    setIsLoading(true);
    try {
      const knowledge = await getCreativeSoftwareKnowledge(query.trim());
      setResults(knowledge);
    } catch (error) {
      console.error('Creative software knowledge error:', error);
      toast.error('Failed to get creative software knowledge. Please check if the streaming backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const quickQueries = [
    'Photoshop selection tools',
    'Blender modeling workspace',
    'VEGAS Pro video effects',
    'Layer blending techniques',
    'Keyframe animation basics',
    'Color grading workflow'
  ];

  const softwareCards = [
    {
      name: 'Adobe Photoshop',
      description: 'Professional image editing and digital art creation',
      icon: '🎨',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      name: 'Blender',
      description: '3D modeling, animation, and rendering software',
      icon: '🧊',
      color: 'from-orange-500 to-red-500'
    },
    {
      name: 'Sony VEGAS Pro',
      description: 'Professional video editing and post-production',
      icon: '🎬',
      color: 'from-purple-500 to-pink-500'
    }
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
          <h1 className="text-4xl font-bold gradient-text mb-4">Creative Software Knowledge</h1>
          <p className="text-xl text-slate-300">
            Expert knowledge and guidance for Photoshop, Blender, and VEGAS Pro
          </p>
        </div>

        {/* Software Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {softwareCards.map((software) => (
            <motion.div
              key={software.name}
              className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 hover:border-slate-600 transition-colors cursor-pointer"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setQuery(`${software.name} tools and features`)}
            >
              <div className={`inline-flex p-3 rounded-lg bg-gradient-to-r ${software.color} mb-4`}>
                <span className="text-2xl">{software.icon}</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{software.name}</h3>
              <p className="text-slate-400 text-sm">{software.description}</p>
            </motion.div>
          ))}
        </div>

        {/* Search Form */}
        <div className="mb-8">
          <form onSubmit={handleSearch} className="max-w-2xl mx-auto">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <PaintBrushIcon className="h-5 w-5 text-slate-400" />
              </div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask about creative software tools, techniques, or workflows..."
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

          {/* Quick Queries */}
          <div className="max-w-2xl mx-auto mt-4">
            <p className="text-sm text-slate-400 mb-3">Quick searches:</p>
            <div className="flex flex-wrap gap-2">
              {quickQueries.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setQuery(suggestion)}
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
              {/* Summary */}
              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
                <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                  <CubeIcon className="h-5 w-5 mr-2 text-cyan-400" />
                  {results.software_focus} Knowledge
                </h2>
                <p className="text-slate-300 leading-relaxed mb-4">{results.summary}</p>
                <div className="text-sm text-slate-400">
                  Query: "{results.query}"
                </div>
              </div>

              {/* Tabs */}
              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl overflow-hidden">
                <div className="flex border-b border-slate-700">
                  {[
                    { key: 'tools', label: 'Tools', count: results.tools.length },
                    { key: 'workspaces', label: 'Workspaces', count: results.workspaces.length },
                    { key: 'techniques', label: 'Techniques', count: results.techniques.length },
                    { key: 'concepts', label: 'Concepts', count: results.common_concepts.length },
                  ].map((tab) => (
                    <button
                      key={tab.key}
                      onClick={() => setActiveTab(tab.key as any)}
                      className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                        activeTab === tab.key
                          ? 'bg-slate-700 text-cyan-400 border-b-2 border-cyan-400'
                          : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
                      }`}
                    >
                      {tab.label} ({tab.count})
                    </button>
                  ))}
                </div>

                <div className="p-6">
                  {/* Tools Tab */}
                  {activeTab === 'tools' && (
                    <div className="space-y-4">
                      {results.tools.map((tool, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.3, delay: index * 0.1 }}
                          className="bg-slate-700/30 rounded-lg p-4"
                        >
                          <div className="flex items-start justify-between mb-2">
                            <h3 className="text-lg font-semibold text-white">{tool.name}</h3>
                            {tool.shortcut && (
                              <span className="bg-slate-600 text-slate-300 text-xs px-2 py-1 rounded">
                                {tool.shortcut}
                              </span>
                            )}
                          </div>
                          <p className="text-slate-300 mb-2">{tool.function}</p>
                          <p className="text-slate-400 text-sm mb-2">{tool.how_it_works}</p>
                          <span className="inline-block bg-slate-600 text-slate-300 text-xs px-2 py-1 rounded">
                            {tool.category}
                          </span>
                        </motion.div>
                      ))}
                    </div>
                  )}

                  {/* Workspaces Tab */}
                  {activeTab === 'workspaces' && (
                    <div className="space-y-4">
                      {results.workspaces.map((workspace, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.3, delay: index * 0.1 }}
                          className="bg-slate-700/30 rounded-lg p-4"
                        >
                          <h3 className="text-lg font-semibold text-white mb-2">{workspace.name}</h3>
                          <p className="text-slate-300 mb-2">{workspace.purpose}</p>
                          <p className="text-slate-400 text-sm">{workspace.how_it_works}</p>
                        </motion.div>
                      ))}
                    </div>
                  )}

                  {/* Techniques Tab */}
                  {activeTab === 'techniques' && (
                    <div className="space-y-4">
                      {results.techniques.map((technique, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.3, delay: index * 0.1 }}
                          className="bg-slate-700/30 rounded-lg p-4"
                        >
                          <h3 className="text-lg font-semibold text-white mb-2">{technique.technique}</h3>
                          <p className="text-slate-300 mb-3">{technique.description}</p>
                          
                          <div className="mb-3">
                            <h4 className="text-sm font-medium text-slate-200 mb-2">Steps:</h4>
                            <ol className="list-decimal list-inside space-y-1 text-sm text-slate-400">
                              {technique.steps.map((step, stepIndex) => (
                                <li key={stepIndex}>{step}</li>
                              ))}
                            </ol>
                          </div>
                          
                          <p className="text-slate-400 text-sm">{technique.technical_details}</p>
                        </motion.div>
                      ))}
                    </div>
                  )}

                  {/* Concepts Tab */}
                  {activeTab === 'concepts' && (
                    <div className="space-y-3">
                      {results.common_concepts.map((concept, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.3, delay: index * 0.1 }}
                          className="bg-slate-700/30 rounded-lg p-4"
                        >
                          <p className="text-slate-300">{concept}</p>
                        </motion.div>
                      ))}
                    </div>
                  )}
                </div>
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
            <WrenchScrewdriverIcon className="h-16 w-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-300 mb-2">
              Ready to Learn
            </h3>
            <p className="text-slate-400">
              Ask about creative software tools, techniques, or workflows to get expert knowledge
            </p>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
};

export default CreativeSoftware; 