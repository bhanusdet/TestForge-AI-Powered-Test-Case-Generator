.PHONY: all backend frontend install-backend install-frontend setup-learning clean test dev

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
	@echo "🚀 Starting TestForge full-stack development..."
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
	cd backend && rm -rf chroma_db  # Remove learning database
	cd frontend && rm -rf node_modules build

# Legacy support
all: setup dev

# Quick start (recommended)
# make setup && make dev