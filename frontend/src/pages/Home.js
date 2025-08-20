import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Zap, 
  Brain, 
  FileText, 
  TrendingUp, 
  Shield, 
  Target,
  ArrowRight,
  Figma
} from 'lucide-react';

const Home = () => {
  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Intelligence',
      description: 'Advanced RAG system with 78% better semantic understanding using state-of-the-art embeddings.'
    },
    {
      icon: Figma,
      title: 'Figma Design Integration',
          description: 'Generate UI-focused Test Cases directly from your Figma Designs. Extract components, interactions, and user flows automatically.'
    },
    {
      icon: TrendingUp,
      title: 'Continuous Learning',
      description: 'System gets smarter with every interaction. Persistent memory across server restarts.'
    },
    {
      icon: FileText,
      title: 'Multi-Modal Support',
      description: 'Process text, images (OCR), and PDF documents with intelligent context merging.'
    },
    {
      icon: Target,
      title: 'Domain Intelligence',
      description: 'Specialized knowledge for e-commerce, authentication, finance, and more domains.'
    },
    {
      icon: Shield,
      title: 'Comprehensive Coverage',
      description: 'Positive, negative, edge, boundary, security, and performance test scenarios.'
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-gray-900 via-gray-800 to-black py-20 overflow-hidden">
        {/* Stunning Modern Background */}
        <div className="absolute inset-0">
          {/* Animated Gradient Mesh */}
          <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-gray-900/20"></div>
          
          {/* Dynamic Grid Pattern */}
          <div className="absolute inset-0 opacity-30" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cdefs%3E%3Cpattern id='grid' width='20' height='20' patternUnits='userSpaceOnUse'%3E%3Cpath d='M 20 0 L 0 0 0 20' fill='none' stroke='%23ffffff' stroke-width='0.5' opacity='0.3'/%3E%3C/pattern%3E%3C/defs%3E%3Crect width='100' height='100' fill='url(%23grid)'/%3E%3C/svg%3E")`,
          }}></div>
          
          {/* Floating Orbs with Glow */}
          <div className="absolute top-20 left-20 w-64 h-64 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-full blur-3xl animate-pulse" style={{animationDuration: '4s'}}></div>
          <div className="absolute bottom-20 right-20 w-80 h-80 bg-gradient-to-r from-purple-500/15 to-pink-500/15 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s', animationDuration: '6s'}}></div>
          <div className="absolute top-1/2 left-1/3 w-48 h-48 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-full blur-2xl animate-pulse" style={{animationDelay: '1s', animationDuration: '5s'}}></div>
          
          {/* Geometric Shapes */}
          <div className="absolute top-32 right-32 w-24 h-24 border-2 border-white/20 rotate-45 animate-spin" style={{animationDuration: '20s'}}></div>
          <div className="absolute bottom-40 left-40 w-16 h-16 bg-white/10 rotate-12 animate-bounce" style={{animationDuration: '3s'}}></div>
          <div className="absolute top-1/4 right-1/4 w-32 h-32 border border-white/15 rounded-full animate-pulse" style={{animationDuration: '4s'}}></div>
          
          {/* Animated Lines */}
          <div className="absolute top-0 left-1/4 w-px h-full bg-gradient-to-b from-transparent via-white/20 to-transparent animate-pulse"></div>
          <div className="absolute top-0 right-1/3 w-px h-full bg-gradient-to-b from-transparent via-blue-400/20 to-transparent animate-pulse" style={{animationDelay: '1s'}}></div>
        </div>

        {/* Elegant Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent"></div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <div className="flex justify-center mb-6">
              <div className="relative p-4 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20">
                {/* Glowing effect */}
                <div className="absolute inset-0 bg-blue-500/20 rounded-2xl blur-xl animate-pulse"></div>
                <Zap className="relative w-12 h-12 text-white" />
              </div>
            </div>
                <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
                  CaseVector <span className="text-blue-300">AI</span>
                </h1>
            <p className="text-xl md:text-2xl text-gray-200 mb-8 max-w-3xl mx-auto">
              Effortless AI-powered system that generates comprehensive manual Test Cases 
              from <span className="font-medium text-blue-300">User Stories</span>, <span className="font-medium text-purple-300">Figma Designs</span>, and <span className="font-medium text-cyan-300">Learns from Every Interaction</span>
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/generate"
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg shadow-blue-500/25"
              >
                <span>Start Generating</span>
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                to="/docs"
                className="border border-white/30 text-white px-8 py-4 rounded-lg font-medium hover:border-white/50 hover:bg-white/10 backdrop-blur-sm transition-all duration-200"
              >
                View Documentation
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative py-20 bg-gradient-to-b from-gray-50 to-white overflow-hidden">
        {/* Modern Background Elements */}
        <div className="absolute inset-0">
          {/* Subtle Dot Pattern */}
          <div className="absolute inset-0 opacity-40" style={{
            backgroundImage: `radial-gradient(circle at 2px 2px, rgba(0,0,0,0.15) 1px, transparent 0)`,
            backgroundSize: '32px 32px',
          }}></div>
          
          {/* Flowing Gradient Shapes */}
          <div className="absolute top-20 left-10 w-72 h-72 bg-gradient-to-r from-blue-100/50 to-purple-100/50 rounded-full blur-3xl opacity-60 animate-pulse" style={{animationDuration: '8s'}}></div>
          <div className="absolute bottom-10 right-10 w-96 h-96 bg-gradient-to-r from-purple-100/40 to-pink-100/40 rounded-full blur-3xl opacity-50 animate-pulse" style={{animationDelay: '2s', animationDuration: '10s'}}></div>
          
          {/* Geometric Accents */}
          <div className="absolute top-32 right-20 w-24 h-24 border border-gray-300/50 rotate-45 animate-spin" style={{animationDuration: '30s'}}></div>
          <div className="absolute bottom-32 left-32 w-16 h-16 bg-gray-200/60 rounded-lg animate-pulse" style={{animationDelay: '1s'}}></div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Powered by Advanced AI
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                Experience the next generation of Test Case generation with our learning-enabled AI system
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="bg-white p-8 rounded-lg border border-gray-100 hover:border-gray-200 transition-all duration-300"
                >
                  <div className="bg-gray-50 w-12 h-12 rounded-lg flex items-center justify-center mb-6">
                    <Icon className="w-6 h-6 text-gray-700" />
                  </div>
                  <h3 className="text-xl font-medium text-gray-900 mb-3">{feature.title}</h3>
                  <p className="text-gray-500 leading-relaxed">{feature.description}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 py-20 overflow-hidden">
        {/* Epic Background Elements */}
        <div className="absolute inset-0">
          {/* Animated Mesh Gradient */}
          <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 via-purple-600/20 to-cyan-600/20 animate-pulse" style={{animationDuration: '6s'}}></div>
          
          {/* Dynamic Grid */}
          <div className="absolute inset-0 opacity-30" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='80' height='80' viewBox='0 0 80 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cdefs%3E%3Cpattern id='grid' width='40' height='40' patternUnits='userSpaceOnUse'%3E%3Cpath d='M 40 0 L 0 0 0 40' fill='none' stroke='%23ffffff' stroke-width='1' opacity='0.3'/%3E%3C/pattern%3E%3C/defs%3E%3Crect width='80' height='80' fill='url(%23grid)'/%3E%3C/svg%3E")`,
          }}></div>
          
          {/* Spectacular Orbs */}
          <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-gradient-to-r from-blue-500/30 to-purple-500/30 rounded-full blur-3xl animate-pulse" style={{animationDuration: '8s'}}></div>
          <div className="absolute bottom-0 right-0 w-[600px] h-[600px] bg-gradient-to-r from-purple-500/25 to-pink-500/25 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s', animationDuration: '10s'}}></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '4s', animationDuration: '12s'}}></div>
          
          {/* Floating Elements */}
          <div className="absolute top-20 right-20 w-32 h-32 border-2 border-white/20 rotate-45 animate-spin" style={{animationDuration: '25s'}}></div>
          <div className="absolute bottom-20 left-20 w-24 h-24 bg-white/10 rounded-full animate-pulse" style={{animationDelay: '1s'}}></div>
        </div>

        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-3xl md:text-4xl font-medium text-white mb-6">
              Ready to Transform Your Testing?
            </h2>
            <p className="text-xl text-gray-200 mb-10 max-w-2xl mx-auto">
                Start generating intelligent Test Cases that improve with every interaction
            </p>
            <Link
              to="/generate"
              className="bg-white text-gray-900 px-10 py-4 rounded-lg font-medium hover:bg-gray-100 transition-all duration-200 inline-flex items-center space-x-2 shadow-2xl"
            >
              <span>Get Started Now</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Home;