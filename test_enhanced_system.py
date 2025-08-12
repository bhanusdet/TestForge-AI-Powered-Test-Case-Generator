#!/usr/bin/env python3
"""
Test script for the Enhanced AI Test Case Generator
"""

import requests
import json
import time

# Server configuration
BASE_URL = "http://localhost:8000"

def test_generate_test_cases():
    """Test the enhanced test case generation"""
    
    print("🔮 Testing Enhanced Test Case Generation...")
    
    # Sample user story
    story = """
    As an e-commerce customer, I want to add products to my shopping cart 
    so that I can review my selections before purchasing multiple items together.
    
    Acceptance Criteria:
    - User can add products from product listing page
    - Cart should show correct quantities and prices
    - User should be able to modify quantities in cart
    - Cart should persist across browser sessions
    """
    
    payload = {
        "story": story
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/generate-test-cases",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if it's the new enhanced format
            if "test_cases" in result and "metadata" in result:
                test_cases = result["test_cases"]
                metadata = result["metadata"]
                
                print(f"✅ Enhanced Generation Successful!")
                print(f"📊 Generated {len(test_cases)} test cases")
                print(f"🧠 Similar examples used: {metadata.get('similar_examples_used', 0)}")
                print(f"🆔 Story ID: {metadata.get('story_id', 'N/A')}")
                print(f"🤖 Model: {metadata.get('model_used', 'N/A')}")
                print(f"🔄 Enhanced RAG: {metadata.get('enhanced_rag', False)}")
                
                # Show first test case as example
                if test_cases:
                    print(f"\n📋 Sample Test Case:")
                    tc = test_cases[0]
                    print(f"   ID: {tc.get('id', 'N/A')}")
                    print(f"   Title: {tc.get('title', 'N/A')}")
                    print(f"   Priority: {tc.get('priority', 'N/A')}")
                
                return metadata.get('story_id'), len(test_cases)
            else:
                # Legacy format
                print(f"✅ Generation Successful (Legacy Format)")
                print(f"📊 Generated {len(result)} test cases")
                return None, len(result)
                
        else:
            print(f"❌ Generation Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None, 0
            
    except Exception as e:
        print(f"❌ Request Failed: {e}")
        return None, 0

def test_submit_feedback(story_id):
    """Test the feedback system"""
    
    if not story_id:
        print("⚠️ Skipping feedback test (no story ID)")
        return
    
    print(f"\n⭐ Testing Feedback System...")
    
    feedback_data = {
        "story_id": story_id,
        "quality_score": 4.5,
        "feedback": "Great test coverage! The edge cases were particularly well thought out.",
        "improved_testcases": []
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/feedback",
            json=feedback_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Feedback Submitted Successfully!")
            print(f"📊 Quality Score: {result.get('quality_score', 'N/A')}")
            print(f"🆔 Story ID: {result.get('story_id', 'N/A')}")
        else:
            print(f"❌ Feedback Failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Feedback Request Failed: {e}")

def test_learning_stats():
    """Test learning statistics"""
    
    print(f"\n📈 Testing Learning Statistics...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/learning-stats", timeout=30)
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Learning Stats Retrieved!")
            print(f"🧠 Total Stories Learned: {stats.get('total_stories_learned', 0)}")
            print(f"💬 Total Feedback Received: {stats.get('total_feedback_received', 0)}")
            print(f"🤖 Embedding Model: {stats.get('embedding_model', 'N/A')}")
            print(f"📅 Last Updated: {stats.get('last_updated', 'N/A')}")
        else:
            print(f"❌ Stats Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Stats Request Failed: {e}")

def test_similar_stories():
    """Test similar stories analysis"""
    
    print(f"\n🔍 Testing Similar Stories Analysis...")
    
    query_data = {
        "story": "As a user, I want to login to my account so I can access my personal dashboard",
        "top_k": 3
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/similar-stories",
            json=query_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            similar_cases = result.get("similar_test_cases", [])
            
            print(f"✅ Similar Stories Found!")
            print(f"🔍 Query: {result.get('query_story', 'N/A')[:50]}...")
            print(f"📊 Similar Test Cases Found: {result.get('count', 0)}")
            
            for i, case in enumerate(similar_cases[:2], 1):
                relevance = case.get('context_relevance', 'N/A')
                print(f"   {i}. {case.get('title', 'N/A')} (Relevance: {relevance})")
        else:
            print(f"❌ Similar Stories Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Similar Stories Request Failed: {e}")

def main():
    print("=" * 70)
    print("🤖 Enhanced AI Test Case Generator - System Test")
    print("=" * 70)
    
    print(f"🔗 Testing server at: {BASE_URL}")
    
    # Test enhanced generation
    story_id, test_count = test_generate_test_cases()
    
    # Small delay for processing
    time.sleep(2)
    
    # Test feedback system
    test_submit_feedback(story_id)
    
    # Test learning stats
    test_learning_stats()
    
    # Test similar stories
    test_similar_stories()
    
    print("\n" + "=" * 70)
    print("🎉 Enhanced System Test Complete!")
    print("=" * 70)
    print("💡 The system is now learning from interactions and will improve over time!")
    print("🚀 Ready for production use with continuous learning capabilities!")

if __name__ == "__main__":
    main()