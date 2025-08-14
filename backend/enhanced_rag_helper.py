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
                    user_feedback: str = "", improved_testcases: List[Dict] = None,
                    feedback_categories: List[str] = None, missing_scenarios: List[str] = None):
        """
        Enhanced feedback processing for better learning
        """
        try:
            # 🎯 UPDATE ORIGINAL STORY QUALITY SCORE
            self._update_story_quality_score(story_id, testcase_quality_score)
            
            # 📊 ANALYZE FEEDBACK CATEGORIES
            analyzed_feedback = self._analyze_feedback_sentiment(user_feedback)
            
            feedback_data = {
                "story_id": story_id,
                "quality_score": testcase_quality_score,
                "user_feedback": user_feedback,
                "improved_testcases": json.dumps(improved_testcases or []),
                "feedback_categories": json.dumps(feedback_categories or []),
                "missing_scenarios": json.dumps(missing_scenarios or []),
                "feedback_date": datetime.now().isoformat(),
                "sentiment_analysis": json.dumps(analyzed_feedback),
                "feedback_weight": self._calculate_feedback_weight(testcase_quality_score, user_feedback)
            }
            
            # 🧠 CREATE RICHER EMBEDDING FROM COMPREHENSIVE FEEDBACK
            feedback_text = self._create_enriched_feedback_text(
                user_feedback, testcase_quality_score, feedback_categories, missing_scenarios
            )
            embedding = self.model.encode(feedback_text).tolist()
            
            # 💾 STORE IN FEEDBACK COLLECTION
            self.feedback_collection.add(
                documents=[feedback_text],
                embeddings=[embedding],
                metadatas=[feedback_data],
                ids=[f"feedback_{story_id}_{datetime.now().timestamp()}"]
            )
            
            # 🔄 IF HIGH-QUALITY IMPROVED TEST CASES PROVIDED, ADD AS NEW EXAMPLES
            if improved_testcases and testcase_quality_score >= 4.0:
                self._add_improved_examples_to_knowledge_base(story_id, improved_testcases)
            
            # 📈 UPDATE DOMAIN-SPECIFIC QUALITY METRICS
            self._update_domain_quality_metrics(story_id, testcase_quality_score, feedback_categories)
            
            logger.info(f"✅ Enhanced feedback processed for story: {story_id} (Score: {testcase_quality_score})")
            
        except Exception as e:
            logger.error(f"Failed to add enhanced feedback: {e}")
    
    def _update_story_quality_score(self, story_id: str, new_score: float):
        """Update the quality score of the original story in the main collection"""
        try:
            # Get the original story
            results = self.collection.get(
                where={"story_id": story_id}
            )
            
            if results and results['documents']:
                # Update metadata with new feedback score
                for i, id in enumerate(results['ids']):
                    current_metadata = results['metadatas'][i]
                    
                    # Calculate weighted average if previous scores exist
                    current_score = current_metadata.get('feedback_score', 3.0)
                    feedback_count = current_metadata.get('feedback_count', 0)
                    
                    # Weighted average with recency bias
                    updated_score = (current_score * feedback_count + new_score * 1.2) / (feedback_count + 1.2)
                    
                    # Update metadata
                    updated_metadata = {**current_metadata}
                    updated_metadata['feedback_score'] = round(updated_score, 2)
                    updated_metadata['feedback_count'] = feedback_count + 1
                    updated_metadata['last_feedback'] = datetime.now().isoformat()
                    
                    # Update in collection
                    self.collection.update(
                        ids=[id],
                        metadatas=[updated_metadata]
                    )
                    
                logger.info(f"📊 Updated story quality score: {story_id} -> {updated_score:.2f}")
                
        except Exception as e:
            logger.error(f"Failed to update story quality score: {e}")
    
    def _analyze_feedback_sentiment(self, feedback_text: str) -> Dict:
        """Analyze feedback sentiment and extract key insights"""
        if not feedback_text:
            return {"sentiment": "neutral", "key_issues": [], "suggestions": []}
        
        feedback_lower = feedback_text.lower()
        
        # 🎯 IDENTIFY COMMON FEEDBACK PATTERNS
        quality_indicators = {
            "positive": ["good", "great", "excellent", "comprehensive", "thorough", "detailed"],
            "negative": ["poor", "bad", "incomplete", "missing", "lacking", "insufficient"],
            "suggestions": ["should", "could", "need", "add", "include", "consider", "improve"]
        }
        
        sentiment_score = 0
        key_issues = []
        suggestions = []
        
        for word in feedback_lower.split():
            if word in quality_indicators["positive"]:
                sentiment_score += 1
            elif word in quality_indicators["negative"]:
                sentiment_score -= 1
                key_issues.append(word)
            elif word in quality_indicators["suggestions"]:
                suggestions.append(word)
        
        sentiment = "positive" if sentiment_score > 0 else "negative" if sentiment_score < 0 else "neutral"
        
        return {
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "key_issues": key_issues,
            "suggestions": suggestions,
            "feedback_length": len(feedback_text)
        }
    
    def _calculate_feedback_weight(self, quality_score: float, feedback_text: str) -> float:
        """Calculate how much weight to give this feedback"""
        base_weight = 1.0
        
        # 📏 MORE DETAILED FEEDBACK GETS MORE WEIGHT
        if len(feedback_text) > 50:
            base_weight += 0.3
        elif len(feedback_text) > 20:
            base_weight += 0.1
        
        # 🎯 EXTREME SCORES (VERY GOOD OR VERY BAD) GET MORE WEIGHT
        if quality_score <= 2.0 or quality_score >= 4.5:
            base_weight += 0.2
        
        return min(2.0, base_weight)  # Cap at 2.0
    
    def _create_enriched_feedback_text(self, feedback_text: str, quality_score: float, 
                                     categories: List[str], missing_scenarios: List[str]) -> str:
        """Create enriched text for better embedding"""
        parts = [f"Quality: {quality_score}/5"]
        
        if feedback_text:
            parts.append(f"Feedback: {feedback_text}")
        
        if categories:
            parts.append(f"Categories: {', '.join(categories)}")
        
        if missing_scenarios:
            parts.append(f"Missing: {', '.join(missing_scenarios)}")
        
        return " | ".join(parts)
    
    def _add_improved_examples_to_knowledge_base(self, original_story_id: str, improved_testcases: List[Dict]):
        """Add user-improved test cases as high-quality examples"""
        try:
            # Get the original story
            results = self.collection.get(where={"story_id": original_story_id})
            
            if results and results['documents']:
                original_story = results['documents'][0]
                original_metadata = results['metadatas'][0]
                
                # Create new entry with improved test cases
                improved_metadata = {**original_metadata}
                improved_metadata.update({
                    "testCases": json.dumps(improved_testcases),
                    "source": "user_improved",
                    "feedback_score": 5.0,  # User-improved examples are high quality
                    "original_story_id": original_story_id,
                    "improvement_date": datetime.now().isoformat()
                })
                
                embedding = self.model.encode(original_story).tolist()
                
                self.collection.add(
                    documents=[original_story],
                    embeddings=[embedding],
                    metadatas=[improved_metadata],
                    ids=[f"improved_{original_story_id}_{datetime.now().timestamp()}"]
                )
                
                logger.info(f"📚 Added user-improved examples for story: {original_story_id}")
                
        except Exception as e:
            logger.error(f"Failed to add improved examples: {e}")
    
    def _update_domain_quality_metrics(self, story_id: str, quality_score: float, categories: List[str]):
        """Track quality metrics per domain for insights"""
        try:
            # This could be expanded to track domain-specific quality trends
            # For now, we'll log it for future analytics
            logger.info(f"📊 Domain quality update: {story_id} -> Score: {quality_score}, Categories: {categories}")
        except Exception as e:
            logger.error(f"Failed to update domain quality metrics: {e}")
    
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
        🚀 ENHANCED relevance scoring with improved feedback integration
        """
        # 🎯 Base semantic similarity (35% weight - reduced to make room for quality)
        semantic_score = max(0, 1 - distance) * 0.35
        
        # 🏢 Domain matching bonus (25% weight)
        candidate_domain = metadata.get('domain', 'general')
        domain_score = 0.25 if query_domain == candidate_domain else 0.05
        
        # 🔤 Keyword overlap bonus (15% weight)
        candidate_keywords_str = metadata.get('keywords', '')
        candidate_keywords = candidate_keywords_str.split(',') if candidate_keywords_str else []
        keyword_overlap = len(set(query_keywords) & set(candidate_keywords))
        keyword_score = min(0.15, keyword_overlap * 0.03)
        
        # 🌟 ENHANCED Quality scoring from feedback (20% weight - INCREASED!)
        feedback_score = metadata.get('feedback_score', 3.0)  # Default to 3.0 instead of 0.5
        feedback_count = metadata.get('feedback_count', 0)
        
        # Quality bonus with confidence factor
        if feedback_count >= 3:  # High confidence
            quality_score = ((feedback_score - 3.0) / 2.0) * 0.20  # -0.20 to +0.20
        elif feedback_count >= 1:  # Medium confidence
            quality_score = ((feedback_score - 3.0) / 2.0) * 0.15  # -0.15 to +0.15
        else:  # Low confidence - use default
            quality_score = 0.05
        
        # 📈 User-improved examples get priority boost
        if metadata.get('source') == 'user_improved':
            quality_score += 0.10
        
        # ⏰ Recency bonus (5% weight)
        source = metadata.get('source', 'sample')
        if source == 'generated':
            recency_score = 0.05
        elif source == 'user_improved':
            recency_score = 0.03  # Slightly less than generated but still recent
        else:
            recency_score = 0.01
        
        # 🎯 Calculate total score
        total_score = semantic_score + domain_score + keyword_score + quality_score + recency_score
        
        # 🚀 Apply additional boosts for exceptional cases
        if feedback_score >= 4.5 and feedback_count >= 2:
            total_score *= 1.1  # 10% boost for consistently high-rated examples
        elif feedback_score <= 2.0 and feedback_count >= 2:
            total_score *= 0.8  # 20% penalty for consistently low-rated examples
        
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
        """🚀 Enhanced learning statistics with detailed insights"""
        try:
            total_stories = self.collection.count()
            total_feedback = self.feedback_collection.count()
            
            # 📊 Get feedback quality distribution
            feedback_quality_dist = self._get_feedback_quality_distribution()
            
            # 🎯 Get domain performance
            domain_stats = self._get_domain_performance_stats()
            
            # 📈 Get improvement trends
            improvement_trends = self._get_improvement_trends()
            
            return {
                "total_stories_learned": total_stories,
                "total_feedback_received": total_feedback,
                "embedding_model": "all-mpnet-base-v2",
                "last_updated": datetime.now().isoformat(),
                "feedback_quality_distribution": feedback_quality_dist,
                "domain_performance": domain_stats,
                "improvement_trends": improvement_trends,
                "system_health": {
                    "status": "active" if total_feedback > 0 else "waiting_for_feedback",
                    "learning_effectiveness": self._calculate_learning_effectiveness(),
                    "data_quality_score": self._calculate_data_quality_score()
                }
            }
        except Exception as e:
            logger.error(f"Error getting enhanced stats: {e}")
            return {"error": str(e)}
    
    def _get_feedback_quality_distribution(self) -> Dict:
        """Get distribution of feedback quality scores"""
        try:
            feedback_results = self.feedback_collection.get()
            
            if not feedback_results['metadatas']:
                return {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
            
            distribution = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
            
            for metadata in feedback_results['metadatas']:
                score = str(int(float(metadata.get('quality_score', 3))))
                if score in distribution:
                    distribution[score] += 1
            
            return distribution
        except Exception as e:
            logger.error(f"Error getting quality distribution: {e}")
            return {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    
    def _get_domain_performance_stats(self) -> Dict:
        """Get performance statistics by domain"""
        try:
            story_results = self.collection.get()
            
            if not story_results['metadatas']:
                return {}
            
            domain_stats = {}
            
            for metadata in story_results['metadatas']:
                domain = metadata.get('domain', 'general')
                feedback_score = metadata.get('feedback_score', 3.0)
                feedback_count = metadata.get('feedback_count', 0)
                
                if domain not in domain_stats:
                    domain_stats[domain] = {
                        "story_count": 0,
                        "avg_quality": 0,
                        "total_feedback": 0
                    }
                
                domain_stats[domain]["story_count"] += 1
                domain_stats[domain]["total_feedback"] += feedback_count
                
                # Calculate weighted average
                current_avg = domain_stats[domain]["avg_quality"]
                story_count = domain_stats[domain]["story_count"]
                domain_stats[domain]["avg_quality"] = (current_avg * (story_count - 1) + feedback_score) / story_count
            
            return domain_stats
        except Exception as e:
            logger.error(f"Error getting domain stats: {e}")
            return {}
    
    def _get_improvement_trends(self) -> Dict:
        """Analyze improvement trends over time"""
        try:
            feedback_results = self.feedback_collection.get()
            
            if not feedback_results['metadatas']:
                return {"trend": "insufficient_data", "recent_avg": 3.0, "older_avg": 3.0}
            
            # Sort feedback by date
            feedback_with_dates = []
            for i, metadata in enumerate(feedback_results['metadatas']):
                try:
                    date_str = metadata.get('feedback_date', datetime.now().isoformat())
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    quality_score = float(metadata.get('quality_score', 3.0))
                    feedback_with_dates.append((date_obj, quality_score))
                except:
                    continue
            
            if len(feedback_with_dates) < 2:
                return {"trend": "insufficient_data", "recent_avg": 3.0, "older_avg": 3.0}
            
            feedback_with_dates.sort(key=lambda x: x[0])
            
            # Split into older and recent halves
            mid_point = len(feedback_with_dates) // 2
            older_scores = [score for _, score in feedback_with_dates[:mid_point]]
            recent_scores = [score for _, score in feedback_with_dates[mid_point:]]
            
            older_avg = sum(older_scores) / len(older_scores) if older_scores else 3.0
            recent_avg = sum(recent_scores) / len(recent_scores) if recent_scores else 3.0
            
            trend = "improving" if recent_avg > older_avg + 0.1 else "declining" if recent_avg < older_avg - 0.1 else "stable"
            
            return {
                "trend": trend,
                "recent_avg": round(recent_avg, 2),
                "older_avg": round(older_avg, 2),
                "improvement_rate": round(recent_avg - older_avg, 2)
            }
        except Exception as e:
            logger.error(f"Error getting improvement trends: {e}")
            return {"trend": "error", "recent_avg": 3.0, "older_avg": 3.0}
    
    def _calculate_learning_effectiveness(self) -> float:
        """Calculate how effectively the system is learning"""
        try:
            story_results = self.collection.get()
            
            if not story_results['metadatas']:
                return 0.5
            
            high_quality_stories = sum(1 for metadata in story_results['metadatas'] 
                                     if metadata.get('feedback_score', 3.0) >= 4.0)
            total_stories = len(story_results['metadatas'])
            
            return round(high_quality_stories / total_stories if total_stories > 0 else 0.5, 2)
        except:
            return 0.5
    
    def _calculate_data_quality_score(self) -> float:
        """Calculate overall data quality score"""
        try:
            feedback_count = self.feedback_collection.count()
            story_count = self.collection.count()
            
            # Data quality based on feedback coverage
            feedback_coverage = min(1.0, feedback_count / max(story_count, 1))
            
            return round(feedback_coverage, 2)
        except:
            return 0.0

# Global instance
rag_helper = EnhancedRAGHelper()