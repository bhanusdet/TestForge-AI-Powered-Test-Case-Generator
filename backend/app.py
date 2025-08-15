# app.py
import os
import tempfile
from typing import List, Dict
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import datetime

# Smart import with graceful fallbacks
def setup_rag_system():
    """Setup RAG system with graceful fallback"""
    try:
        from enhanced_rag_helper import rag_helper
        print("✅ RAG system loaded")
        return rag_helper
    except Exception as e:
        print(f"⚠️ RAG system not available: {e}")
        
        # Create mock RAG helper
        class MockRAGHelper:
            def retrieve_similar_with_context(self, story, top_k=5):
                return []
            def add_generated_story_context(self, **kwargs):
                pass
            def add_feedback(self, **kwargs):
                pass
            def get_learning_stats(self):
                return {"status": "RAG system not available"}
        
        return MockRAGHelper()

def setup_image_processing():
    """Setup image processing with graceful fallback"""
    try:
        from image_helper import get_text_from_image
        print("✅ Image processing loaded")
        return get_text_from_image
    except Exception as e:
        print(f"⚠️ Image processing not available: {e}")
        def fallback_image_processor(filepath):
            return "Image processing not available. Please install required dependencies."
        return fallback_image_processor

# Initialize systems
rag_helper = setup_rag_system()
get_text_from_image = setup_image_processing()

# --- Lazy loader helpers for heavy libraries ---
def lazy_import_transformers():
    import importlib
    return importlib.import_module('transformers')

def lazy_import_sentence_transformers():
    import importlib
    return importlib.import_module('sentence_transformers')

def lazy_import_pandas():
    import importlib
    return importlib.import_module('pandas')

def lazy_import_sklearn():
    import importlib
    return importlib.import_module('sklearn')
# Smart PDF processing with graceful fallbacks
def setup_pdf_processing():
    """Setup PDF processing with graceful fallbacks"""
    global get_text_from_pdf, get_detailed_pdf_content
    
    # Try enhanced PDF helper first
    try:
        from enhanced_pdf_helper import get_text_from_pdf, get_detailed_pdf_content
        print("✅ Using Enhanced PDF Processing")
        return "enhanced"
    except ImportError as e:
        print("\u26a0\ufe0f Advanced PDF extraction features are disabled (PyMuPDF not installed). To enable them, run: pip install PyMuPDF")
        
        # Fallback to basic PDF processing
        try:
            import pdfplumber
            
            def get_text_from_pdf(filepath):
                """Basic PDF text extraction fallback"""
                text = ""
                try:
                    with pdfplumber.open(filepath) as pdf:
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                    return text.strip() if text else None
                except Exception as e:
                    print(f"PDF extraction error: {e}")
                    return f"Error: Could not extract text from PDF - {str(e)}"
            
            def get_detailed_pdf_content(filepath):
                """Basic fallback for detailed content"""
                text = get_text_from_pdf(filepath)
                return {
                    'text_content': text or '',
                    'tables': [],
                    'images_text': [],
                    'metadata': {},
                    'structured_sections': [],
                    'extraction_method': ['basic'],
                    'quality_score': 0.5 if text else 0.0
                }
            
            print("⚠️ Using Basic PDF Processing (pdfplumber only)")
            return "basic"
            
        except ImportError:
            # Ultra-minimal fallback
            def get_text_from_pdf(filepath):
                return "PDF processing not available. Please install: pip install pdfplumber PyMuPDF"
            
            def get_detailed_pdf_content(filepath):
                return {
                    'text_content': get_text_from_pdf(filepath),
                    'tables': [],
                    'images_text': [],
                    'metadata': {},
                    'structured_sections': [],
                    'extraction_method': ['none'],
                    'quality_score': 0.0
                }
            
            print("❌ PDF processing not available - install dependencies")
            return "none"

# Initialize PDF processing
PDF_PROCESSING_MODE = setup_pdf_processing()
# Removed eager import of AdvancedPromptEngineer; now lazily imported in handlers for performance

load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY environment variable is required. Please set it in backend/.env file")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
# If you ever switch to OpenAI: set OPENAI_API_KEY and change URL+headers accordingly.

