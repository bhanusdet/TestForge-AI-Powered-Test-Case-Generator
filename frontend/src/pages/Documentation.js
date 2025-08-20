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
  Copy,
  Figma
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
            <p className="text-gray-600">Get started with CaseVector AI in minutes:</p>
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
            <p className="text-gray-600">Generate Test Cases using our REST API:</p>
          <div className="bg-gray-900 rounded-lg p-4 text-green-400 font-mono text-sm">
            <div className="flex items-center justify-between mb-2">
                <span># Generate Test Cases</span>
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
      icon: Figma,
      title: 'Figma Integration',
      content: (
        <div className="space-y-4">
            <p className="text-gray-600">Generate design-focused Test Cases from your Figma prototypes:</p>
          <div className="bg-purple-50 rounded-lg p-4">
            <h4 className="font-semibold text-purple-900 mb-2">Features:</h4>
            <ul className="text-purple-800 text-sm space-y-1">
              <li>• Extracts UI components (buttons, inputs, dropdowns)</li>
              <li>• Identifies user interaction flows</li>
              <li>• Generates component-specific test scenarios</li>
              <li>• Supports file, design, and prototype URLs</li>
            </ul>
          </div>
          <div className="bg-gray-900 rounded-lg p-4 text-green-400 font-mono text-sm">
            <div className="flex items-center justify-between mb-2">
              <span># With Figma URL</span>
              <button 
                onClick={() => copyToClipboard(`{
  "story": "As a user, I want to login...",
  "figma_url": "https://www.figma.com/design/ABC123/Login-Page"
}`)}
                className="text-gray-400 hover:text-white"
              >
                <Copy className="w-4 h-4" />
              </button>
            </div>
            <div>{`{`}</div>
            <div>  "story": "As a user, I want to login...",</div>
            <div>  "figma_url": "https://www.figma.com/design/ABC123/Login-Page"</div>
            <div>{`}`}</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-sm text-gray-600 mb-2">
              <strong>Setup:</strong> Add your Figma Personal Access Token to <code className="bg-gray-200 px-1 rounded">backend/.env</code>
            </p>
            <code className="text-xs text-gray-700">FIGMA_ACCESS_TOKEN=your_figma_token_here</code>
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
                <li>• Generates context-aware Test Cases</li>
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
            <div>FIGMA_ACCESS_TOKEN=your_figma_token_here</div>
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
          description: 'Generate Test Cases from User Story',
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
          description: 'Find similar User Stories',
      color: 'orange'
    }
  ];

  return (
    <div className="relative min-h-screen">
      {/* Advanced Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-50 via-white to-gray-100 opacity-80">
        {/* Documentation-themed Pattern */}
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23000000' fill-opacity='0.02'%3E%3Cpath d='M20 20h60v3H20zM20 30h40v3H20zM20 40h50v3H20zM20 50h35v3H20zM20 60h45v3H20zM20 70h30v3H20z'/%3E%3C/g%3E%3C/svg%3E")`,
        }}></div>
        
        {/* Floating Doc Elements */}
        <div className="absolute top-24 right-16 w-36 h-36 bg-gradient-to-br from-gray-200/15 to-gray-300/15 rounded-2xl animate-pulse" style={{animationDuration: '7s'}}></div>
        <div className="absolute bottom-32 left-16 w-24 h-32 bg-gradient-to-tr from-gray-200/20 to-gray-300/20 rounded-lg animate-bounce" style={{animationDuration: '5s'}}></div>
        <div className="absolute top-1/2 right-1/3 w-20 h-20 border border-gray-300/30 rounded-full animate-pulse" style={{animationDelay: '1s'}}></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex justify-center mb-4">
            <div className="relative p-3 bg-gray-900 rounded-xl">
              <div className="absolute inset-0 bg-gray-800 rounded-xl blur-lg opacity-40 animate-pulse"></div>
              <BookOpen className="relative w-8 h-8 text-white" />
            </div>
          </div>
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
          Documentation
        </h1>
            <p className="text-lg text-gray-600">
              Everything you need to know about CaseVector AI
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
                <p className="text-sm text-gray-600">Try generating your first Test Cases</p>
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
    </div>
  );
};

export default Documentation;