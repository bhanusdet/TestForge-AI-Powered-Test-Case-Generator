# CaseVector AI - Effortless Test Case Generation!

## Overview
This project automates the generation, management, and improvement of software Test Cases using advanced AI, PDF, image processing, and **Figma Design integration**. It features an interactive web frontend and a Python/Flask backend supporting LLMs, RAG, OCR, and design-driven Test Case generation with **optimized prompt engineering** and **enhanced visual processing**.

---

## Project Structure
- **backend/**: Python source code (Flask API, PDF/image processing, RAG, optimized prompt engineering)
- **frontend/**: ReactJS web app with modern UI (TailwindCSS, React Router, enhanced UX)
- **chroma_db/**: ChromaDB vector database files for RAG system
- **uploads/**: Uploaded files (user docs, images, Figma screenshots)
- **feedback_analyzer.py**: Learning insight analytics and feedback processing

---

## Quick Setup (Recommended)
Use the included **Makefile** for streamlined setup:

```bash
# Complete setup (backend + frontend + learning system)
make setup

# Start development mode (both servers)
make dev

# Get help with all available commands
make help
```

### Manual Setup

#### Backend Setup & Usage
1. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Set up environment variables (see backend/.env.example):
   - `GROQ_API_KEY` is **required**
   - `FIGMA_ACCESS_TOKEN` for Figma integration (optional but recommended)
   - If using OpenAI: set `OPENAI_API_KEY` too

3. Initialize the learning system:
   ```bash
   python setup_learning_system.py
   ```

4. Run the Flask server:
   ```bash
   python app.py
   ```
   - API will start at `http://localhost:8000`

#### Frontend Setup & Usage
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the Dev Server:
   ```bash
   npm start
   ```
   - UI available at `http://localhost:3000`
   - Modern responsive design with TailwindCSS
   - Real-time progress indicators and enhanced UX

---

## Main Features

### 🚀 Core Capabilities
- **Automated Test Case generation**: AI-powered with optimized prompt engineering
- **Enhanced Figma integration**: Visual element detection, screenshot analysis, UI component mapping
- **Advanced RAG system**: Retrieval-augmented generation with ChromaDB for contextual learning
- **Multi-format support**: User Stories, PDF documents, images, Figma designs
- **Smart feedback system**: Continuous learning from user feedback and improvements

### 🧠 AI & Machine Learning
- **Optimized prompt engineering**: Reduced token usage while maintaining quality
- **Enhanced visual processing**: OCR, image analysis, design pattern recognition
- **Learning system**: Adaptive improvement based on user feedback and usage patterns
- **LLM flexibility**: Support for Groq, OpenAI, and other compatible APIs
- **Contextual awareness**: Design-driven test case generation with visual context

### 🎨 Enhanced User Experience
- **Modern React frontend**: Built with React 18, TailwindCSS, and Framer Motion
- **Real-time progress tracking**: Visual feedback during test case generation
- **Drag-and-drop file uploads**: Support for multiple file types
- **Interactive feedback system**: Rate and improve generated test cases
- **Responsive design**: Optimized for desktop and mobile use
- **Analytics dashboard**: Track usage patterns and system performance

---

## Advanced Features

### 🎨 Enhanced Figma Integration

#### Getting Your Figma Access Token
1. Go to Figma Settings → Account → Personal Access Tokens
2. Click "Create new token"
3. Name your token (e.g., "TestCase Generator")
4. Copy the generated token
5. Add it to your `.env` file: `FIGMA_ACCESS_TOKEN=your_token_here`

#### Supported Figma URL Formats
- `https://www.figma.com/file/[file-key]/[file-name]`
- `https://www.figma.com/design/[file-key]/[file-name]`
- URLs with specific node selection: `#[node-id]`

#### Enhanced Figma Processing Capabilities
- **Visual Element Detection**: Advanced computer vision for UI component identification
- **Screenshot Analysis**: High-quality image capture and processing
- **OCR Integration**: Extract text from design mockups and prototypes
- **Design Pattern Recognition**: Identify common UI patterns and workflows
- **Component Mapping**: Map visual elements to testable scenarios
- **Interactive Element Detection**: Buttons, forms, navigation, modals, etc.

### 🔧 Optimized Prompt Engineering
- **Reduced Token Usage**: 60-70% reduction in prompt length while maintaining quality
- **Context-Aware Generation**: Smart selection of relevant testing techniques
- **Dynamic Prompt Adaptation**: Automatically adjusts based on story complexity
- **Enhanced Coverage Analysis**: Better requirement extraction and test coverage
- **Performance Optimized**: Faster generation with lower API costs

### 🧠 Advanced Learning System
- **Feedback Integration**: Continuous improvement from user ratings and comments
- **Pattern Recognition**: Learning from successful test case patterns
- **Contextual Memory**: RAG system with enhanced retrieval capabilities
- **Analytics Integration**: Track performance metrics and usage patterns

---

## API Endpoints

### Core Test Case Generation
- `POST /api/v1/generate-test-cases` - Generate Test Cases with multi-format support
- `POST /api/v1/optimize-test-cases` - Generate optimized test cases with reduced token usage
- `POST /api/v1/analyze-requirements` - Advanced requirement extraction and coverage analysis

### Enhanced Figma Integration
- `POST /api/v1/validate-figma` - Validate and preview Figma designs
- `POST /api/v1/figma-components` - Get detailed component analysis
- `POST /api/v1/figma-screenshot` - Capture and analyze Figma screenshots
- `POST /api/v1/figma-visual-analysis` - Advanced visual element detection

### Learning & Feedback System
- `POST /api/v1/submit-feedback` - Submit user feedback for continuous improvement
- `GET /api/v1/learning-stats` - Get learning system statistics and insights
- `POST /api/v1/improve-test-cases` - Get improved test cases based on feedback

### System Health & Analytics
- `GET /api/v1/health` - System health check and component status
- `GET /api/v1/analytics` - Usage analytics and performance metrics

## Development Tools

### Available Make Commands
```bash
# Setup and Installation
make setup              # Complete full-stack setup
make install-backend    # Install backend dependencies only  
make install-frontend   # Install frontend dependencies only

# Development
make dev               # Start both backend and frontend
make backend          # Start backend server only
make frontend         # Start frontend server only

# Testing and Validation
make test             # Test RAG system and core components

# Build and Production
make build            # Production build (backend + frontend)
make build-frontend   # Build frontend only

# Maintenance
make clean            # Clean up build artifacts and caches
make help             # Show all available commands
```

### Requirements Files
- `requirements.txt` - Main production dependencies
- `requirements-py38.txt` - Python 3.8 compatibility
- `requirements-minimal.txt` - Minimal setup for basic functionality
- `requirements-advanced.txt` - Full feature set with all enhancements

---

## System Requirements

### Backend Dependencies
- **Python**: 3.8+ (with Python 3.10+ recommended)
- **Core Libraries**: Flask, ChromaDB, Sentence Transformers
- **AI/ML**: OpenAI API or Groq API access
- **Image Processing**: OpenCV, PIL, pytesseract (for OCR)
- **PDF Processing**: PyMuPDF, pdfplumber
- **Vector Database**: ChromaDB with persistence

### Frontend Dependencies
- **Node.js**: 16+ (with Node.js 18+ recommended)
- **React**: 18.2+ with modern hooks and context
- **UI Framework**: TailwindCSS with custom components
- **Build Tools**: Create React App, PostCSS, Autoprefixer

## Troubleshooting

### Common Issues
1. **ChromaDB Installation**: If ChromaDB fails to install, try using Python 3.10+
2. **OCR Dependencies**: Install tesseract on your system for image text extraction
3. **Figma Access**: Ensure your Figma token has proper permissions
4. **Memory Issues**: For large Figma files, increase system memory allocation

### Performance Optimization
- Use `requirements-minimal.txt` for basic functionality
- Enable optimized prompt engineering to reduce API costs
- Configure ChromaDB persistence for faster subsequent runs
- Use image compression for large Figma screenshots

## Contributing
We welcome contributions! Please see our contributing guidelines and feel free to submit issues, feature requests, or pull requests.

## Project Authors
- **Bhanu Pratap Singh** - Lead Developer & AI/ML Engineer

## License
MIT License (see LICENSE file)

---

## Quick Start Summary
```bash
# 1. Clone the repository
git clone <repository-url>
cd TestKumar

# 2. Complete setup using Makefile
make setup

# 3. Configure environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# 4. Start development
make dev

# 5. Open http://localhost:3000 in your browser
```

---

*🚀 **Pro Tip**: Use the Makefile commands for the smoothest development experience!*
*🎨 **Figma Integration**: Get your personal access token from Figma Settings for enhanced design-driven testing!*
*🧠 **Optimized AI**: The system now uses 60-70% fewer tokens while maintaining high-quality test case generation!*