# ---------- Enhanced Utility Functions ----------
def build_enhanced_story_context(user_story: str) -> dict:
    """Build context information about the story for better prompting"""
    return {
        'story_hash': hash(user_story) % 10000,  # Simple story identifier
        'timestamp': datetime.now().isoformat(),
        'word_count': len(user_story.split())
    }

def call_groq(prompt: str):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0
    }
    r = requests.post(GROQ_URL, headers=headers, json=body, timeout=60)
    r.raise_for_status()
    return r.json()

def validate_and_filter_test_cases(test_cases: List[Dict], user_story: str) -> List[Dict]:
    """
    Validate test cases against story requirements and filter out-of-scope ones
    """
    try:
        from prompt_engineering import AdvancedPromptEngineer

        # Extract requirements from story
        story_requirements = AdvancedPromptEngineer.extract_requirements_from_story(user_story)

        validated_cases = []
        for test_case in test_cases:
            validation_result = AdvancedPromptEngineer.validate_test_case_scope(
                test_case, story_requirements
            )

            if validation_result['is_valid']:
                test_case['validation_score'] = validation_result['score']
                validated_cases.append(test_case)
            else:
                print(f"⚠️ Filtered out-of-scope test case: {test_case.get('title', 'Unknown')}")
                print(f"   Issues: {', '.join(validation_result['issues'])}")

        return validated_cases
    except Exception as e:
        print(f"⚠️ Validation failed, returning original test cases: {e}")
        return test_cases

# --------- Parser: convert LLM text into list of dicts ----------
def parse_testcases_from_text(content: str):
    """
    Parse LLM text into a list of test case dicts.
    This uses the same parsing logic you had before but returns a list directly.
    """
    def clean(text):
        return text.replace("**", "").strip()

    test_cases = []
    blocks = content.strip().split("\n\n")

    current_tc = {}
    current_field = None
    buffer = []

    for block in blocks:
        lines = block.strip().split("\n")
        for line in lines:
            line = line.strip()
            lower_line = line.lower()

            if ":" in line:
                # if we were reading previous field, flush it
                if current_field and buffer:
                    current_tc[current_field] = clean(" ".join(buffer))
                    buffer = []

                # detect field
                if "test case id" in lower_line:
                    if current_tc:
                        test_cases.append(current_tc)
                        current_tc = {}
                    current_field = "id"
                elif "title" in lower_line:
                    current_field = "title"
                elif "preconditions" in lower_line:
                    current_field = "preconditions"
                elif "test steps" in lower_line or "steps" in lower_line:
                    current_field = "steps"
                elif "expected result" in lower_line or "expected" in lower_line:
                    current_field = "expected"
                elif "actual result" in lower_line or "actual" in lower_line:
                    current_field = "actual"
                elif "requirement mapping" in lower_line or "mapping" in lower_line:
                    current_field = "requirement_mapping"
                elif "priority" in lower_line:
                    current_field = "priority"
                elif "status" in lower_line:
                    current_field = "status"
                else:
                    current_field = None

                # append the text after first ":" (if we have a valid field)
                if current_field:
                    buffer.append(line.split(":", 1)[1])
            else:
                # continuation line for current field
                buffer.append(line)

        # block finished -> flush buffer into current_field
        if current_field and buffer:
            current_tc[current_field] = clean(" ".join(buffer))
            buffer = []

    # end of blocks -> flush last tc
    if current_tc:
        test_cases.append(current_tc)

    # Normalise: ensure each test case has required keys
    normalized = []
    for i, tc in enumerate(test_cases, start=1):
        normalized.append({
            "id": tc.get("id") or f"TC_{i:03}",
            "title": tc.get("title", ""),
            "preconditions": tc.get("preconditions", ""),
            "steps": tc.get("steps", ""),
            "expected": tc.get("expected", ""),
            "actual": tc.get("actual", ""),
            "priority": tc.get("priority", ""),
            "requirement_mapping": tc.get("requirement_mapping", ""),
            "status": tc.get("status", "Pending")
        })

    return normalized

# ----------------- Routes -----------------

