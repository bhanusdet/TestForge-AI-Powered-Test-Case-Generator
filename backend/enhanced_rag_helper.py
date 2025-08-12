# enhanced_rag_helper.py

from sentence_transformers import SentenceTransformer
import chromadb
import json
import os
from datetime import datetime
import hashlib
from typing import List, Dict, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedRAGHelper:
    def __init__(self, db_path: str = "./chroma_db", collection_name: str = "testcases"):
        """
        Initialize enhanced RAG system with persistent storage and learning capabilities
        """
        # Use better embedding model for improved accuracy
        self.model = SentenceTransformer("all-mpnet-base-v2")  # Better than all-MiniLM-L6-v2
        
        # Persistent ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Better for sentence embeddings
        )
        
        # Learning system collections
        self.feedback_collection = self.client.get_or_create_collection(
            name="feedback_data",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.context_collection = self.client.get_or_create_collection(
            name="story_contexts",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info("Enhanced RAG system initialized with persistent storage")
    
    def ingest_testcases_from_json(self, filepath: str):
        """Load sample test cases with enhanced metadata"""
        with open(filepath, 'r') as f:
            examples = json.load(f)
        
        for i, item in enumerate(examples):
            story = item['userStory']
            test_cases = item['testCases']
            
            # Create richer embeddings
            embedding = self.model.encode(story).tolist()
            
            # Enhanced metadata with keywords and domain info (ChromaDB compatible)
            metadata = {
                "testCases": json.dumps(test_cases),  # Serialize to JSON string
                "domain": self._extract_domain(story),
                "keywords": ",".join(self._extract_keywords(story)),  # Join as string
                "num_testcases": len(test_cases),
                "ingestion_date": datetime.now().isoformat(),
                "source": "sample_data"
            }
            
            self.collection.add(
                documents=[story],
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[f"sample_{i}"]
            )
        
        logger.info(f"✅ Ingested {len(examples)} sample user stories")
    
    def add_generated_story_context(self, user_story: str, generated_testcases: List[Dict], 
                                  feedback_score: Optional[float] = None):
        """
        Add newly generated test cases to the knowledge base for future learning
        """
        try:
            # Create unique ID for this story
            story_id = self._generate_story_id(user_story)
            
            # Create embedding
            embedding = self.model.encode(user_story).tolist()
            
            # Enhanced metadata (ChromaDB compatible)
            metadata = {
                "testCases": json.dumps(generated_testcases),  # Serialize to JSON string
                "domain": self._extract_domain(user_story),
                "keywords": ",".join(self._extract_keywords(user_story)),  # Join as string
                "num_testcases": len(generated_testcases),
                "creation_date": datetime.now().isoformat(),
                "feedback_score": feedback_score or 0.0,  # Ensure numeric
                "source": "generated",
                "story_length": len(user_story),
                "complexity_score": self._calculate_complexity_score(user_story)
            }
            
            # Add to knowledge base
            self.collection.add(
                documents=[user_story],
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[story_id]
            )
            
            logger.info(f"✅ Added new story context: {story_id}")
            
        except Exception as e:
            logger.error(f"Failed to add story context: {e}")
    
    def retrieve_similar_with_context(self, user_story: str, top_k: int = 5) -> List[Dict]:
        """
        Enhanced retrieval with contextual understanding and quality scoring
        """
        try:
            query_embedding = self.model.encode(user_story).tolist()
            
            # Get more candidates for better filtering
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k * 3, 20),  # Get more candidates
                include=['metadatas', 'documents', 'distances']
            )
            
            # Extract and score results
            scored_results = []
            story_domain = self._extract_domain(user_story)
            story_keywords = self._extract_keywords(user_story)
            
            for i, (metadata, distance, document) in enumerate(zip(
                results['metadatas'][0], results['distances'][0], results['documents'][0]
            )):
                # Calculate relevance score
                relevance_score = self._calculate_relevance_score(
                    user_story, document, metadata, distance, story_domain, story_keywords
                )
                
                scored_results.append({
                    'metadata': metadata,
                    'document': document,
                    'distance': distance,
                    'relevance_score': relevance_score
                })
            
            # Sort by relevance score and take top results
            scored_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Extract test cases from top results
            combined_test_cases = []
            seen_ids = set()
            
            for result in scored_results[:top_k]:
                test_cases_str = result['metadata'].get('testCases', '[]')
                try:
                    test_cases = json.loads(test_cases_str) if isinstance(test_cases_str, str) else test_cases_str
                except:
                    test_cases = []
                
                for case in test_cases:
                    case_id = case.get('id')
                    if case_id not in seen_ids:
                        # Add context score to test case
                        case['context_relevance'] = result['relevance_score']
                        combined_test_cases.append(case)
                        seen_ids.add(case_id)
            
            # Add intelligent edge cases if needed
            if len(combined_test_cases) < top_k:
                edge_cases = self._generate_domain_specific_edge_cases(story_domain, user_story)
                combined_test_cases.extend(edge_cases[:top_k - len(combined_test_cases)])
            
            logger.info(f"Retrieved {len(combined_test_cases)} relevant test cases")
            return combined_test_cases[:top_k]
            
        except Exception as e:
            logger.error(f"Error in similarity retrieval: {e}")
            return self._get_fallback_cases()
    
    def add_feedback(self, story_id: str, testcase_quality_score: float, 
                    user_feedback: str = "", improved_testcases: List[Dict] = None):
        """
        Add user feedback to improve future generations
        """
        try:
            feedback_data = {
                "story_id": story_id,
                "quality_score": testcase_quality_score,
                "user_feedback": user_feedback,
                "improved_testcases": json.dumps(improved_testcases or []),  # Serialize
                "feedback_date": datetime.now().isoformat()
            }
            
            # Create embedding from feedback
            feedback_text = f"{user_feedback} Quality: {testcase_quality_score}"
            embedding = self.model.encode(feedback_text).tolist()
            
            self.feedback_collection.add(
                documents=[feedback_text],
                embeddings=[embedding],
                metadatas=[feedback_data],
                ids=[f"feedback_{story_id}_{datetime.now().timestamp()}"]
            )
            
            logger.info(f"✅ Added feedback for story: {story_id}")
            
        except Exception as e:
            logger.error(f"Failed to add feedback: {e}")
    
    def _generate_story_id(self, story: str) -> str:
        """Generate unique ID for a story"""
        return f"story_{hashlib.md5(story.encode()).hexdigest()[:8]}"
    
    def _extract_domain(self, story: str) -> str:
        """Extract domain/category from user story"""
        story_lower = story.lower()
        
        domain_keywords = {
            'ecommerce': ['cart', 'product', 'checkout', 'order', 'purchase', 'shop', 'inventory'],
            'authentication': ['login', 'password', 'user', 'account', 'register', 'auth'],
            'finance': ['payment', 'transaction', 'billing', 'invoice', 'money', 'credit'],
            'social': ['post', 'comment', 'like', 'share', 'follow', 'message'],
            'search': ['search', 'filter', 'sort', 'query', 'results'],
            'mobile': ['mobile', 'app', 'swipe', 'touch', 'notification'],
            'ui_ux': ['click', 'button', 'form', 'page', 'navigate', 'interface']
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in story_lower for keyword in keywords):
                return domain
        
        return 'general'
    
    def _extract_keywords(self, story: str) -> List[str]:
        """Extract relevant keywords from story"""
        import re
        
        # Simple keyword extraction (can be enhanced with NLP)
        words = re.findall(r'\b\w+\b', story.lower())
        
        # Filter out common stop words
        stop_words = {'i', 'want', 'to', 'so', 'that', 'as', 'a', 'an', 'the', 'and', 'or', 'but'}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Return most frequent keywords
        from collections import Counter
        return [word for word, _ in Counter(keywords).most_common(10)]
    
    def _calculate_complexity_score(self, story: str) -> float:
        """Calculate story complexity for better matching"""
        # Simple complexity scoring based on length and specific indicators
        word_count = len(story.split())
        
        complexity_indicators = ['integrate', 'multiple', 'complex', 'advanced', 'system']
        complexity_bonus = sum(1 for indicator in complexity_indicators if indicator in story.lower())
        
        return min(1.0, (word_count / 100) + (complexity_bonus * 0.2))
    
    def _calculate_relevance_score(self, query_story: str, candidate_story: str, 
                                 metadata: Dict, distance: float, query_domain: str, 
                                 query_keywords: List[str]) -> float:
        """
        Calculate comprehensive relevance score for better ranking
        """
        # Base semantic similarity (lower distance = higher similarity)
        semantic_score = max(0, 1 - distance)
        
        # Domain matching bonus
        candidate_domain = metadata.get('domain', 'general')
        domain_bonus = 0.3 if query_domain == candidate_domain else 0
        
        # Keyword overlap bonus
        candidate_keywords_str = metadata.get('keywords', '')
        candidate_keywords = candidate_keywords_str.split(',') if candidate_keywords_str else []
        keyword_overlap = len(set(query_keywords) & set(candidate_keywords))
        keyword_bonus = min(0.2, keyword_overlap * 0.05)
        
        # Quality bonus from feedback
        feedback_score = metadata.get('feedback_score', 0.5)
        quality_bonus = (feedback_score - 0.5) * 0.2
        
        # Recency bonus for generated content
        recency_bonus = 0.1 if metadata.get('source') == 'generated' else 0
        
        total_score = semantic_score + domain_bonus + keyword_bonus + quality_bonus + recency_bonus
        return min(1.0, total_score)
    
    def _generate_domain_specific_edge_cases(self, domain: str, story: str) -> List[Dict]:
        """Generate domain-specific edge cases for better coverage"""
        base_cases = {
            'ecommerce': [
                {
                    "id": "edge_ecom_1",
                    "title": "Edge: Out of stock item handling",
                    "preconditions": "Product inventory is 0",
                    "steps": "Attempt to add out-of-stock item to cart",
                    "expected": "Clear out-of-stock message, no cart addition",
                    "priority": "High"
                },
                {
                    "id": "edge_ecom_2", 
                    "title": "Edge: Cart persistence across sessions",
                    "preconditions": "User has items in cart",
                    "steps": "Log out and log back in",
                    "expected": "Cart items remain preserved",
                    "priority": "Medium"
                }
            ],
            'authentication': [
                {
                    "id": "edge_auth_1",
                    "title": "Edge: Multiple failed login attempts",
                    "preconditions": "User account exists",
                    "steps": "Enter wrong password 5 times consecutively",
                    "expected": "Account temporarily locked with clear message",
                    "priority": "Critical"
                }
            ],
            'general': [
                {
                    "id": "edge_gen_1",
                    "title": "Edge: Network interruption handling",
                    "preconditions": "User performing action",
                    "steps": "Disconnect network during operation",
                    "expected": "Graceful error handling, retry mechanism",
                    "priority": "High"
                }
            ]
        }
        
        return base_cases.get(domain, base_cases['general'])
    
    def _get_fallback_cases(self) -> List[Dict]:
        """Fallback cases when retrieval fails"""
        return [
            {
                "id": "fallback_1",
                "title": "Basic functionality validation",
                "preconditions": "System is accessible",
                "steps": "Perform core user action as described in story",
                "expected": "Action completes successfully with expected outcome",
                "priority": "High"
            }
        ]
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about the learning system"""
        try:
            total_stories = self.collection.count()
            total_feedback = self.feedback_collection.count()
            
            return {
                "total_stories_learned": total_stories,
                "total_feedback_received": total_feedback,
                "embedding_model": "all-mpnet-base-v2",
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}

# Global instance
rag_helper = EnhancedRAGHelper()