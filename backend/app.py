# app.py
import os
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import datetime

# your helpers - keep these files in the same folder
from enhanced_rag_helper import rag_helper
from image_helper import get_text_from_image
from pdf_helper import get_text_from_pdf
from prompt_engineering import AdvancedPromptEngineer

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
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0
    }
    r = requests.post(GROQ_URL, headers=headers, json=body, timeout=60)
    r.raise_for_status()
    return r.json()

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
                    text = get_text_from_pdf(tmp_path)  # your helper
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

    # Enhanced RAG retrieval with learning capabilities
    try:
        similar_test_cases = rag_helper.retrieve_similar_with_context(full_story, top_k=5)
        print(f"✅ Retrieved {len(similar_test_cases)} similar test cases")
    except Exception as e:
        print("RAG retrieval error:", e)
        similar_test_cases = []

    # Build enhanced prompt with better context
    story_context = build_enhanced_story_context(full_story)
    prompt = AdvancedPromptEngineer.build_enhanced_prompt(
        full_story, similar_test_cases, story_context
    )
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

    # 🧠 LEARNING: Add this interaction to the knowledge base for future improvement
    try:
        story_id = story_context.get('story_hash', 'unknown')
        rag_helper.add_generated_story_context(
            user_story=full_story,
            generated_testcases=test_cases,
            feedback_score=None  # Will be updated when user provides feedback
        )
        print(f"✅ Added story to learning database: {story_id}")
    except Exception as e:
        print(f"⚠️ Failed to add to learning database: {e}")

    # Return enhanced response with metadata
    response = {
        "test_cases": test_cases,
        "metadata": {
            "story_id": story_context.get('story_hash'),
            "generated_count": len(test_cases),
            "similar_examples_used": len(similar_test_cases),
            "generation_timestamp": story_context.get('timestamp'),
            "model_used": "llama3-8b-8192",
            "enhanced_rag": True
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
    Submit feedback on generated test cases to improve future generations
    """
    try:
        data = request.get_json()
        
        story_id = data.get('story_id')
        quality_score = data.get('quality_score')  # 1-5 scale
        user_feedback = data.get('feedback', '')
        improved_testcases = data.get('improved_testcases', [])
        
        if not story_id or quality_score is None:
            return jsonify({"error": "Missing story_id or quality_score"}), 400
        
        # Add feedback to learning system
        rag_helper.add_feedback(
            story_id=str(story_id),
            testcase_quality_score=float(quality_score),
            user_feedback=user_feedback,
            improved_testcases=improved_testcases
        )
        
        return jsonify({
            "message": "Feedback submitted successfully",
            "story_id": story_id,
            "quality_score": quality_score
        })
        
    except Exception as e:
        print(f"Feedback submission error: {e}")
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


if __name__ == '__main__':
    app.run(debug=True, port=8000)