@app.route('/api/v1/generate-test-cases', methods=['POST'])
def generate_test_cases():
    """
    Accepts:
      - multipart/form-data with 'story' (form field) and multiple 'attachments' (files)
      - OR JSON { "story": "..." }
    Returns:
      - JSON array (list) of test case objects
    """
    extracted_texts = []
    user_story = ""

    # multipart
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        user_story = request.form.get('story', '') or ""
        files = request.files.getlist('attachments')
        for f in files:
            if not f or not f.filename:
                continue
            filename = secure_filename(f.filename)
            ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''

            # save to temp file and call appropriate extractor
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                f.save(tmp.name)
                tmp_path = tmp.name

            try:
                if ext in ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp']:
                    text = get_text_from_image(tmp_path)  # your helper
                elif ext == 'pdf':
                    # Use enhanced PDF processing
                    text = get_text_from_pdf(tmp_path)
                    
                    # Log PDF processing results for monitoring
                    try:
                        detailed_result = get_detailed_pdf_content(tmp_path)
                        quality_score = detailed_result.get('quality_score', 0.0)
                        methods_used = detailed_result.get('extraction_method', [])
                        tables_count = len(detailed_result.get('tables', []))
                        images_count = len(detailed_result.get('images_text', []))
                        
                        print(f"📄 PDF processed: Quality={quality_score:.2f}, "
                              f"Methods={methods_used}, Tables={tables_count}, "
                              f"Images={images_count}, Size={len(text)} chars")
                    except Exception as log_error:
                        print(f"⚠️ PDF processing logging failed: {log_error}")
                else:
                    text = None

                if text:
                    extracted_texts.append(text)
            finally:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    # JSON
    elif request.is_json:
        data = request.get_json()
        user_story = data.get('story', '') or ""
        extracted_texts = []
    else:
        return jsonify({"error": "Unsupported Content-Type"}), 415

    if not user_story and not extracted_texts:
        return jsonify({"error": "Missing user story or attachments"}), 400

    # Merge story + attachments
    full_story = "\n\n".join(filter(None, [user_story.strip()] + extracted_texts)).strip()

    # Enhanced RAG retrieval with learning capabilities (if available)
    try:
        similar_test_cases = rag_helper.retrieve_similar_with_context(full_story, top_k=5)
        print(f"✅ Retrieved {len(similar_test_cases)} similar test cases")
    except Exception as e:
        print("RAG retrieval error:", e)
        similar_test_cases = []

    # Build prompt (enhanced if RAG available, basic otherwise)
    story_context = build_enhanced_story_context(full_story)
    
    try:
        # Lazy import for cold start optimization
        from prompt_engineering import AdvancedPromptEngineer
        prompt = AdvancedPromptEngineer.build_enhanced_prompt(
            full_story, similar_test_cases, story_context
        )
        print("\u2705 Using enhanced prompt engineering")
    except Exception as e:
        print(f"\u26a0\ufe0f Advanced prompting not available: {e}")
        # Basic prompt fallback
        prompt = f"""Generate comprehensive test cases for the following user story.

IMPORTANT: Only test features and functionality explicitly mentioned in the user story below. 
Do not create test cases for features not described in the requirements.

User Story: {full_story}

SCOPE CONSTRAINTS:
- Test ONLY what is mentioned in the user story above
- Do not test admin features, integrations, or external systems unless explicitly mentioned
- Stay within the boundaries of the described functionality
- Each test case must map back to specific requirements in the story

Generate 3-5 detailed test cases with the following format for each:

Test Case ID: TC_XXX
Title: [Clear test case title]
Preconditions: [What needs to be set up before testing]
Requirement Mapping: [Which part of the user story this test validates]
Test Steps: 
1. [Step 1]
2. [Step 2]
3. [Step 3]
Expected Result: [What should happen]
Priority: [High/Medium/Low]

Make sure test cases cover positive scenarios, negative scenarios, and edge cases.
Remember: ONLY test what is explicitly described in the user story requirements."""
    print("\n===== FINAL PROMPT SENT TO GROQ =====\n")
    print(prompt)
    print("\n=====================================\n")
    try:
        resp_json = call_groq(prompt)
    except Exception as e:
        print("LLM request error:", e)
        return jsonify({"error": f"LLM request failed: {str(e)}"}), 500

    # Extract content safely
    try:
        llm_content = None
        # Groq / OpenAI compatible response shape:
        if "choices" in resp_json and len(resp_json["choices"]) > 0:
            choice = resp_json["choices"][0]
            # two possibilities: message.content or text
            if isinstance(choice, dict) and "message" in choice and "content" in choice["message"]:
                llm_content = choice["message"]["content"]
            elif "text" in choice:
                llm_content = choice["text"]
        if llm_content is None:
            # fallback: stringify top-level response
            llm_content = str(resp_json)
    except Exception as e:
        llm_content = str(resp_json)

    # Parse into structured test cases
    test_cases = parse_testcases_from_text(llm_content)

    # Validate and filter test cases to ensure they stay within requirements
    print(f"📋 Generated {len(test_cases)} test cases, validating scope...")
    test_cases = validate_and_filter_test_cases(test_cases, full_story)

    # If parser returned empty, include a fallback single testcase with raw LLM text so frontend sees something
    if not test_cases:
        test_cases = [{
            "id": "TC_001",
            "title": "LLM output (raw)",
            "preconditions": "",
            "steps": "",
            "expected": llm_content[:200] + ("..." if len(llm_content) > 200 else ""),
            "priority": "Medium",
            "status": "Pending"
        }]

    # 🧠 LEARNING: Add this interaction to the knowledge base (if available)
    try:
        story_id = story_context.get('story_hash', 'unknown')
        rag_helper.add_generated_story_context(
            user_story=full_story,
            generated_testcases=test_cases,
            feedback_score=None  # Will be updated when user provides feedback
        )
        print(f"✅ Added story to learning database: {story_id}")
    except Exception as e:
        print(f"⚠️ Learning system not available: {e}")

    # Return enhanced response with metadata
    response = {
        "test_cases": test_cases,
        "metadata": {
            "story_id": story_context.get('story_hash'),
            "generated_count": len(test_cases),
            "similar_examples_used": len(similar_test_cases),
            "generation_timestamp": story_context.get('timestamp'),
            "model_used": "openai/gpt-oss-120b",
            "pdf_processing": PDF_PROCESSING_MODE,
            "rag_available": hasattr(rag_helper, 'retrieve_similar_with_context') and callable(getattr(rag_helper, 'retrieve_similar_with_context', None)),
            "scope_validated": True
        }
    }
    
    return jsonify(response)


