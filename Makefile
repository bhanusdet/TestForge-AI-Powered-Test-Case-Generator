.PHONY: all backend frontend install-backend install-frontend setup-learning clean test dev build build-frontend help

# Backend commands
install-backend:
	cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

setup-learning:
	cd backend && source venv/bin/activate && python setup_learning_system.py

backend:
	cd backend && source venv/bin/activate && python app.py

# Frontend commands
install-frontend:
	cd frontend && npm install

frontend:
	cd frontend && npm start

build-frontend:
	cd frontend && npm run build

# Full-stack setup
setup: install-backend setup-learning install-frontend
	@echo "✅ Complete full-stack setup finished!"
	@echo "💡 Run 'make dev' to start both backend and frontend"

# Development mode (runs both backend and frontend)
dev:
	@echo "🚀 Starting CaseVector AI development..."
	@echo "Backend will run on http://localhost:8000"
	@echo "Frontend will run on http://localhost:3000"
	@trap 'kill %1; kill %2' SIGINT; \
	(cd backend && source venv/bin/activate && python app.py) & \
	(cd frontend && npm start) & \
	wait

# Test the system
test:
	cd backend && source venv/bin/activate && python -c "from enhanced_rag_helper import rag_helper; print('✅ Enhanced RAG system working!')"

# Production build
build: setup-learning build-frontend
	@echo "✅ Production build complete!"

# Clean up
clean:
	cd backend && rm -rf venv __pycache__ *.pyc
	cd backend && rm -rf chroma_db
	cd frontend && rm -rf node_modules build

# Help command
help:
	@echo "🚀 CaseVector AI - Available Commands"
	@echo "=============================================="
	@echo ""
	@echo "📦 Setup Commands:"
	@echo "  make setup           - Complete full-stack setup"
	@echo "  make install-backend - Install backend dependencies"
	@echo "  make install-frontend- Install frontend dependencies"
	@echo ""
	@echo "🚀 Development Commands:"
	@echo "  make dev             - Start both backend and frontend"
	@echo "  make backend         - Start backend only"
	@echo "  make frontend        - Start frontend only"
	@echo ""
	@echo "🧪 Testing Commands:"
	@echo "  make test            - Test RAG system"
	@echo ""
	@echo "🏗️ Build Commands:"
	@echo "  make build           - Production build"
	@echo "  make build-frontend  - Build frontend only"
	@echo ""
	@echo "🧹 Maintenance Commands:"
	@echo "  make clean           - Clean up build artifacts"

# Legacy support
all: setup dev

# Default target
.DEFAULT_GOAL := help