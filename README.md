# CaseVector AI - Effortless Test Case Generation!

## Overview
This project automates the generation, management, and improvement of software Test Cases using advanced AI, PDF, image processing, and **Figma Design integration**. It features an interactive web frontend and a Python/Flask backend supporting LLMs, RAG, OCR, and design-driven Test Case generation.

---

## Project Structure
- **backend/**: Python source code (Flask API, PDF/image processing, RAG, prompt engineering)
- **frontend/**: ReactJS web app (user interface for uploading stories, attachments, feedback)
- **chroma_db/**: ChromaDB vector database files
- **uploads/**: Uploaded files (user docs, images, etc.)
- **feedback_analyzer.py**: Learning insight analytics

---

## Backend Setup & Usage
1. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
2. Set up environment variables (see backend/.env.example):
   - `GROQ_API_KEY` is **required**
   - `FIGMA_ACCESS_TOKEN` for Figma integration (optional but recommended)
   - If using OpenAI: set `OPENAI_API_KEY` too
3. Run the Flask server:
   ```bash
   python app.py
   ```
   - API will start at `http://localhost:8000`
4. Optional features:
   - For advanced PDF: `pip install PyMuPDF`
   - For image/OCR: `pip install pytesseract Pillow`
   - For **Figma integration**: Get your personal access token from [Figma Settings > Personal Access Tokens](https://www.figma.com/settings)

---

## Frontend Setup & Usage
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
   - Proxy to backend is set up in `package.json`

---

## Main Features
- **Automated Test Case generation**: AI-based, supports User Stories + PDF/image attachments
- **Figma integration**: Extract UI components and design patterns from Figma files for comprehensive testing
- **RAG system**: Retrieval-augmented generation for smarter text case synthesis (ChromaDB-powered)
- **Prompt engineering**: Modular advanced prompting with design-aware context
- **LLM flexibility**: Works with Groq and OpenAI APIs
- **PDF/image parsing**: Extracts text from complex docs/screenshots
- **Requirement analysis**: Advanced requirement extraction and coverage analysis
- **Feedback/learning**: User feedback improves future Test Cases

---

## Figma Integration Setup

### Getting Your Figma Access Token
1. Go to Figma Settings → Account → Personal Access Tokens
2. Click "Create new token"
3. Name your token (e.g., "TestCase Generator")
4. Copy the generated token
5. Add it to your `.env` file: `FIGMA_ACCESS_TOKEN=your_token_here`

### Supported Figma URL Formats
- `https://www.figma.com/file/[file-key]/[file-name]`
- `https://www.figma.com/design/[file-key]/[file-name]`
- URLs with specific node selection: `#[node-id]`

### What Gets Extracted
- **UI Components**: Buttons, inputs, dropdowns, modals, etc.
- **Design Patterns**: Card layouts, forms, navigation patterns
- **User Flows**: Multi-step interactions and component relationships
- **Test Scenarios**: Suggested Test Cases based on component interactions

---

## API Endpoints

### Core Endpoints
- `POST /api/v1/generate-test-cases` - Generate Test Cases (supports Figma URLs)
- `POST /api/v1/validate-figma` - Validate and preview Figma designs
- `POST /api/v1/figma-components` - Get detailed component analysis
- `POST /api/v1/analyze-requirements` - Analyze requirement coverage

---

## Project Authors
- Bhanu Pratap Singh

---

## License
MIT License (see LICENSE file)

---

*For any advanced PDF issues, ensure you install PyMuPDF as instructed above!*
*For Figma integration, ensure you have a valid personal access token configured!*