# Keep existing small screenshot endpoint (optional)
@app.route('/screenshot', methods=['POST'])
def screenshot():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        if ext == 'pdf':
            text = get_text_from_pdf(tmp_path)
            
            # Log enhanced PDF processing results
            try:
                detailed_result = get_detailed_pdf_content(tmp_path)
                quality_score = detailed_result.get('quality_score', 0.0)
                methods_used = detailed_result.get('extraction_method', [])
                print(f"📄 Screenshot PDF processed: Quality={quality_score:.2f}, Methods={methods_used}")
            except Exception:
                pass  # Don't fail if detailed processing fails
        else:
            text = get_text_from_image(tmp_path)
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    if text is None:
        return jsonify({"error": "Could not extract text from file"}), 500
    return jsonify({"text": text})


# ---------- NEW: Learning and Feedback Endpoints ----------

@app.route('/api/v1/feedback', methods=['POST'])
def submit_feedback():
    """
    🚀 Enhanced feedback submission with detailed learning data
    """
    try:
        data = request.get_json()
        
        story_id = data.get('story_id')
        quality_score = data.get('quality_score')  # 1-5 scale
        user_feedback = data.get('feedback', '')
        improved_testcases = data.get('improved_testcases', [])
        feedback_categories = data.get('feedback_categories', [])
        missing_scenarios = data.get('missing_scenarios', [])
        
        if not story_id or quality_score is None:
            return jsonify({"error": "Missing story_id or quality_score"}), 400
        
        # Validate quality score
        if not 1 <= quality_score <= 5:
            return jsonify({"error": "Quality score must be between 1 and 5"}), 400
        
        # 🧠 Add enhanced feedback to learning system
        rag_helper.add_feedback(
            story_id=str(story_id),
            testcase_quality_score=float(quality_score),
            user_feedback=user_feedback,
            improved_testcases=improved_testcases,
            feedback_categories=feedback_categories,
            missing_scenarios=missing_scenarios
        )
        
        # 📊 Prepare response with learning insights
        feedback_insight = ""
        if quality_score >= 4:
            feedback_insight = "Thank you! Your positive feedback helps us identify high-quality patterns."
        elif quality_score <= 2:
            feedback_insight = "We appreciate your critical feedback - it helps us improve significantly."
        else:
            feedback_insight = "Your balanced feedback helps us fine-tune our generation process."
        
        response_data = {
            "message": "Enhanced feedback submitted successfully",
            "story_id": story_id,
            "quality_score": quality_score,
            "categories_received": len(feedback_categories),
            "missing_scenarios_count": len(missing_scenarios),
            "improved_testcases_count": len(improved_testcases) if improved_testcases else 0,
            "learning_insight": feedback_insight,
            "impact": "This feedback will improve future test case generation for similar stories."
        }
        
        print(f"✅ Enhanced feedback received: Story {story_id}, Score: {quality_score}, "
              f"Categories: {feedback_categories}, Missing: {missing_scenarios}")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Enhanced feedback submission error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/learning-stats', methods=['GET'])
