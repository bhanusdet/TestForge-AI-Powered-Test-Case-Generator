#!/usr/bin/env python3
"""
Setup script for initializing the enhanced learning system
"""

import os
import sys
import requests
import json
from enhanced_rag_helper import rag_helper

def setup_learning_system():
    """Initialize the learning system with sample data and configurations"""
    
    print("🚀 Setting up Enhanced AI Test Case Generator Learning System...")
    
    try:
        # 1. Initialize RAG helper with sample data
        print("\n📚 Loading sample test cases into vector database...")
        
        sample_file = 'sample_testcases.json'
        if os.path.exists(sample_file):
            rag_helper.ingest_testcases_from_json(sample_file)
            print(f"✅ Successfully loaded sample test cases from {sample_file}")
        else:
            print(f"⚠️ Sample file {sample_file} not found. Creating minimal dataset...")
            create_minimal_dataset()
        
        # 2. Test the system
        print("\n🧪 Testing the enhanced RAG system...")
        test_story = "As a user, I want to add products to my shopping cart so that I can purchase them later."
        
        similar_cases = rag_helper.retrieve_similar_with_context(test_story, top_k=3)
        print(f"✅ RAG system working! Found {len(similar_cases)} similar test cases")
        
        # 3. Get system stats
        stats = rag_helper.get_learning_stats()
        print(f"\n📊 System Statistics:")
        print(f"   - Total stories in database: {stats.get('total_stories_learned', 0)}")
        print(f"   - Total feedback entries: {stats.get('total_feedback_received', 0)}")
        print(f"   - Embedding model: {stats.get('embedding_model', 'N/A')}")
        
        print(f"\n✅ Learning system setup completed successfully!")
        print(f"💡 The system will now learn from each interaction and improve over time.")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

def create_minimal_dataset():
    """Create a minimal dataset if sample file is missing"""
    
    minimal_data = [
        {
            "userStory": "As a user, I want to login to my account so that I can access my personal information.",
            "testCases": [
                {
                    "id": "TC_LOGIN_001",
                    "title": "Valid login with correct credentials",
                    "preconditions": "User has a valid registered account",
                    "steps": "1. Navigate to login page\n2. Enter valid username\n3. Enter valid password\n4. Click login button",
                    "expected": "User is successfully logged in and redirected to dashboard",
                    "priority": "High"
                }
            ]
        },
        {
            "userStory": "As a customer, I want to add products to cart so that I can purchase multiple items together.",
            "testCases": [
                {
                    "id": "TC_CART_001", 
                    "title": "Add single product to cart",
                    "preconditions": "User is on product page with available product",
                    "steps": "1. Select product quantity\n2. Click 'Add to Cart' button\n3. Verify cart notification",
                    "expected": "Product added to cart with correct quantity and price",
                    "priority": "High"
                }
            ]
        }
    ]
    
    with open('sample_testcases.json', 'w') as f:
        json.dump(minimal_data, f, indent=2)
    
    rag_helper.ingest_testcases_from_json('sample_testcases.json')
    print("✅ Created and loaded minimal dataset")

def test_api_endpoints():
    """Test the API endpoints to ensure they're working"""
    
    base_url = "http://localhost:8000"
    
    print("\n🔗 Testing API endpoints...")
    
    try:
        # Test learning stats endpoint
        response = requests.get(f"{base_url}/api/v1/learning-stats")
        if response.status_code == 200:
            print("✅ Learning stats endpoint working")
        else:
            print(f"⚠️ Learning stats endpoint returned {response.status_code}")
    except:
        print("ℹ️ API endpoints will be available when the server is running")

if __name__ == "__main__":
    print("=" * 70)
    print("🤖 AI Test Case Generator - Enhanced Learning System Setup")
    print("=" * 70)
    
    success = setup_learning_system()
    
    if success:
        print("\n" + "=" * 70)
        print("🎉 Setup Complete! Next Steps:")
        print("=" * 70)
        print("1. Run: python app.py")
        print("2. Test the API: POST /api/v1/generate-test-cases")
        print("3. Submit feedback: POST /api/v1/feedback")
        print("4. View learning stats: GET /api/v1/learning-stats")
        print("\n💡 The system will now learn and improve with each use!")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1)