#!/bin/bash

# TestForge AI - Complete Setup Script
# Author: Bhanu Pratap Singh

echo "🚀 TestForge AI - Setting up full-stack application..."
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "Makefile" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Backend setup
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "📚 Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Setup learning system
echo "🧠 Initializing AI learning system..."
python setup_learning_system.py

# Setup environment file
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment file..."
    cp .env.example .env
    echo "🔑 Please edit backend/.env and add your GROQ_API_KEY"
fi

cd ..

# Frontend setup
echo "🎨 Setting up frontend..."
cd frontend

# Install npm dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🔑 Next steps:"
echo "1. Edit backend/.env and add your GROQ_API_KEY"
echo "2. Run 'make dev' to start both servers"
echo "3. Access the app at http://localhost:3000"
echo ""
echo "📖 Commands:"
echo "  make dev      - Start both frontend and backend"
echo "  make backend  - Start only backend (port 8000)"
echo "  make frontend - Start only frontend (port 3000)"
echo "  make clean    - Clean all dependencies"
echo ""
echo "🎉 Happy testing with TestForge AI!"