def get_learning_stats():
    """
    Get statistics about the learning system
    """
    try:
        stats = rag_helper.get_learning_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/initialize-learning', methods=['POST'])
def initialize_learning_system():
    """
    Initialize the learning system with sample data
    """
    try:
        # Initialize with sample test cases
        rag_helper.ingest_testcases_from_json('sample_testcases.json')
        
        stats = rag_helper.get_learning_stats()
        
        return jsonify({
            "message": "Learning system initialized successfully",
            "stats": stats
        })
        
    except Exception as e:
        print(f"Initialization error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/similar-stories', methods=['POST'])
def get_similar_stories():
    """
    Get similar stories for analysis (useful for debugging RAG)
    """
    try:
        data = request.get_json()
        user_story = data.get('story', '')
        top_k = data.get('top_k', 3)
        
        if not user_story:
            return jsonify({"error": "Missing user story"}), 400
        
        similar_cases = rag_helper.retrieve_similar_with_context(user_story, top_k)
        
        return jsonify({
            "query_story": user_story,
            "similar_test_cases": similar_cases,
            "count": len(similar_cases)
        })
        
    except Exception as e:
        print(f"Similar stories error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/feedback-analysis', methods=['GET'])
def get_feedback_analysis():
    """
    🔍 Get comprehensive feedback analysis and insights
    """
    try:
        # Lazy import for performance
        from feedback_analyzer import FeedbackAnalyzer
        analyzer = FeedbackAnalyzer()
        analysis = analyzer.analyze_feedback_patterns()
        
        return jsonify({
            "status": "success",
            "analysis": analysis,
            "generated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Feedback analysis error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/quality-insights', methods=['GET'])
def get_quality_insights():
    """
    📊 Get actionable insights for quality improvement
    """
    try:
        # Get current learning stats
        stats = rag_helper.get_learning_stats()
        
        # Calculate quality insights
        insights = {
            "current_performance": {
                "learning_effectiveness": stats.get("system_health", {}).get("learning_effectiveness", 0.5),
                "data_quality_score": stats.get("system_health", {}).get("data_quality_score", 0.0),
                "feedback_coverage": min(1.0, stats.get("total_feedback_received", 0) / max(stats.get("total_stories_learned", 1), 1))
            },
            "recommendations": [],
            "next_steps": []
        }
        
        # Generate recommendations based on current state
        effectiveness = insights["current_performance"]["learning_effectiveness"]
        feedback_coverage = insights["current_performance"]["feedback_coverage"]
        
        if effectiveness < 0.6:
            insights["recommendations"].append({
                "priority": "HIGH",
                "area": "Quality Improvement",
                "issue": "Low learning effectiveness",
                "action": "Focus on collecting feedback for low-performing test cases"
            })
        
        if feedback_coverage < 0.3:
            insights["recommendations"].append({
                "priority": "MEDIUM", 
                "area": "Data Collection",
                "issue": "Insufficient feedback coverage",
                "action": "Encourage more users to provide feedback on generated test cases"
            })
        
        # Next steps based on system state
        total_feedback = stats.get("total_feedback_received", 0)
        if total_feedback < 10:
            insights["next_steps"].append("Collect at least 10 feedback samples to enable meaningful analysis")
        elif total_feedback < 50:
            insights["next_steps"].append("Gather more diverse feedback across different domains")
        else:
            insights["next_steps"].append("Focus on fine-tuning based on identified patterns")
        
        return jsonify(insights)
        
    except Exception as e:
        print(f"Quality insights error: {e}")
        return jsonify({"error": str(e)}), 500


# ---------- NEW: Enhanced PDF Analysis Endpoint ----------

@app.route('/api/v1/analyze-pdf', methods=['POST'])
def analyze_pdf():
    """
    🔍 Enhanced PDF analysis endpoint
    Returns detailed PDF content analysis including tables, images, quality metrics
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No PDF file provided"}), 400
        
        file = request.files['file']
        if not file or not file.filename:
            return jsonify({"error": "No file selected"}), 400
        
        filename = secure_filename(file.filename)
        if not filename.lower().endswith('.pdf'):
            return jsonify({"error": "Only PDF files are supported"}), 400
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
        
        try:
            # Get detailed analysis
            detailed_result = get_detailed_pdf_content(tmp_path)
            
            # Prepare response with analysis
            analysis = {
                "file_info": {
                    "filename": filename,
                    "processed_at": datetime.now().isoformat()
                },
                "extraction_summary": {
                    "quality_score": detailed_result.get('quality_score', 0.0),
                    "methods_used": detailed_result.get('extraction_method', []),
                    "total_characters": len(detailed_result.get('text_content', '')),
                    "sections_found": len(detailed_result.get('structured_sections', [])),
                    "tables_count": len(detailed_result.get('tables', [])),
                    "images_with_text": len(detailed_result.get('images_text', []))
                },
                "content": {
                    "main_text": detailed_result.get('text_content', ''),
                    "structured_sections": detailed_result.get('structured_sections', [])
                },
                "tables": detailed_result.get('tables', []),
                "images_text": detailed_result.get('images_text', []),
                "metadata": detailed_result.get('metadata', {}),
                "recommendations": []
            }
            
            # Add processing recommendations
            quality_score = analysis["extraction_summary"]["quality_score"]
            if quality_score < 0.3:
                analysis["recommendations"].append({
                    "type": "warning",
                    "message": "Low extraction quality detected. Document might be scanned or have complex formatting."
                })
            elif quality_score < 0.6:
                analysis["recommendations"].append({
                    "type": "info", 
                    "message": "Moderate extraction quality. Some content might need manual review."
                })
            else:
                analysis["recommendations"].append({
                    "type": "success",
                    "message": "High quality extraction achieved."
                })
            
            if len(analysis["tables"]) > 0:
                analysis["recommendations"].append({
                    "type": "info",
                    "message": f"Found {len(analysis['tables'])} tables that have been processed and included."
                })
            
            return jsonify(analysis)
            
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass
                
    except Exception as e:
        print(f"PDF analysis error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/analyze-requirements', methods=['POST'])
def analyze_requirements():
    """
    📊 Analyze requirement coverage for generated test cases
    """
    try:
        data = request.get_json()
        user_story = data.get('user_story', '')
        test_cases = data.get('test_cases', [])

        if not user_story or not test_cases:
            return jsonify({"error": "Missing user_story or test_cases"}), 400

        # Import requirement analyzer
        from requirement_analyzer import RequirementAnalyzer

        # Extract requirements
        requirements = RequirementAnalyzer.extract_testable_requirements(user_story)

        # Analyze coverage
        coverage_analysis = RequirementAnalyzer.analyze_test_coverage(test_cases, user_story)

        # Generate report
        coverage_report = RequirementAnalyzer.generate_coverage_report(test_cases, user_story)

        return jsonify({
            "status": "success",
            "requirements": requirements,
            "coverage_analysis": coverage_analysis,
            "coverage_report": coverage_report,
            "recommendations": [
                "Focus on uncovered requirements" if coverage_analysis['coverage_percentage'] < 80 else "Good coverage achieved",
                "Review scope violations" if any(tc['scope_issues'] for tc in coverage_analysis['test_case_analysis']) else "All tests within scope"
            ]
        })

    except Exception as e:
        print(f"Requirement analysis error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=8000)