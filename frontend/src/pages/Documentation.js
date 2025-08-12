import React from 'react';
import { motion } from 'framer-motion';
import { 
  BookOpen, 
  Code, 
  Zap, 
  Settings, 
  Brain,
  FileText,
  Star,
  ArrowRight,
  Copy
} from 'lucide-react';
import { toast } from 'react-toastify';

const Documentation = () => {
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const sections = [
    {
      icon: Zap,
      title: 'Quick Start',
      content: (
        <div className="space-y-4">
          <p className="text-gray-600">Get started with TestForge in minutes:</p>
          <div className="bg-gray-900 rounded-lg p-4 text-green-400 font-mono text-sm">
            <div className="flex items-center justify-between mb-2">
              <span># Clone and setup</span>
              <button 
                onClick={() => copyToClipboard('make setup && make backend')}
                className="text-gray-400 hover:text-white"
              >
                <Copy className="w-4 h-4" />
              </button>
            </div>
            <div>make setup && make backend</div>
          </div>
        </div>
      )
    },
    {
      icon: Code,
      title: 'API Usage',
      content: (
        <div className="space-y-4">
          <p className="text-gray-600">Generate test cases using our REST API:</p>
          <div className="bg-gray-900 rounded-lg p-4 text-green-400 font-mono text-sm">
            <div className="flex items-center justify-between mb-2">
              <span># Generate test cases</span>
              <button 
                onClick={() => copyToClipboard(`curl -X POST http://localhost:8000/api/v1/generate-test-cases \\
  -H "Content-Type: application/json" \\
  -d '{"story": "As a user, I want to login..."}'`)}
                className="text-gray-400 hover:text-white"
              >
                <Copy className="w-4 h-4" />
              </button>
            </div>
            <div>curl -X POST http://localhost:8000/api/v1/generate-test-cases \</div>
            <div>  -H "Content-Type: application/json" \</div>
            <div>  -d '{`{"story": "As a user, I want to login..."}`}'</div>
          </div>
        </div>
      )
    },
    {
      icon: Brain,
      title: 'Learning System',
      content: (
        <div className="space-y-4">
          <p className="text-gray-600">The AI learns from your feedback to improve future generations:</p>
          <div className="bg-blue-50 rounded-lg p-4">
            <h4 className="font-semibold text-blue-900 mb-2">How it works:</h4>
            <ul className="text-blue-800 text-sm space-y-1">
              <li>• Analyzes user story domain and complexity</li>
              <li>• Retrieves similar examples using advanced embeddings</li>
              <li>• Generates context-aware test cases</li>
              <li>• Learns from user ratings and feedback</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      icon: Settings,
      title: 'Configuration',
      content: (
        <div className="space-y-4">
          <p className="text-gray-600">Configure your environment variables:</p>
          <div className="bg-gray-900 rounded-lg p-4 text-green-400 font-mono text-sm">
            <div>GROQ_API_KEY=your_groq_api_key_here</div>
            <div>RAG_TOP_K=5</div>
            <div>EMBEDDING_MODEL=all-mpnet-base-v2</div>
            <div>LEARNING_ENABLED=true</div>
          </div>
        </div>
      )
    }
  ];

  const endpoints = [
    {
      method: 'POST',
      path: '/api/v1/generate-test-cases',
      description: 'Generate test cases from user story',
      color: 'green'
    },
    {
      method: 'POST',
      path: '/api/v1/feedback',
      description: 'Submit feedback to improve AI',
      color: 'blue'
    },
    {
      method: 'GET',
      path: '/api/v1/learning-stats',
      description: 'Get learning system statistics',
      color: 'purple'
    },
    {
      method: 'POST',
      path: '/api/v1/similar-stories',
      description: 'Find similar user stories',
      color: 'orange'
    }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <div className="flex justify-center mb-4">
          <div className="p-3 bg-gradient-to-r from-purple-500 to-blue-600 rounded-xl">
            <BookOpen className="w-8 h-8 text-white" />
          </div>
        </div>
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
          Documentation
        </h1>
        <p className="text-lg text-gray-600">
          Everything you need to know about TestForge AI
        </p>
      </motion.div>

      {/* Main Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
        {sections.map((section, index) => {
          const Icon = section.icon;
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl border border-gray-200 p-6"
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className="bg-blue-50 w-10 h-10 rounded-lg flex items-center justify-center">
                  <Icon className="w-5 h-5 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900">{section.title}</h3>
              </div>
              {section.content}
            </motion.div>
          );
        })}
      </div>

      {/* API Endpoints */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white rounded-xl border border-gray-200 p-6 mb-8"
      >
        <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center">
          <Code className="w-6 h-6 mr-2 text-blue-600" />
          API Endpoints
        </h2>
        
        <div className="space-y-4">
          {endpoints.map((endpoint, index) => {
            const methodColors = {
              GET: 'bg-green-100 text-green-800',
              POST: 'bg-blue-100 text-blue-800',
              PUT: 'bg-yellow-100 text-yellow-800',
              DELETE: 'bg-red-100 text-red-800'
            };

            return (
              <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-4">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${methodColors[endpoint.method]}`}>
                    {endpoint.method}
                  </span>
                  <code className="text-sm font-mono text-gray-800">{endpoint.path}</code>
                </div>
                <span className="text-sm text-gray-600">{endpoint.description}</span>
              </div>
            );
          })}
        </div>
      </motion.div>

      {/* Features Overview */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6"
      >
        <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center">
          <Star className="w-6 h-6 mr-2 text-purple-600" />
          Key Features
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <FileText className="w-8 h-8 text-blue-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">Multi-Modal Input</h3>
            <p className="text-sm text-gray-600">Process text, images, and PDF documents</p>
          </div>
          
          <div>
            <Brain className="w-8 h-8 text-purple-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">AI Learning</h3>
            <p className="text-sm text-gray-600">Continuous improvement through feedback</p>
          </div>
          
          <div>
            <Zap className="w-8 h-8 text-green-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-2">High Performance</h3>
            <p className="text-sm text-gray-600">78% better semantic understanding</p>
          </div>
        </div>
        
        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-gray-900">Ready to get started?</h3>
              <p className="text-sm text-gray-600">Try generating your first test cases</p>
            </div>
            <a
              href="/generate"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center space-x-2"
            >
              <span>Start Now</span>
              <ArrowRight className="w-4 h-4" />
            </a>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Documentation;