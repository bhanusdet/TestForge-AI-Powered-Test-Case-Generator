# AI Test Case Generator Project

## Overview
This project automates the generation, management, and improvement of software test cases using advanced AI, PDF, and image processing. It features an interactive web frontend and a Python/Flask backend supporting LLMs, RAG, OCR, and more.

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
   - If using OpenAI: set `OPENAI_API_KEY` too
3. Run the Flask server:
   ```bash
   python app.py
   ```
   - API will start at `http://localhost:8000`
4. Optional features:
   - For advanced PDF: `pip install PyMuPDF`
   - For image/OCR: `pip install pytesseract Pillow`

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
- **Automated test case generation**: AI-based, supports user stories + PDF/image attachments
- **RAG system**: Retrieval-augmented generation for smarter text case synthesis (ChromaDB-powered)
- **Prompt engineering**: Modular advanced prompting
- **LLM flexibility**: Works with Groq and OpenAI APIs
- **PDF/image parsing**: Extracts text from complex docs/screenshots
- **Feedback/learning**: User feedback improves future test cases

---

## Project Authors
- Bhanu Pratap Singh

---

## License
MIT License (see LICENSE file)

---

*For any advanced PDF issues, ensure you install PyMuPDF as instructed above!*