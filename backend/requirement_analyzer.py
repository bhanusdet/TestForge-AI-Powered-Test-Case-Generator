# requirement_analyzer.py

from typing import List, Dict, Any, Set, Tuple, Optional
import re
import json
from dataclasses import dataclass
from enum import Enum

class RequirementType(Enum):
    FUNCTIONAL = "functional"
    UI_INTERACTION = "ui_interaction"
    BUSINESS_RULE = "business_rule"
    DATA_VALIDATION = "data_validation"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ACCEPTANCE_CRITERIA = "acceptance_criteria"
    USER_FLOW = "user_flow"

@dataclass
class ExtractedRequirement:
    """Structured representation of a requirement"""
    content: str
    type: RequirementType
    priority: str = "medium"
    testable: bool = True
    keywords: List[str] = None
    confidence_score: float = 1.0
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []

class RequirementAnalyzer:
    """
    Enhanced requirement analyzer with improved parsing and reliability
    """
    
    # Enhanced keyword patterns for better detection
    FUNCTIONAL_KEYWORDS = {
        'create': ['create', 'add', 'insert', 'generate', 'make', 'build'],
        'read': ['view', 'see', 'display', 'show', 'list', 'browse', 'search', 'find'],
        'update': ['edit', 'modify', 'change', 'update', 'alter', 'revise'],
        'delete': ['delete', 'remove', 'cancel', 'clear', 'destroy'],
        'process': ['process', 'handle', 'manage', 'execute', 'perform'],
        'validate': ['validate', 'verify', 'check', 'confirm', 'authenticate'],
        'notify': ['notify', 'alert', 'inform', 'send', 'email', 'message']
    }
    
    UI_KEYWORDS = {
        'input': ['field', 'input', 'textbox', 'textarea', 'form'],
        'action': ['button', 'link', 'click', 'tap', 'select', 'choose'],
        'display': ['page', 'screen', 'dialog', 'popup', 'modal', 'window'],
        'navigation': ['menu', 'navigate', 'go to', 'redirect', 'route'],
        'selection': ['dropdown', 'checkbox', 'radio', 'list', 'option']
    }
    
    BUSINESS_RULE_INDICATORS = [
        'must', 'should', 'shall', 'required', 'mandatory', 'only', 'if', 'when',
        'unless', 'provided that', 'cannot', 'must not', 'should not', 'forbidden'
    ]
    
    @staticmethod
    def extract_testable_requirements(user_story: str) -> Dict[str, List[ExtractedRequirement]]:
        """
        Enhanced requirement extraction with structured output
        """
        requirements = {req_type.value: [] for req_type in RequirementType}
        
        # Preprocess story
        story_sentences = RequirementAnalyzer._preprocess_story(user_story)
        
        for sentence in story_sentences:
            extracted_reqs = RequirementAnalyzer._extract_from_sentence(sentence)
            for req in extracted_reqs:
                requirements[req.type.value].append(req)
        
        # Extract structured sections (Given-When-Then, acceptance criteria)
        structured_reqs = RequirementAnalyzer._extract_structured_requirements(user_story)
        for req in structured_reqs:
            requirements[req.type.value].append(req)
        
        # Post-process: deduplicate and enhance
        for req_type in requirements.keys():
            requirements[req_type] = RequirementAnalyzer._deduplicate_requirements(
                requirements[req_type]
            )
        
        return requirements
    
    @staticmethod
    def _preprocess_story(story: str) -> List[str]:
        """
        Clean and split story into analyzable sentences
        """
        # Clean the story
        story = re.sub(r'\s+', ' ', story.strip())
        
        # Split into sentences while preserving structured sections
        sentences = []
        
        # Handle bullet points and numbered lists
        lines = story.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Split bullet points and numbered items
            if re.match(r'^[-•*]\s+', line) or re.match(r'^\d+\.\s+', line):
                sentences.append(line)
            else:
                # Split by sentence endings but be careful with abbreviations
                parts = re.split(r'(?<=[.!?])\s+(?=[A-Z])', line)
                sentences.extend([p.strip() for p in parts if p.strip()])
        
        return sentences
    
    @staticmethod
    def _extract_from_sentence(sentence: str) -> List[ExtractedRequirement]:
        """
        Extract requirements from a single sentence
        """
        requirements = []
        
        # Extract functional requirements
        functional_reqs = RequirementAnalyzer._extract_functional_requirements(sentence)
        requirements.extend(functional_reqs)
        
        # Extract UI requirements
        ui_reqs = RequirementAnalyzer._extract_ui_requirements(sentence)
        requirements.extend(ui_reqs)
        
        # Extract business rules
        business_reqs = RequirementAnalyzer._extract_business_rules(sentence)
        requirements.extend(business_reqs)
        
        # Extract data validation requirements
        data_reqs = RequirementAnalyzer._extract_data_requirements(sentence)
        requirements.extend(data_reqs)
        
        return requirements
    
    @staticmethod
    def _extract_functional_requirements(sentence: str) -> List[ExtractedRequirement]:
        """
        Extract functional requirements with improved accuracy
        """
        requirements = []
        sentence_lower = sentence.lower()
        
        # User story pattern: "As a ... I want to ... so that ..."
        user_story_pattern = r'(?:as\s+a\s+\w+[,\s]+)?I\s+want\s+to\s+(.+?)(?:\s+so\s+that|$)'
        matches = re.findall(user_story_pattern, sentence_lower, re.IGNORECASE)
        
        for match in matches:
            keywords = RequirementAnalyzer._extract_action_keywords(match)
            confidence = 0.9 if 'I want to' in sentence_lower else 0.7
            
            req = ExtractedRequirement(
                content=match.strip(),
                type=RequirementType.FUNCTIONAL,
                keywords=keywords,
                confidence_score=confidence,
                priority=RequirementAnalyzer._determine_priority(sentence)
            )
            requirements.append(req)
        
        # System behavior patterns
        system_patterns = [
            r'(?:the\s+)?system\s+(?:should|must|will|shall)\s+(.+?)(?=\.|$)',
            r'(?:application|app)\s+(?:should|must|will|shall)\s+(.+?)(?=\.|$)',
            r'(?:user|customer)\s+(?:can|should be able to)\s+(.+?)(?=\.|$)'
        ]
        
        for pattern in system_patterns:
            matches = re.findall(pattern, sentence_lower, re.IGNORECASE)
            for match in matches:
                keywords = RequirementAnalyzer._extract_action_keywords(match)
                req = ExtractedRequirement(
                    content=match.strip(),
                    type=RequirementType.FUNCTIONAL,
                    keywords=keywords,
                    confidence_score=0.8,
                    priority=RequirementAnalyzer._determine_priority(sentence)
                )
                requirements.append(req)
        
        return requirements
    
    @staticmethod
    def _extract_ui_requirements(sentence: str) -> List[ExtractedRequirement]:
        """
        Extract UI interaction requirements
        """
        requirements = []
        sentence_lower = sentence.lower()
        
        # UI interaction patterns
        ui_patterns = [
            r'(?:click|tap|press|select)\s+(?:on\s+)?(?:the\s+)?(\w+(?:\s+\w+)*?)(?:\s+(?:button|link|field|menu))?',
            r'(?:enter|input|type)\s+(.+?)\s+(?:in|into)\s+(?:the\s+)?(\w+(?:\s+\w+)*?)(?:\s+field)?',
            r'(?:navigate|go)\s+to\s+(?:the\s+)?(.+?)(?:\s+page|\s+screen|$)',
            r'(?:display|show)\s+(?:the\s+)?(.+?)(?:\s+on\s+screen|$)'
        ]
        
        for pattern in ui_patterns:
            matches = re.findall(pattern, sentence_lower)
            for match in matches:
                content = match if isinstance(match, str) else ' '.join(match)
                keywords = RequirementAnalyzer._extract_ui_keywords(content)
                
                req = ExtractedRequirement(
                    content=content.strip(),
                    type=RequirementType.UI_INTERACTION,
                    keywords=keywords,
                    confidence_score=0.8
                )
                requirements.append(req)
        
        return requirements
    
    @staticmethod
    def _extract_business_rules(sentence: str) -> List[ExtractedRequirement]:
        """
        Extract business rules and constraints
        """
        requirements = []
        sentence_lower = sentence.lower()
        
        # Business rule patterns
        rule_patterns = [
            r'(?:if|when)\s+(.+?)\s+(?:then|,)',
            r'(?:must\s+not|cannot|should\s+not)\s+(.+?)(?=\.|$)',
            r'(?:only|exclusively)\s+(.+?)(?=\.|$)',
            r'(?:provided\s+that|as\s+long\s+as)\s+(.+?)(?=\.|$)'
        ]
        
        for pattern in rule_patterns:
            matches = re.findall(pattern, sentence_lower, re.IGNORECASE | re.DOTALL)
            for match in matches:
                req = ExtractedRequirement(
                    content=match.strip(),
                    type=RequirementType.BUSINESS_RULE,
                    keywords=RequirementAnalyzer._extract_constraint_keywords(match),
                    confidence_score=0.9,
                    priority="high"
                )
                requirements.append(req)
        
        return requirements
    
    @staticmethod
    def _extract_data_requirements(sentence: str) -> List[ExtractedRequirement]:
        """
        Extract data validation and handling requirements
        """
        requirements = []
        sentence_lower = sentence.lower()
        
        # Data validation patterns
        data_patterns = [
            r'(?:validate|verify|check)\s+(.+?)(?=\.|$)',
            r'(?:format|type)\s+(?:should\s+be|must\s+be)\s+(.+?)(?=\.|$)',
            r'(?:required|mandatory|optional)\s+(.+?)(?=\.|$)'
        ]
        
        for pattern in data_patterns:
            matches = re.findall(pattern, sentence_lower, re.IGNORECASE)
            for match in matches:
                req = ExtractedRequirement(
                    content=match.strip(),
                    type=RequirementType.DATA_VALIDATION,
                    keywords=RequirementAnalyzer._extract_data_keywords(match),
                    confidence_score=0.8
                )
                requirements.append(req)
        
        return requirements
    
    @staticmethod
    def _extract_structured_requirements(story: str) -> List[ExtractedRequirement]:
        """
        Extract structured requirements (Given-When-Then, acceptance criteria)
        """
        requirements = []
        
        # Given-When-Then patterns
        gwt_pattern = r'(?:given|when|then)\s+(.+?)(?=\n|given|when|then|$)'
        matches = re.findall(gwt_pattern, story, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            req = ExtractedRequirement(
                content=match.strip(),
                type=RequirementType.ACCEPTANCE_CRITERIA,
                confidence_score=0.95,
                priority="high"
            )
            requirements.append(req)
        
        # Acceptance criteria sections
        ac_patterns = [
            r'acceptance\s+criteria:?\s*(.+?)(?=\n\n|\Z)',
            r'scenarios?:?\s*(.+?)(?=\n\n|\Z)'
        ]
        
        for pattern in ac_patterns:
            matches = re.findall(pattern, story, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Split multiple criteria
                criteria = re.split(r'\n-|\n\d+\.|\n•', match)
                for criterion in criteria:
                    if criterion.strip():
                        req = ExtractedRequirement(
                            content=criterion.strip(),
                            type=RequirementType.ACCEPTANCE_CRITERIA,
                            confidence_score=0.9,
                            priority="high"
                        )
                        requirements.append(req)
        
        return requirements
    
    @staticmethod
    def _extract_action_keywords(text: str) -> List[str]:
        """
        Extract action keywords from text
        """
        keywords = []
        text_lower = text.lower()
        
        for action_type, words in RequirementAnalyzer.FUNCTIONAL_KEYWORDS.items():
            for word in words:
                if word in text_lower:
                    keywords.append(word)
        
        return list(set(keywords))
    
    @staticmethod
    def _extract_ui_keywords(text: str) -> List[str]:
        """
        Extract UI-related keywords from text
        """
        keywords = []
        text_lower = text.lower()
        
        for ui_type, words in RequirementAnalyzer.UI_KEYWORDS.items():
            for word in words:
                if word in text_lower:
                    keywords.append(word)
        
        return list(set(keywords))
    
    @staticmethod
    def _extract_constraint_keywords(text: str) -> List[str]:
        """
        Extract business rule constraint keywords
        """
        keywords = []
        text_lower = text.lower()
        
        for indicator in RequirementAnalyzer.BUSINESS_RULE_INDICATORS:
            if indicator in text_lower:
                keywords.append(indicator)
        
        return keywords
    
    @staticmethod
    def _extract_data_keywords(text: str) -> List[str]:
        """
        Extract data validation keywords
        """
        data_keywords = ['email', 'phone', 'number', 'date', 'time', 'url', 'password',
                        'required', 'optional', 'format', 'length', 'range']
        keywords = []
        text_lower = text.lower()
        
        for keyword in data_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        return keywords
    
    @staticmethod
    def _determine_priority(sentence: str) -> str:
        """
        Determine requirement priority based on language used
        """
        sentence_lower = sentence.lower()
        
        high_priority_indicators = ['must', 'critical', 'essential', 'required', 'shall']
        medium_priority_indicators = ['should', 'important', 'recommended']
        low_priority_indicators = ['could', 'nice to have', 'optional', 'may']
        
        if any(indicator in sentence_lower for indicator in high_priority_indicators):
            return "high"
        elif any(indicator in sentence_lower for indicator in medium_priority_indicators):
            return "medium"
        elif any(indicator in sentence_lower for indicator in low_priority_indicators):
            return "low"
        
        return "medium"
    
    @staticmethod
    def _deduplicate_requirements(requirements: List[ExtractedRequirement]) -> List[ExtractedRequirement]:
        """
        Remove duplicate requirements and merge similar ones
        """
        if not requirements:
            return []
        
        unique_requirements = []
        seen_content = set()
        
        for req in requirements:
            # Simple deduplication by content similarity
            content_normalized = re.sub(r'\s+', ' ', req.content.lower().strip())
            
            # Check if we've seen similar content
            is_duplicate = False
            for seen in seen_content:
                if RequirementAnalyzer._similarity_score(content_normalized, seen) > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen_content.add(content_normalized)
                unique_requirements.append(req)
        
        # Sort by confidence score and priority
        priority_order = {"high": 3, "medium": 2, "low": 1}
        unique_requirements.sort(
            key=lambda x: (priority_order.get(x.priority, 2), x.confidence_score),
            reverse=True
        )
        
        return unique_requirements
    
    @staticmethod
    def _similarity_score(text1: str, text2: str) -> float:
        """
        Calculate similarity score between two texts
        """
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    @staticmethod
    def analyze_test_coverage(test_cases: List[Dict], user_story: str) -> Dict[str, Any]:
        """
        Enhanced test coverage analysis with detailed requirement mapping
        """
        requirements = RequirementAnalyzer.extract_testable_requirements(user_story)
        
        # Flatten requirements for easier analysis
        all_requirements = []
        for req_type, reqs in requirements.items():
            for req in reqs:
                all_requirements.append({
                    'content': req.content,
                    'type': req.type.value,
                    'priority': req.priority,
                    'keywords': req.keywords,
                    'confidence': req.confidence_score,
                    'covered_by': []
                })
        
        coverage_analysis = {
            'total_requirements': len(all_requirements),
            'covered_requirements': 0,
            'coverage_percentage': 0.0,
            'coverage_by_type': {},
            'coverage_by_priority': {},
            'uncovered_requirements': [],
            'scope_violations': [],
            'test_case_analysis': [],
            'quality_score': 0.0,
            'recommendations': []
        }
        
        # Initialize coverage by type and priority
        for req_type in RequirementType:
            coverage_analysis['coverage_by_type'][req_type.value] = {
                'total': 0, 'covered': 0, 'percentage': 0.0
            }
        
        for priority in ['high', 'medium', 'low']:
            coverage_analysis['coverage_by_priority'][priority] = {
                'total': 0, 'covered': 0, 'percentage': 0.0
            }
        
        # Count requirements by type and priority
        for req in all_requirements:
            coverage_analysis['coverage_by_type'][req['type']]['total'] += 1
            coverage_analysis['coverage_by_priority'][req['priority']]['total'] += 1
        
        # Analyze each test case
        for test_case in test_cases:
            test_analysis = RequirementAnalyzer._analyze_single_test_case_enhanced(
                test_case, all_requirements, user_story
            )
            coverage_analysis['test_case_analysis'].append(test_analysis)
            
            # Update requirement coverage
            for req_idx in test_analysis['mapped_requirements']:
                if req_idx < len(all_requirements):
                    all_requirements[req_idx]['covered_by'].append(test_case.get('id', 'Unknown'))
        
        # Calculate coverage metrics
        covered_requirements = [req for req in all_requirements if req['covered_by']]
        coverage_analysis['covered_requirements'] = len(covered_requirements)
        
        if coverage_analysis['total_requirements'] > 0:
            coverage_analysis['coverage_percentage'] = (
                len(covered_requirements) / coverage_analysis['total_requirements']
            ) * 100
        
        # Calculate coverage by type and priority
        for req in covered_requirements:
            coverage_analysis['coverage_by_type'][req['type']]['covered'] += 1
            coverage_analysis['coverage_by_priority'][req['priority']]['covered'] += 1
        
        for req_type_data in coverage_analysis['coverage_by_type'].values():
            if req_type_data['total'] > 0:
                req_type_data['percentage'] = (req_type_data['covered'] / req_type_data['total']) * 100
        
        for priority_data in coverage_analysis['coverage_by_priority'].values():
            if priority_data['total'] > 0:
                priority_data['percentage'] = (priority_data['covered'] / priority_data['total']) * 100
        
        # Identify uncovered requirements
        coverage_analysis['uncovered_requirements'] = [
            {
                'content': req['content'],
                'type': req['type'],
                'priority': req['priority'],
                'confidence': req['confidence']
            }
            for req in all_requirements if not req['covered_by']
        ]
        
        # Calculate quality score
        coverage_analysis['quality_score'] = RequirementAnalyzer._calculate_quality_score(
            coverage_analysis, test_cases
        )
        
        # Generate recommendations
        coverage_analysis['recommendations'] = RequirementAnalyzer._generate_recommendations(
            coverage_analysis, all_requirements
        )
        
        return coverage_analysis
    
    @staticmethod
    def _analyze_single_test_case_enhanced(test_case: Dict, requirements: List[Dict], user_story: str) -> Dict:
        """
        Enhanced single test case analysis with better requirement mapping
        """
        test_content = f"{test_case.get('title', '')} {test_case.get('steps', '')} {test_case.get('expected', '')}".lower()
        story_lower = user_story.lower()
        
        analysis = {
            'test_id': test_case.get('id', 'Unknown'),
            'title': test_case.get('title', 'Unknown'),
            'mapped_requirements': [],
            'requirement_types': [],
            'coverage_score': 0.0,
            'scope_issues': [],
            'quality_issues': []
        }
        
        # Advanced requirement mapping
        for idx, req in enumerate(requirements):
            mapping_score = RequirementAnalyzer._calculate_requirement_mapping_score(
                test_content, req
            )
            
            if mapping_score > 0.3:  # Threshold for considering a match
                analysis['mapped_requirements'].append(idx)
                analysis['requirement_types'].append(req['type'])
                analysis['coverage_score'] = max(analysis['coverage_score'], mapping_score)
        
        # Enhanced scope violation detection
        scope_violations = RequirementAnalyzer._detect_scope_violations(test_content, story_lower)
        analysis['scope_issues'] = scope_violations
        
        # Quality issue detection
        quality_issues = RequirementAnalyzer._detect_quality_issues(test_case)
        analysis['quality_issues'] = quality_issues
        
        return analysis
    
    @staticmethod
    def _calculate_requirement_mapping_score(test_content: str, requirement: Dict) -> float:
        """
        Calculate how well a test case maps to a requirement
        """
        req_content = requirement['content'].lower()
        req_keywords = [kw.lower() for kw in requirement['keywords']]
        
        score = 0.0
        
        # Direct content overlap
        req_words = set(req_content.split())
        test_words = set(test_content.split())
        
        if req_words and test_words:
            overlap = req_words.intersection(test_words)
            content_score = len(overlap) / len(req_words.union(test_words))
            score += content_score * 0.6
        
        # Keyword matching
        keyword_matches = sum(1 for kw in req_keywords if kw in test_content)
        if req_keywords:
            keyword_score = keyword_matches / len(req_keywords)
            score += keyword_score * 0.4
        
        # Boost score based on requirement confidence
        score *= requirement.get('confidence', 1.0)
        
        return min(score, 1.0)
    
    @staticmethod
    def _detect_scope_violations(test_content: str, story_content: str) -> List[str]:
        """
        Enhanced scope violation detection
        """
        violations = []
        
        # Common scope violations
        violation_categories = {
            'admin_functions': ['admin', 'administrator', 'manage users', 'system config'],
            'external_integrations': ['api', 'third party', 'external system', 'integration'],
            'infrastructure': ['database', 'server', 'deployment', 'backup', 'restore'],
            'advanced_features': ['reporting', 'analytics', 'export', 'import', 'bulk operations']
        }
        
        for category, keywords in violation_categories.items():
            for keyword in keywords:
                if keyword in test_content and keyword not in story_content:
                    violations.append(f"Tests {category.replace('_', ' ')}: '{keyword}' not mentioned in story")
        
        return violations
    
    @staticmethod
    def _detect_quality_issues(test_case: Dict) -> List[str]:
        """
        Detect quality issues in test cases
        """
        issues = []
        
        title = test_case.get('title', '')
        steps = test_case.get('steps', '')
        expected = test_case.get('expected', '')
        
        # Check for missing or vague content
        if not title.strip():
            issues.append("Missing test case title")
        elif len(title) < 10:
            issues.append("Test title too short or vague")
        
        if not steps.strip():
            issues.append("Missing test steps")
        elif len(steps.split()) < 5:
            issues.append("Test steps too brief")
        
        if not expected.strip():
            issues.append("Missing expected result")
        elif len(expected.split()) < 3:
            issues.append("Expected result too vague")
        
        # Check for action words in steps
        action_words = ['click', 'enter', 'select', 'navigate', 'verify', 'check', 'confirm']
        if not any(word in steps.lower() for word in action_words):
            issues.append("Test steps lack clear actions")
        
        return issues
    
    @staticmethod
    def _calculate_quality_score(coverage_analysis: Dict, test_cases: List[Dict]) -> float:
        """
        Calculate overall quality score for the test suite
        """
        if not test_cases:
            return 0.0
            
        score = 0.0
        
        # Coverage component (40%)
        coverage_score = coverage_analysis['coverage_percentage'] / 100
        score += coverage_score * 0.4
        
        # Priority coverage component (30%)
        high_priority_coverage = coverage_analysis['coverage_by_priority'].get('high', {}).get('percentage', 0) / 100
        score += high_priority_coverage * 0.3
        
        # Test case quality component (20%)
        total_quality_issues = sum(
            len(tc['quality_issues']) for tc in coverage_analysis['test_case_analysis']
        )
        quality_score = max(0, 1 - (total_quality_issues / len(test_cases) / 5))  # Normalize
        score += quality_score * 0.2
        
        # Scope adherence component (10%)
        total_scope_violations = sum(
            len(tc['scope_issues']) for tc in coverage_analysis['test_case_analysis']
        )
        scope_score = max(0, 1 - (total_scope_violations / len(test_cases) / 3))  # Normalize
        score += scope_score * 0.1
        
        return round(score, 3)
    
    @staticmethod
    def _generate_recommendations(coverage_analysis: Dict, requirements: List[Dict]) -> List[str]:
        """
        Generate actionable recommendations based on analysis
        """
        recommendations = []
        
        # Coverage recommendations
        if coverage_analysis['coverage_percentage'] < 70:
            recommendations.append("Low coverage detected. Add more test cases to cover missing requirements.")
        
        # Priority-based recommendations
        high_priority_coverage = coverage_analysis['coverage_by_priority'].get('high', {}).get('percentage', 0)
        if high_priority_coverage < 90:
            recommendations.append("High priority requirements not fully covered. Focus on critical functionality.")
        
        # Type-based recommendations
        for req_type, data in coverage_analysis['coverage_by_type'].items():
            if data['total'] > 0 and data['percentage'] < 60:
                recommendations.append(f"Poor coverage for {req_type.replace('_', ' ')} requirements.")
        
        # Quality recommendations
        if coverage_analysis['quality_score'] < 0.7:
            recommendations.append("Test case quality needs improvement. Add more detailed steps and clear expected results.")
        
        return recommendations
    
    @staticmethod
    def generate_coverage_report(test_cases: List[Dict], user_story: str) -> str:
        """
        Generate comprehensive coverage report
        """
        analysis = RequirementAnalyzer.analyze_test_coverage(test_cases, user_story)
        
        # Build report with safe string concatenation
        report = "Enhanced Test Coverage Analysis Report\n"
        report += "========================================\n\n"
        report += f"Overall Quality Score: {analysis['quality_score']:.1%}\n"
        report += f"Overall Coverage: {analysis['coverage_percentage']:.1f}%\n"
        report += f"Total Requirements Identified: {analysis['total_requirements']}\n"
        report += f"Test Cases Generated: {len(test_cases)}\n\n"
        report += "Coverage by Requirement Type:\n"
        
        for req_type, data in analysis['coverage_by_type'].items():
            if data['total'] > 0:
                status = "GOOD" if data['percentage'] >= 80 else "FAIR" if data['percentage'] >= 60 else "POOR"
                report += f"  {status}: {req_type.replace('_', ' ').title()}: {data['covered']}/{data['total']} ({data['percentage']:.1f}%)\n"
        
        report += "\nCoverage by Priority:\n"
        for priority, data in analysis['coverage_by_priority'].items():
            if data['total'] > 0:
                status = "GOOD" if data['percentage'] >= 90 else "FAIR" if data['percentage'] >= 70 else "POOR"
                report += f"  {status}: {priority.title()}: {data['covered']}/{data['total']} ({data['percentage']:.1f}%)\n"
        
        report += "\nTest Case Analysis:\n"
        for test_analysis in analysis['test_case_analysis']:
            req_count = len(test_analysis['mapped_requirements'])
            status = "GOOD" if req_count > 0 else "POOR"
            report += f"  {status}: {test_analysis['title']} (Maps to {req_count} requirements)\n"
            
            if test_analysis['scope_issues']:
                report += f"    Scope Issues: {'; '.join(test_analysis['scope_issues'])}\n"
            
            if test_analysis['quality_issues']:
                report += f"    Quality Issues: {'; '.join(test_analysis['quality_issues'])}\n"
        
        if analysis['uncovered_requirements']:
            report += f"\nUncovered Requirements ({len(analysis['uncovered_requirements'])}):\n"
            for req in analysis['uncovered_requirements'][:5]:  # Show top 5
                report += f"  - {req['content']} ({req['type']}, {req['priority']} priority)\n"
            
            if len(analysis['uncovered_requirements']) > 5:
                report += f"  ... and {len(analysis['uncovered_requirements']) - 5} more\n"
        
        report += "\nRecommendations:\n"
        for rec in analysis['recommendations']:
            report += f"  - {rec}\n"
        
        return report