# prompt_engineering.py

from typing import List, Dict, Any
import re
from datetime import datetime

class AdvancedPromptEngineer:
    """
    Advanced prompt engineering for more accurate test case generation
    """
    

    @staticmethod
    def extract_requirements_from_story(story: str) -> Dict[str, Any]:
        """
        Extract explicit requirements and constraints from user story
        """
        requirements = {
            'acceptance_criteria': [],
            'business_rules': [],
            'user_actions': [],
            'system_behaviors': [],
            'constraints': [],
            'scope_boundaries': []
        }

        # Extract acceptance criteria
        ac_patterns = [
            r'acceptance criteria?:?\s*(.+?)(?=\n\n|\Z)',
            r'given.+?when.+?then.+',
            r'scenario:?\s*(.+?)(?=\n\n|\Z)',
        ]

        for pattern in ac_patterns:
            matches = re.findall(pattern, story, re.IGNORECASE | re.DOTALL)
            requirements['acceptance_criteria'].extend(matches)

        # Extract user actions (I want to...)
        action_pattern = r'I want to\s+(.+?)(?=\s+so that|\s+because|\.|$)'
        user_actions = re.findall(action_pattern, story, re.IGNORECASE)
        requirements['user_actions'] = user_actions

        # Extract business value (so that...)
        value_pattern = r'so that\s+(.+?)(?=\.|$)'
        business_values = re.findall(value_pattern, story, re.IGNORECASE)
        requirements['business_rules'] = business_values

        # Extract constraints
        constraint_patterns = [
            r'must not\s+(.+?)(?=\.|$)',
            r'should not\s+(.+?)(?=\.|$)',
            r'cannot\s+(.+?)(?=\.|$)',
            r'only\s+(.+?)(?=\.|$)',
            r'within\s+\d+\s+\w+',  # time constraints
            r'maximum\s+\d+',       # quantity constraints
            r'minimum\s+\d+'        # quantity constraints
        ]

        for pattern in constraint_patterns:
            matches = re.findall(pattern, story, re.IGNORECASE)
            requirements['constraints'].extend(matches)

        return requirements

    @staticmethod
    def validate_test_case_scope(test_case: Dict, story_requirements: Dict) -> Dict[str, Any]:
        """
        Validate if test case stays within story requirements
        """
        validation_result = {
            'is_valid': True,
            'score': 1.0,
            'issues': [],
            'suggestions': []
        }

        test_title = test_case.get('title', '').lower()
        test_steps = test_case.get('steps', '').lower()
        test_content = f"{test_title} {test_steps}".lower()

        # Check if test relates to user actions
        user_actions = story_requirements.get('user_actions', [])
        if user_actions:
            action_found = any(action.lower() in test_content for action in user_actions)
            if not action_found:
                validation_result['issues'].append("Test case doesn't relate to specified user actions")
                validation_result['score'] -= 0.3

        # Check for scope creep (testing features not mentioned)
        scope_violations = [
            'admin panel', 'database migration', 'api integration',
            'third party', 'external system', 'reporting',
            'analytics', 'backup', 'restore'
        ]

        for violation in scope_violations:
            if violation in test_content and violation not in story_requirements.get('user_actions', []):
                validation_result['issues'].append(f"Potential scope creep: {violation}")
                validation_result['score'] -= 0.2

        # Check constraints compliance
        constraints = story_requirements.get('constraints', [])
        for constraint in constraints:
            if 'not' in constraint.lower() and constraint.lower().replace('not', '').strip() in test_content:
                validation_result['issues'].append(f"Test violates constraint: {constraint}")
                validation_result['score'] -= 0.4

        validation_result['is_valid'] = validation_result['score'] >= 0.7
        return validation_result

    @staticmethod
    def generate_technique_examples(story_analysis: Dict) -> str:
        """Generate specific examples for each testing technique based on story domain"""
        domain = story_analysis['domain']
        
        technique_examples = f"""
### Testing Technique Examples for {domain.title()} Domain:

#### Positive & Negative Testing Examples:
**Positive:** Valid {domain} workflow → Success response
**Negative:** Invalid inputs → Appropriate error messages

#### Boundary Value Analysis Examples:"""
        
        if domain == 'ecommerce':
            technique_examples += """
- Quantity field (1-999): Test 0, 1, 999, 1000
- Price range ($1-$10000): Test $0.99, $1.00, $10000.00, $10000.01
- Product name (3-50 chars): Test 2, 3, 50, 51 characters"""
            
        elif domain == 'authentication':
            technique_examples += """
- Password length (8-128 chars): Test 7, 8, 128, 129 characters
- Login attempts (max 3): Test 3rd, 4th attempt
- Session timeout (30 min): Test at 29:59, 30:00, 30:01"""
            
        else:
            technique_examples += """
- Input field limits: Test minimum-1, minimum, maximum, maximum+1
- Date ranges: Test boundary dates, leap years, invalid dates
- Numeric ranges: Test edge values around limits"""

        technique_examples += """

#### Equivalence Partitioning Examples:
**Valid Partition:** Acceptable input ranges
**Invalid Partition:** Out-of-range, wrong format, null values

#### Decision Table Example:
| Condition 1 | Condition 2 | Action |
|-------------|-------------|---------|
| True        | True        | Accept  |
| True        | False       | Reject  |
| False       | True        | Reject  |
| False       | False       | Reject  |

#### State Transition Examples:"""
        
        if domain == 'ecommerce':
            technique_examples += """
Cart Empty → Add Item → Cart Has Items → Checkout → Order Placed"""
        elif domain == 'authentication':
            technique_examples += """
Logged Out → Enter Credentials → Authenticated → Access Resources → Logout"""
        else:
            technique_examples += """
Initial State → User Action → Intermediate State → Final State"""

        technique_examples += """

#### Error Guessing Focus Areas:
- Common user mistakes and typos
- System limits and resource constraints  
- Network interruptions and timeouts
- Concurrent user actions
- Browser compatibility issues
- Special characters and encoding issues
"""
        
        return technique_examples

    @staticmethod
    def analyze_applicable_techniques(story: str, story_analysis: Dict) -> Dict[str, bool]:
        """Intelligently determine which testing techniques are applicable for this story"""
        story_lower = story.lower()
        
        applicable_techniques = {
            'positive_negative': True,  # Always applicable
            'boundary_value': False,
            'equivalence_partitioning': False,
            'decision_table': False,
            'state_transition': False,
            'error_guessing': True,  # Usually applicable
            'use_case': True,  # Always include end-to-end
            'pairwise': False,
            'adhoc': False
        }
        
        # Boundary Value Analysis - look for numeric constraints, limits, ranges
        boundary_indicators = [
            'maximum', 'minimum', 'limit', 'range', 'between', 'up to', 'at least',
            'length', 'size', 'count', 'number', 'quantity', 'age', 'price',
            'characters', 'digits', 'letters', 'words'
        ]
        if any(indicator in story_lower for indicator in boundary_indicators):
            applicable_techniques['boundary_value'] = True
        
        # Equivalence Partitioning - look for categories, types, classifications
        ep_indicators = [
            'type', 'category', 'role', 'status', 'level', 'grade', 'class',
            'format', 'valid', 'invalid', 'different', 'various'
        ]
        if any(indicator in story_lower for indicator in ep_indicators):
            applicable_techniques['equivalence_partitioning'] = True
        
        # Decision Table - look for complex business rules with multiple conditions
        decision_indicators = [
            'if', 'when', 'and', 'or', 'but', 'unless', 'provided that',
            'depending on', 'based on', 'according to', 'conditions',
            'criteria', 'rules', 'requirements'
        ]
        # Need at least 2 decision indicators for complex rules
        decision_count = sum(1 for indicator in decision_indicators if indicator in story_lower)
        if decision_count >= 2:
            applicable_techniques['decision_table'] = True
        
        # State Transition - look for status changes, workflows, processes
        state_indicators = [
            'status', 'state', 'stage', 'phase', 'step', 'process', 'workflow',
            'approve', 'reject', 'submit', 'complete', 'pending', 'active',
            'inactive', 'enabled', 'disabled', 'from', 'to', 'becomes'
        ]
        if any(indicator in story_lower for indicator in state_indicators):
            applicable_techniques['state_transition'] = True
        
        # Pairwise - look for multiple variables or configurations
        pairwise_indicators = [
            'browser', 'device', 'platform', 'version', 'configuration',
            'setting', 'option', 'mode', 'environment', 'combination'
        ]
        if any(indicator in story_lower for indicator in pairwise_indicators):
            applicable_techniques['pairwise'] = True
        
        # Ad-hoc - for complex or unclear stories
        if (story_analysis.get('complexity') == 'high' or 
            len(story.split()) > 100 or 
            'complex' in story_lower or 
            'integration' in story_lower):
            applicable_techniques['adhoc'] = True
            
        return applicable_techniques

    @staticmethod
    def generate_contextual_technique_guidance(applicable_techniques: Dict[str, bool], story_analysis: Dict) -> str:
        """Generate guidance only for applicable techniques"""
        
        guidance = "### Applicable Testing Techniques for This Story:\n\n"
        
        # Always include basics
        guidance += "#### ✅ **Positive & Negative Testing** (Always Required)\n"
        guidance += "- Test valid inputs and expected flows\n"
        guidance += "- Test invalid inputs and error scenarios\n\n"
        
        if applicable_techniques['boundary_value']:
            guidance += "#### ✅ **Boundary Value Analysis** (Detected: Numeric limits/ranges in story)\n"
            guidance += "- Test minimum, maximum, and edge values\n"
            guidance += "- Focus on the specific limits mentioned in the story\n\n"
        
        if applicable_techniques['equivalence_partitioning']:
            guidance += "#### ✅ **Equivalence Partitioning** (Detected: Categories/types in story)\n" 
            guidance += "- Group similar inputs and test representative values\n"
            guidance += "- Focus on the data classifications mentioned\n\n"
        
        if applicable_techniques['decision_table']:
            guidance += "#### ✅ **Decision Table Testing** (Detected: Complex business rules)\n"
            guidance += "- Create combinations of conditions and actions\n"
            guidance += "- Cover all logical combinations of the business rules\n\n"
        
        if applicable_techniques['state_transition']:
            guidance += "#### ✅ **State Transition Testing** (Detected: Status/workflow changes)\n"
            guidance += "- Test transitions between different states\n"
            guidance += "- Focus on the state changes mentioned in the story\n\n"
        
        if applicable_techniques['pairwise']:
            guidance += "#### ✅ **Pairwise Testing** (Detected: Multiple variables/configurations)\n"
            guidance += "- Test important combinations without full permutation\n"
            guidance += "- Focus on the variable interactions mentioned\n\n"
        
        if applicable_techniques['adhoc']:
            guidance += "#### ✅ **Ad-hoc Testing** (Complex story detected)\n"
            guidance += "- Include exploratory scenarios for edge cases\n"
            guidance += "- Focus on potential integration or complexity issues\n\n"
        
        guidance += "#### ✅ **Use Case Testing** (Always Required)\n"
        guidance += "- Include complete end-to-end user scenario\n\n"
        
        guidance += "#### ✅ **Error Guessing** (Always Required)\n"
        guidance += "- Include experience-based edge cases\n\n"
        
        # Add techniques NOT applicable
        not_applicable = []
        if not applicable_techniques['boundary_value']:
            not_applicable.append("Boundary Value Analysis (no numeric limits detected)")
        if not applicable_techniques['equivalence_partitioning']:
            not_applicable.append("Equivalence Partitioning (no data categories detected)")
        if not applicable_techniques['decision_table']:
            not_applicable.append("Decision Table (no complex business rules detected)")
        if not applicable_techniques['state_transition']:
            not_applicable.append("State Transition (no status changes detected)")
        if not applicable_techniques['pairwise']:
            not_applicable.append("Pairwise Testing (no multiple variables detected)")
        if not applicable_techniques['adhoc']:
            not_applicable.append("Ad-hoc Testing (story is straightforward)")
        
        if not_applicable:
            guidance += "### ❌ Techniques NOT Applicable (Don't Force These):\n"
            for technique in not_applicable:
                guidance += f"- {technique}\n"
        
        return guidance

    @staticmethod
    def build_enhanced_prompt(story: str, similar_examples: List[Dict], 
                            story_context: Dict = None) -> str:
        """
        Build an enhanced prompt with better structure and context
        """

        # Extract explicit requirements first
        story_requirements = AdvancedPromptEngineer.extract_requirements_from_story(story)
        
        # Analyze story characteristics
        story_analysis = AdvancedPromptEngineer._analyze_story(story)
        story_analysis['requirements'] = story_requirements

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

        # Analyze which techniques are actually applicable
        applicable_techniques = AdvancedPromptEngineer.analyze_applicable_techniques(story, story_analysis)
        
        # Build contextual technique guidance
        technique_guidance = AdvancedPromptEngineer.generate_contextual_technique_guidance(
            applicable_techniques, story_analysis
        )

        scope_constraints = AdvancedPromptEngineer._build_scope_constraints(story_requirements)
        
        prompt = f"""
{context_section}

{requirements_section}

## USER STORY TO ANALYZE:
{story}

{examples_section}

{technique_guidance}

{scope_constraints}

## GENERATION INSTRUCTIONS:

### Quality Standards:
1. **Precision**: Each test case must be directly related to the user story
2. **Completeness**: Cover all acceptance criteria and edge cases
3. **Clarity**: Use clear, actionable language that any QA tester can follow
4. **Coverage**: Include positive, negative, boundary, and edge test scenarios
5. **Traceability**: Each test case should map back to specific story requirements

### CRITICAL: Test cases must ONLY test what is explicitly mentioned in the user story. Do not test features, integrations, or functionality not described in the requirements.

### Advanced Test Case Writing Techniques to Apply:

#### 1. **Positive & Negative Testing**
- **Positive Tests**: Verify system works with valid inputs and expected user flows
- **Negative Tests**: Verify system handles invalid inputs, edge cases, and error conditions gracefully
- Examples: Valid login vs invalid credentials, proper form submission vs missing required fields

#### 2. **Boundary Value Analysis (BVA)**
- Test values at boundaries (minimum, maximum, just inside, just outside limits)
- Focus on edge conditions where most defects occur
- Examples: Age field 18-60 → test 17, 18, 60, 61; String length limits; Date ranges

#### 3. **Equivalence Partitioning (EP)**
- Divide input data into valid and invalid partitions
- Test representative values from each partition to reduce redundant testing
- Examples: PIN codes (valid 6-digit vs invalid 5-digit/7-digit)

#### 4. **Decision Table Testing**
- Use combinations of conditions → actions for complex business rules
- Create test cases covering all condition combinations
- Examples: Loan approval (Salary + CIBIL score combinations)

#### 5. **State Transition Testing**
- Test system behavior when moving between different states
- Focus on events, conditions, and state changes
- Examples: ATM states (card inserted → PIN entry → transactions), order statuses

#### 6. **Error Guessing**
- Apply tester experience and intuition to identify potential problem areas
- Think about common user mistakes and system vulnerabilities
- Examples: File upload size limits, special characters in fields, concurrent access

#### 7. **Use Case Testing**
- Derive test cases from complete user journeys and business scenarios
- Ensure end-to-end workflow validation
- Examples: E-commerce checkout flow, user registration process

#### 8. **Pairwise/Orthogonal Array Testing**
- Test important combinations of parameters without full permutation explosion
- Useful when multiple variables interact
- Examples: Browser × OS combinations, feature flags combinations

#### 9. **Ad-hoc Testing**
- Include exploratory testing scenarios for uncovering hidden defects
- Focus on intuitive user interactions and unexpected usage patterns

### Test Case Categories with Techniques:
- **Functional Testing**: Positive/Negative, Use Case, Decision Table
- **Boundary Testing**: BVA, Equivalence Partitioning
- **State-Based Testing**: State Transition, Error Guessing
- **Integration Testing**: Pairwise testing, End-to-end scenarios
- **Security Testing**: Negative testing, Error guessing, Boundary conditions
- **Usability Testing**: Ad-hoc testing, Use case scenarios

### Specific Focus Areas Based on Story Analysis:
{AdvancedPromptEngineer._get_focus_areas(story_analysis)}

### Output Format (STRICT):
For each test case, use EXACTLY this format:

**Test Case ID:** TC_{story_analysis['domain'].upper()}_{'{:03d}'.format(1)}
**Title:** [Clear, descriptive title]
**Test Technique:** [Primary technique used: Positive/Negative, BVA, EP, Decision Table, State Transition, Error Guessing, Use Case, Pairwise, Ad-hoc]
**Preconditions:** [What must be true before testing]
**Test Steps:**
1. [First action step]
2. [Second action step]
3. [Continue as needed]
**Expected Result:** [Specific, measurable expected outcome]
**Priority:** [Critical/High/Medium/Low based on story importance]
**Category:** [Functional/Boundary/Integration/Security/Usability/Performance]
**Test Data:** [Specific test data values if applicable, especially for BVA/EP]
**Requirement Mapping:** [Which specific requirement from the story this test validates]

### Intelligent Technique Selection:
**IMPORTANT**: Only apply testing techniques that are relevant to the specific user story. Do not force techniques that don't naturally fit.

#### Apply techniques based on story content:

**Always Include:**
- **Positive Testing**: Core functionality with valid inputs
- **Negative Testing**: Error handling for invalid scenarios

**Include Only When Relevant:**
- **Boundary Value Analysis**: ONLY if story mentions numeric limits, ranges, or size constraints
- **Equivalence Partitioning**: ONLY if story has categorized inputs or data classifications
- **Decision Table**: ONLY if story has multiple business rules with different condition combinations
- **State Transition**: ONLY if story involves status changes, workflows, or system states
- **Error Guessing**: Include based on complexity and potential failure points
- **Use Case Testing**: Always include one end-to-end scenario
- **Pairwise Testing**: ONLY if story mentions multiple variables or configurations
- **Ad-hoc Testing**: ONLY if story seems complex or has unclear requirements

### Story Analysis for Technique Selection:
- **Simple display/view stories** → Focus on Positive + Negative testing only
- **Stories with input fields** → Add Boundary/Equivalence if limits mentioned
- **Stories with business rules** → Add Decision Tables if multiple conditions
- **Stories with workflows** → Add State Transitions if status changes mentioned
- **Stories with configurations** → Add Pairwise if multiple options interact

### SMART TESTING TECHNIQUE APPLICATION:

#### MANDATORY for all stories:
1. **Positive Testing**: At least 1-2 test cases with valid inputs and expected flows
2. **Negative Testing**: At least 1-2 test cases with invalid inputs and error scenarios  
3. **Use Case Testing**: One complete end-to-end user journey
4. **Error Guessing**: Common failure scenarios based on story context

#### CONDITIONAL - Apply ONLY when story content indicates relevance:
5. **Boundary Value Analysis**: ONLY if story mentions specific limits, ranges, or constraints
6. **Equivalence Partitioning**: ONLY if story has different input categories or data types
7. **Decision Tables**: ONLY if story has complex business rules with multiple conditions
8. **State Transitions**: ONLY if story involves status changes or workflows
9. **Pairwise Testing**: ONLY if story mentions multiple variables or configurations
10. **Ad-hoc Testing**: ONLY if story is complex or has integration requirements

#### Quality over Quantity:
- **Better to have 5-8 highly relevant test cases than 15 forced ones**
- **Each test case must have clear value and purpose**
- **Don't create test cases just to use a technique**
- **Focus on what could realistically break or fail**

### STRICT BOUNDARIES:
- ONLY test functionality explicitly mentioned in the user story
- DO NOT add tests for features not described in requirements  
- Stay within the defined scope and acceptance criteria
- If acceptance criteria are provided, ensure ALL test cases map to them
- **CRITICAL**: Only apply testing techniques that naturally fit the story content
- **DO NOT force techniques** - if BVA doesn't apply, don't create artificial boundary tests
- **DO NOT create fake scenarios** just to use a specific technique
- Each test case should solve a real testing need, not just demonstrate a technique
- Quality and relevance over technique coverage
- **It's better to skip a technique than to force it inappropriately**
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
    def _build_scope_constraints(story_requirements: Dict) -> str:
        """Build scope constraint section"""
        constraints_text = "## SCOPE CONSTRAINTS:\n\n"

        if story_requirements['user_actions']:
            constraints_text += "### User Actions to Test:\n"
            for action in story_requirements['user_actions']:
                constraints_text += f"- {action}\n"

        if story_requirements['constraints']:
            constraints_text += "\n### Business Constraints:\n"
            for constraint in story_requirements['constraints']:
                constraints_text += f"- {constraint}\n"

        if story_requirements['acceptance_criteria']:
            constraints_text += "\n### Acceptance Criteria:\n"
            for criteria in story_requirements['acceptance_criteria']:
                constraints_text += f"- {criteria}\n"

        return constraints_text

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
            focus_areas.append("- **Transaction Flow**: Use case testing for complete purchase workflows")
            focus_areas.append("- **Data Consistency**: Boundary testing for inventory limits and pricing")
            focus_areas.append("- **Cart State Transitions**: Test add/remove/modify item states")
            focus_areas.append("- **Payment Decision Tables**: Test various payment method combinations")
            
        if story_analysis['domain'] == 'authentication':
            focus_areas.append("- **Credential Validation**: Equivalence partitioning for username/password formats")
            focus_areas.append("- **Session State Testing**: State transitions for login/logout flows")
            focus_areas.append("- **Security Boundaries**: BVA for password complexity, attempt limits")
            
        if story_analysis['domain'] == 'web':
            focus_areas.append("- **Form Validation**: Positive/negative testing for all input fields")
            focus_areas.append("- **Browser Compatibility**: Pairwise testing across browsers and devices")
            focus_areas.append("- **Navigation States**: State transition testing for page flows")
        
        return '\n'.join(focus_areas) if focus_areas else "- **Comprehensive Coverage**: Focus on thorough functional testing"