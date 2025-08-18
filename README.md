<div align="center">

# 🤖 AI Test Case Generator Project

[![Visitors](https://api.visitorbadge.io/api/visitors?path=yourusername%2FAI_TestCase_Generator_Project&label=Profile%20Views&countColor=%23263759&style=flat)](https://visitorbadge.io/status?path=yourusername%2FAI_TestCase_Generator_Project)
[![GitHub Profile Views](https://komarev.com/ghpvc/?username=yourusername&color=blue&style=flat)](https://github.com/yourusername)
[![GitHub Stars](https://img.shields.io/github/stars/yourusername/AI_TestCase_Generator_Project?style=social)](https://github.com/yourusername/AI_TestCase_Generator_Project/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/yourusername/AI_TestCase_Generator_Project?style=social)](https://github.com/yourusername/AI_TestCase_Generator_Project/network/members)

</div>

## 🎯 Overview
This project automates the generation, management, and improvement of software test cases using advanced AI, PDF, image processing, and **Figma design integration**. It features an interactive web frontend and a Python/Flask backend supporting LLMs, RAG, OCR, and design-driven test case generation.

## 📊 Repository Stats

<div align="center">

![GitHub repo size](https://img.shields.io/github/repo-size/yourusername/AI_TestCase_Generator_Project)
![GitHub language count](https://img.shields.io/github/languages/count/yourusername/AI_TestCase_Generator_Project)
![GitHub top language](https://img.shields.io/github/languages/top/yourusername/AI_TestCase_Generator_Project)
![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/AI_TestCase_Generator_Project)
![GitHub issues](https://img.shields.io/github/issues/yourusername/AI_TestCase_Generator_Project)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/AI_TestCase_Generator_Project)

</div>

---

## 📁 Project Structure
```
AI_TestCase_Generator_Project/
├── 🐍 backend/              # Python Flask API & AI processing
│   ├── app.py              # Main Flask application
│   ├── figma_integration.py # Figma API integration
│   ├── enhanced_pdf_helper.py # PDF processing
│   ├── image_helper.py     # Image & OCR processing
│   ├── prompt_engineering.py # AI prompt optimization
│   └── requirements.txt    # Python dependencies
├── ⚛️  frontend/            # React.js web interface
│   ├── src/components/     # React components
│   ├── src/pages/         # Application pages
│   └── package.json       # Node.js dependencies
├── 🗄️  chroma_db/          # Vector database files
├── 📁 uploads/            # User uploaded files
├── 📊 feedback_analyzer.py # Learning analytics
└── 📖 README.md           # Project documentation
```

### 🔧 Core Components
- **backend/**: Python source code (Flask API, PDF/image processing, RAG, prompt engineering)
- **frontend/**: ReactJS web app (user interface for uploading stories, attachments, feedback)
- **chroma_db/**: ChromaDB vector database files
- **uploads/**: Uploaded files (user docs, images, etc.)
- **feedback_analyzer.py**: Learning insight analytics

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- Git

### 🐍 Backend Setup & Usage
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/AI_TestCase_Generator_Project.git
   cd AI_TestCase_Generator_Project
   ```

2. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **🔐 Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```
   **Required Variables:**
   - `GROQ_API_KEY` - Get from [Groq Console](https://console.groq.com)
   - `FIGMA_ACCESS_TOKEN` - Get from [Figma Settings](https://www.figma.com/settings) (optional but recommended)
   - `OPENAI_API_KEY` - OpenAI API key (optional alternative to Groq)

4. **Run the Flask server:**
   ```bash
   python app.py
   ```
   - 🌐 API will start at `http://localhost:8000`

5. **Optional enhanced features:**
   ```bash
   # For advanced PDF processing
   pip install PyMuPDF
   
   # For image/OCR capabilities
   pip install pytesseract Pillow
   ```

### ⚡ Using Make Commands
```bash
# Quick development setup
make setup

# Start both backend and frontend
make dev

# Install all dependencies
make install

# Clean up temporary files
make clean
```

---

### ⚛️ Frontend Setup & Usage
1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm start
   ```
   - 🌐 UI available at `http://localhost:3000`
   - 🔄 Proxy to backend is automatically configured in `package.json`

3. **Build for production:**
   ```bash
   npm run build
   ```

---

## ✨ Main Features

<div align="center">

| Feature | Description | Status |
|---------|------------|--------|
| 🤖 **AI Test Generation** | Automated test case creation using advanced LLMs | ✅ Active |
| 🎨 **Figma Integration** | Extract UI components from Figma designs | ✅ Active |
| 📄 **Document Processing** | PDF & image text extraction with OCR | ✅ Active |
| 🧠 **RAG System** | ChromaDB-powered intelligent retrieval | ✅ Active |
| 🔄 **Multi-LLM Support** | Works with Groq, OpenAI, and other APIs | ✅ Active |
| 📊 **Analytics & Learning** | User feedback improves future generations | ✅ Active |
| 🌐 **Web Interface** | Modern React.js frontend | ✅ Active |
| 🔍 **Requirement Analysis** | Smart requirement extraction & coverage | ✅ Active |

</div>

### 🔥 Key Capabilities
- **🤖 Automated test case generation**: AI-powered, supports user stories + PDF/image attachments
- **🎨 Figma integration**: Extract UI components and design patterns from Figma files for comprehensive testing
- **🧠 RAG system**: Retrieval-augmented generation for smarter test case synthesis (ChromaDB-powered)
- **⚡ Prompt engineering**: Modular advanced prompting with design-aware context
- **🔄 LLM flexibility**: Works with Groq and OpenAI APIs
- **📄 PDF/image parsing**: Extracts text from complex docs/screenshots with OCR
- **🔍 Requirement analysis**: Advanced requirement extraction and coverage analysis
- **📈 Feedback/learning**: User feedback continuously improves future test cases

---

## 🎨 Figma Integration Setup

### 🔑 Getting Your Figma Access Token
1. **Navigate to Figma Settings** → Account → [Personal Access Tokens](https://www.figma.com/settings)
2. **Click "Create new token"**
3. **Name your token** (e.g., "TestCase Generator")
4. **Copy the generated token** ⚠️ *Save it securely - you won't see it again!*
5. **Add to your `.env` file:**
   ```bash
   FIGMA_ACCESS_TOKEN=your_token_here
   ```

### 🔗 Supported Figma URL Formats
```
✅ https://www.figma.com/file/[file-key]/[file-name]
✅ https://www.figma.com/design/[file-key]/[file-name]  
✅ URLs with specific node selection: #[node-id]
```

### 🎯 What Gets Extracted
| Component Type | Extracted Data | Generated Tests |
|---------------|----------------|-----------------|
| 🔘 **Buttons** | Text, states, interactions | Click tests, state validation |
| 📝 **Input Fields** | Placeholders, validation | Input validation, error cases |
| 📋 **Forms** | Field relationships | End-to-end form testing |
| 🎛️ **Dropdowns** | Options, selections | Selection tests, edge cases |
| 🪟 **Modals** | Trigger conditions | Open/close, backdrop tests |
| 🧩 **Components** | Design patterns | Pattern-specific test suites |

### 🚀 Usage Example
```javascript
// Paste Figma URL in the web interface
https://www.figma.com/file/abc123/My-Design-File

// AI will automatically:
// 1. Validate URL and access permissions
// 2. Extract UI components and interactions  
// 3. Generate comprehensive test cases
// 4. Include design-specific test scenarios
```

---

## 🛠️ API Documentation

### 📡 Core Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| `POST` | `/api/v1/generate-test-cases` | 🎯 Generate test cases | `story`, `files`, `figma_url` |
| `POST` | `/api/v1/validate-figma` | ✅ Validate Figma designs | `figma_url` |
| `POST` | `/api/v1/figma-components` | 🔍 Get component analysis | `figma_url`, `node_id` |
| `POST` | `/api/v1/analyze-requirements` | 📊 Analyze coverage | `requirements`, `test_cases` |
| `GET`  | `/api/v1/health` | 💚 Health check | - |
| `POST` | `/api/v1/feedback` | 📈 Submit feedback | `test_cases`, `feedback`, `quality_score` |

### 📝 Example Usage

<details>
<summary>🎯 Generate Test Cases</summary>

```bash
curl -X POST http://localhost:8000/api/v1/generate-test-cases \
  -H "Content-Type: application/json" \
  -d '{
    "story": "As a user, I want to login to access my dashboard",
    "figma_url": "https://www.figma.com/file/abc123/login-flow"
  }'
```

</details>

<details>
<summary>✅ Validate Figma URL</summary>

```bash
curl -X POST http://localhost:8000/api/v1/validate-figma \
  -H "Content-Type: application/json" \
  -d '{
    "figma_url": "https://www.figma.com/file/abc123/design-file"
  }'
```

</details>

### 📊 Response Format
```json
{
  "success": true,
  "test_cases": [...],
  "metadata": {
    "total_cases": 5,
    "generation_time": "2.3s",
    "figma_components": 12
  }
}
```

## 🔐 Security & Environment Setup

> ⚠️ **Security Notice**: Never commit your `.env` file with real API keys!

### 🛡️ Environment Variables
```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional but recommended  
FIGMA_ACCESS_TOKEN=your_figma_personal_access_token_here

# Alternative LLM (optional)
OPENAI_API_KEY=your_openai_api_key_here
```

### 🔒 Security Features
- ✅ `.env` files are in `.gitignore`
- ✅ No hardcoded API keys in source code
- ✅ Secure environment variable handling
- ✅ Input validation and sanitization

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **🍴 Fork the repository**
2. **🌿 Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **💾 Commit your changes**: `git commit -m 'Add amazing feature'`
4. **📤 Push to the branch**: `git push origin feature/amazing-feature`
5. **🔄 Open a Pull Request**

### 🐛 Bug Reports
Found a bug? Please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version, etc.)

---

## 📈 Roadmap

- [ ] 🔄 Support for additional LLM providers
- [ ] 🎨 Enhanced Figma component detection
- [ ] 📱 Mobile app support
- [ ] 🌍 Multi-language support
- [ ] 🤖 Advanced AI test optimization
- [ ] 📊 Enhanced analytics dashboard

---

## 🙏 Acknowledgments

- **[Groq](https://groq.com)** for lightning-fast LLM inference
- **[Figma](https://figma.com)** for excellent design API
- **[ChromaDB](https://www.trychroma.com/)** for vector database capabilities
- **[React](https://reactjs.org/)** for the frontend framework

---

## 👨‍💻 Project Authors

<div align="center">

**Bhanu Pratap Singh**  
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/yourusername)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/yourusername)

</div>

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Troubleshooting

<details>
<summary>🐍 Python/Backend Issues</summary>

**PDF Processing Issues:**
```bash
pip install PyMuPDF  # For advanced PDF support
```

**Image/OCR Issues:**
```bash
pip install pytesseract Pillow
# Also install Tesseract: brew install tesseract (macOS)
```

**API Key Issues:**
- Ensure `.env` file exists in `/backend` directory
- Verify API keys are valid and not expired
- Check API key permissions (especially for Figma)

</details>

<details>
<summary>⚛️ Frontend/React Issues</summary>

**Port Conflicts:**
- Backend runs on port 8000
- Frontend runs on port 3000
- Ensure ports are available

**CORS Issues:**
- Proxy is configured in `package.json`
- Check backend is running before starting frontend

</details>

<details>
<summary>🎨 Figma Integration Issues</summary>

**Access Token Problems:**
- Token must have file access permissions
- Check if Figma file is public or shared with your account
- Verify URL format is correct

**URL Format Issues:**
```
✅ Correct: https://www.figma.com/file/abc123/design-name
❌ Wrong: https://www.figma.com/proto/abc123/design-name
```

</details>

---

<div align="center">

**⭐ If this project helped you, please give it a star! ⭐**

![Visitor Count](https://profile-counter.glitch.me/yourusername-AI_TestCase_Generator_Project/count.svg)

*Made with ❤️ by [Bhanu Pratap Singh](https://github.com/yourusername)*

</div>
