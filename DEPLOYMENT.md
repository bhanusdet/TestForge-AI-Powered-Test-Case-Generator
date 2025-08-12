# 🚀 TestForge AI - Deployment Guide

## **Quick Start**

### **1. Clone Repository**
```bash
git clone https://github.com/bhanusdet/TestForge-AI-Powered-Test-Case-Generator.git
cd TestForge-AI-Powered-Test-Case-Generator
```

### **2. Run Setup Script**
```bash
./setup.sh
```

### **3. Configure API Key**
```bash
# Edit backend/.env file
nano backend/.env

# Add your GROQ API key:
GROQ_API_KEY=your_groq_api_key_here
```

### **4. Start Application**
```bash
make dev
```

**Access Points:**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000

---

## **Manual Setup**

### **Backend Setup**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python setup_learning_system.py
cp .env.example .env
# Edit .env with your GROQ_API_KEY
```

### **Frontend Setup**
```bash
cd frontend
npm install
```

### **Start Services**
```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate && python app.py

# Terminal 2 - Frontend  
cd frontend && npm start
```

---

## **Production Deployment**

### **Docker Deployment** (Recommended)

**Create Dockerfile for Backend:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY backend/ .
RUN pip install -r requirements.txt
RUN python setup_learning_system.py

EXPOSE 8000
CMD ["python", "app.py"]
```

**Create Dockerfile for Frontend:**
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY frontend/ .
RUN npm install
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
EXPOSE 80
```

### **Environment Variables**
```bash
# Backend (.env)
GROQ_API_KEY=your_groq_api_key_here
RAG_TOP_K=5
EMBEDDING_MODEL=all-mpnet-base-v2
LEARNING_ENABLED=true
FEEDBACK_THRESHOLD=3.0
FLASK_ENV=production
```

---

## **Troubleshooting**

### **Common Issues**

**1. GROQ API Key Missing**
```bash
# Check if API key is set
cat backend/.env | grep GROQ_API_KEY
```

**2. Python Dependencies**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

**3. Node Dependencies**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**4. Learning System**
```bash
cd backend
source venv/bin/activate
python setup_learning_system.py
```

### **Port Conflicts**
```bash
# Change backend port in app.py
app.run(host='0.0.0.0', port=8001, debug=True)

# Update frontend proxy in package.json
"proxy": "http://localhost:8001"
```

---

## **API Endpoints**

### **Test Case Generation**
```bash
POST /api/v1/generate-test-cases
Content-Type: multipart/form-data

Form Data:
- story: "As a user, I want to..."
- attachments: [files] (optional)
```

### **Feedback Submission**
```bash
POST /api/v1/feedback
Content-Type: application/json

{
  "story_id": "12345",
  "quality_score": 4.5,
  "feedback": "Great coverage!"
}
```

### **Learning Statistics**
```bash
GET /api/v1/learning-stats
```

---

## **Performance Optimization**

### **Backend Optimizations**
- Use Redis for caching
- Implement connection pooling
- Add request rate limiting
- Use async processing for heavy tasks

### **Frontend Optimizations**
- Enable code splitting
- Implement lazy loading
- Use React.memo for expensive components
- Optimize bundle size

---

## **Monitoring & Logging**

### **Backend Logging**
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### **Frontend Error Tracking**
- Implement error boundaries
- Use monitoring tools like Sentry
- Add performance monitoring

---

## **Security Considerations**

### **API Security**
- Add authentication middleware
- Implement CORS properly
- Use HTTPS in production
- Add input validation

### **File Upload Security**
- Validate file types
- Scan for malware
- Limit file sizes
- Use secure storage

---

## **Contributing**

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

---

## **License**

MIT License - See LICENSE file for details.

---

## **Support**

- **Issues**: https://github.com/bhanusdet/TestForge-AI-Powered-Test-Case-Generator/issues
- **Documentation**: Check README.md and ENHANCED_FEATURES.md
- **Author**: Bhanu Pratap Singh