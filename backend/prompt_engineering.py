# prompt_engineering.py

from typing import List, Dict, Any
from datetime import datetime

class AdvancedPromptEngineer:
    """
    Advanced prompt engineering for more accurate test case generation
    """
    
    @staticmethod
    def build_enhanced_prompt(story: str, similar_examples: List[Dict], 
                            story_context: Dict = None) -> str:
        """
        Build an enhanced prompt with better structure and context
        """
        
        # Analyze story characteristics
        story_analysis = AdvancedPromptEngineer._analyze_story(story)
        
        # Build context section
        context_section = AdvancedPromptEngineer._build_context_section(
            story_analysis, story_context
        )
        
        # Build examples section with relevance scores
        examples_section = AdvancedPromptEngineer._build_examples_section(
            similar_examples, story_analysis
        )
        
        # Build requirements section
        requirements_section = AdvancedPromptEngineer._build_requirements_section(
            story_analysis
        )
        
        prompt = f"""
{context_section}

{requirements_section}

## USER STORY TO ANALYZE:
{story}

{examples_section}

## GENERATION INSTRUCTIONS:

### Quality Standards:
1. **Precision**: Each test case must be directly related to the user story
2. **Completeness**: Cover all acceptance criteria and edge cases
3. **Clarity**: Use clear, actionable language that any QA tester can follow
4. **Coverage**: Include positive, negative, boundary, and edge test scenarios
5. **Traceability**: Each test case should map back to specific story requirements

### Test Case Categories to Include:
- **Happy Path**: Normal user flow scenarios
- **Error Handling**: Invalid inputs, system errors, network issues
- **Boundary Testing**: Min/max values, limits, edge conditions  
- **Security**: Authentication, authorization, data validation
- **Performance**: Response times, load handling (if applicable)
- **Usability**: User experience, accessibility considerations

### Specific Focus Areas Based on Story Analysis:
{AdvancedPromptEngineer._get_focus_areas(story_analysis)}

### Output Format (STRICT):
For each test case, use EXACTLY this format:

**Test Case ID:** TC_{story_analysis['domain'].upper()}_{'{:03d}'.format(1)}
**Title:** [Clear, descriptive title]
**Preconditions:** [What must be true before testing]
**Test Steps:**
1. [First action step]
2. [Second action step]
3. [Continue as needed]
**Expected Result:** [Specific, measurable expected outcome]
**Priority:** [Critical/High/Medium/Low based on story importance]
**Category:** [Positive/Negative/Edge/Boundary/Security/Performance]

Remember: Generate comprehensive test cases that ensure the user story is thoroughly validated.
"""
        
        return prompt
    
    @staticmethod
    def _analyze_story(story: str) -> Dict[str, Any]:
        """Analyze story to extract key characteristics"""
        story_lower = story.lower()
        
        # Detect story type and domain
        domain = AdvancedPromptEngineer._detect_domain(story_lower)
        complexity = AdvancedPromptEngineer._assess_complexity(story)
        user_types = AdvancedPromptEngineer._extract_user_types(story)
        actions = AdvancedPromptEngineer._extract_actions(story_lower)
        
        return {
            'domain': domain,
            'complexity': complexity,
            'user_types': user_types,
            'actions': actions,
            'word_count': len(story.split()),
            'has_acceptance_criteria': 'acceptance criteria' in story_lower,
            'has_technical_terms': any(term in story_lower for term in 
                                     ['api', 'database', 'integration', 'authentication'])
        }
    
    @staticmethod
    def _detect_domain(story_lower: str) -> str:
        """Detect the primary domain of the story"""
        domains = {
            'ecommerce': ['shop', 'cart', 'product', 'order', 'purchase', 'inventory', 'checkout'],
            'authentication': ['login', 'password', 'user account', 'register', 'authenticate'],
            'finance': ['payment', 'billing', 'transaction', 'money', 'credit', 'invoice'],
            'social': ['post', 'comment', 'like', 'share', 'follow', 'friend'],
            'search': ['search', 'filter', 'sort', 'query', 'results', 'find'],
            'content': ['create', 'edit', 'delete', 'update', 'content', 'document'],
            'mobile': ['mobile', 'app', 'swipe', 'touch', 'notification', 'push'],
            'web': ['click', 'navigate', 'page', 'button', 'form', 'website']
        }
        
        for domain, keywords in domains.items():
            if sum(1 for keyword in keywords if keyword in story_lower) >= 2:
                return domain
        
        return 'general'
    
    @staticmethod
    def _assess_complexity(story: str) -> str:
        """Assess the complexity level of the story"""
        complexity_indicators = {
            'high': ['integrate', 'multiple systems', 'complex', 'advanced', 'workflow'],
            'medium': ['process', 'manage', 'configure', 'multiple'],
            'low': ['view', 'see', 'display', 'show', 'read']
        }
        
        story_lower = story.lower()
        for level, indicators in complexity_indicators.items():
            if any(indicator in story_lower for indicator in indicators):
                return level
        
        return 'medium'
    
    @staticmethod
    def _extract_user_types(story: str) -> List[str]:
        """Extract user types/roles from the story"""
        import re
        
        # Look for "As a [role]" patterns
        role_pattern = r'as a[n]?\s+([^,]+?)(?:\s*,|\s+I\s+want|\s*$)'
        matches = re.findall(role_pattern, story, re.IGNORECASE)
        
        user_types = [match.strip() for match in matches]
        
        # Add common role detection
        common_roles = ['admin', 'user', 'customer', 'manager', 'guest']
        for role in common_roles:
            if role in story.lower() and role not in user_types:
                user_types.append(role)
        
        return user_types or ['user']
    
    @staticmethod
    def _extract_actions(story_lower: str) -> List[str]:
        """Extract key actions from the story"""
        action_words = ['create', 'read', 'update', 'delete', 'add', 'remove', 
                       'edit', 'view', 'search', 'filter', 'sort', 'manage']
        
        return [action for action in action_words if action in story_lower]
    
    @staticmethod
    def _build_context_section(story_analysis: Dict, story_context: Dict = None) -> str:
        """Build the context section of the prompt"""
        context = f"""
## CONTEXT & ANALYSIS

### Story Analysis:
- **Domain**: {story_analysis['domain'].title()}
- **Complexity**: {story_analysis['complexity'].title()}
- **User Types**: {', '.join(story_analysis['user_types'])}
- **Key Actions**: {', '.join(story_analysis['actions']) if story_analysis['actions'] else 'General functionality'}
- **Technical Story**: {'Yes' if story_analysis['has_technical_terms'] else 'No'}

### Testing Context:
You are an expert QA analyst creating manual test cases for a {story_analysis['domain']} application.
Focus on creating comprehensive test scenarios that ensure robust validation of the user story.
"""
        
        if story_context:
            context += f"""
### Previous Context:
- Similar stories tested: {story_context.get('similar_count', 0)}
- Success rate: {story_context.get('success_rate', 'N/A')}
- Common issues found: {', '.join(story_context.get('common_issues', []))}
"""
        
        return context
    
    @staticmethod
    def _build_examples_section(similar_examples: List[Dict], story_analysis: Dict) -> str:
        """Build the examples section with context"""
        if not similar_examples:
            return "## REFERENCE EXAMPLES:\nNo similar examples found. Focus on comprehensive coverage based on story analysis."
        
        examples_text = "## REFERENCE EXAMPLES:\n"
        examples_text += "Use these examples as reference for structure and quality, but adapt to your specific story:\n"
        
        for i, example in enumerate(similar_examples[:3], 1):  # Limit to top 3
            relevance_note = ""
            if 'context_relevance' in example:
                relevance_note = f" (Relevance: {example['context_relevance']:.2f})"
            
            examples_text += f"""
### Example {i}{relevance_note}:
**Test Case ID:** {example.get('id', f'EX_{i:03d}')}
**Title:** {example.get('title', 'N/A')}
**Preconditions:** {example.get('preconditions', 'N/A')}
**Test Steps:**
{example.get('steps', 'N/A')}
**Expected Result:** {example.get('expected', 'N/A')}
**Priority:** {example.get('priority', 'Medium')}
"""
        
        return examples_text
    
    @staticmethod
    def _build_requirements_section(story_analysis: Dict) -> str:
        """Build requirements section based on story analysis"""
        base_requirements = """
## REQUIREMENTS

### Test Case Generation Requirements:
- Generate all possible test cases covering different scenarios
- Each test case must have a unique ID following the pattern TC_[DOMAIN]_XXX
- Include detailed, step-by-step instructions
- Specify clear preconditions and expected results
- Assign appropriate priority levels
"""
        
        domain_specific = {
            'ecommerce': """
### E-commerce Specific Requirements:
- Test product availability and pricing
- Validate cart functionality and persistence
- Cover payment and checkout scenarios
- Include inventory management edge cases
""",
            'authentication': """
### Authentication Specific Requirements:
- Test various credential combinations
- Cover account lockout scenarios  
- Validate session management
- Include password security requirements
""",
            'web': """
### Web Application Requirements:
- Test cross-browser compatibility considerations
- Validate form submissions and validations
- Cover navigation and user flow scenarios
- Include responsive design considerations
"""
        }
        
        domain_req = domain_specific.get(story_analysis['domain'], "")
        
        return base_requirements + domain_req
    
    @staticmethod
    def _get_focus_areas(story_analysis: Dict) -> str:
        """Get specific focus areas based on story analysis"""
        focus_areas = []
        
        if story_analysis['complexity'] == 'high':
            focus_areas.append("- **Integration Testing**: Focus on system interactions and data flow")
        
        if story_analysis['has_technical_terms']:
            focus_areas.append("- **Technical Validation**: Include API, database, and system-level tests")
        
        if len(story_analysis['user_types']) > 1:
            focus_areas.append("- **Role-Based Testing**: Test different user permission levels")
        
        if story_analysis['domain'] == 'ecommerce':
            focus_areas.append("- **Transaction Flow**: Test complete purchase workflows")
            focus_areas.append("- **Data Consistency**: Validate inventory and pricing accuracy")
        
        return '\n'.join(focus_areas) if focus_areas else "- **Comprehensive Coverage**: Focus on thorough functional testing"