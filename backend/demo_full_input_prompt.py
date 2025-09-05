#!/usr/bin/env python3

"""
Demonstration: How prompts are constructed with User Story + Figma + PDF inputs
"""

import sys
import os
import tempfile
from io import BytesIO
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demonstrate_full_prompt_construction():
    """Demonstrate how the system constructs prompts with all inputs"""
    
    print("🎭 FULL INPUT PROMPT CONSTRUCTION DEMONSTRATION")
    print("=" * 80)
    
    # Mock input data (simulating what the API receives)
    user_story_text = """
As a banking customer, I want to transfer money between my checking and savings accounts
with validation of available balance, daily transfer limits of $5,000, and two-factor authentication
so that I can manage my finances securely. 

The system should:
- Display current account balances
- Allow selection of source and destination accounts  
- Validate transfer amount against available balance
- Enforce daily transfer limits
- Require two-factor authentication for transfers over $1,000
- Provide real-time transaction confirmations
- Send SMS notifications for completed transfers
"""
    
    # Mock PDF content (typical requirements document)
    pdf_content = """
## BANKING SYSTEM REQUIREMENTS

### Account Transfer Module - Technical Specifications

**Functional Requirements:**
- FR-001: System shall display account balances in real-time
- FR-002: Transfer limits: Minimum $1.00, Maximum $5,000 per day
- FR-003: Two-factor authentication required for transfers > $1,000
- FR-004: Transaction processing time: < 5 seconds
- FR-005: SMS notifications sent within 30 seconds of transfer completion

**Business Rules:**
- BR-001: Transfers only allowed between accounts of same customer
- BR-002: Insufficient funds should display clear error message
- BR-003: Daily limit resets at midnight EST
- BR-004: Failed transfers due to system errors should be auto-retried once

**Security Requirements:**
- SEC-001: All transfer data encrypted in transit
- SEC-002: Transaction logs maintained for 7 years
- SEC-003: Multiple failed authentication attempts lock account for 15 minutes

**UI Requirements:**
- UI-001: Balance display updated in real-time
- UI-002: Transfer confirmation screen shows all details
- UI-003: Progress indicator during transfer processing
- UI-004: Error messages displayed prominently
"""
    
    # Mock Figma content (design specifications)
    figma_content = """
## FIGMA DESIGN ANALYSIS

**Design URL:** https://www.figma.com/file/abc123/Banking-Transfer-Flow

**UI Components Identified:**
- Account Selection Dropdown (2 instances: Source, Destination)
- Amount Input Field (Currency formatted, $0.00)
- Balance Display Cards (Real-time, Green/Red indicators)
- Transfer Button (Primary CTA, Blue #0066CC)
- Authentication Modal (PIN + SMS verification)
- Confirmation Screen (Transaction details, Print option)
- Error Alert Banner (Red background, White text)

**Visual Elements:**
- Color Scheme: Primary Blue #0066CC, Success Green #28A745, Error Red #DC3545
- Typography: Roboto font family, 16px base size
- Layout: 2-column grid, Mobile responsive breakpoints
- Icons: Money transfer, Security shield, SMS notification

**Interactive Elements:**
- Account dropdown with search functionality
- Amount field with currency validation
- Slider for common amounts ($100, $500, $1000)
- Biometric authentication option (Touch ID/Face ID)
- Progress stepper (4 steps: Select → Amount → Verify → Complete)

**Accessibility Features:**
- ARIA labels on all form elements
- High contrast mode support
- Screen reader compatible
- Keyboard navigation support
"""
    
    print("📝 INPUT COMPONENTS:")
    print("-" * 40)
    print(f"1️⃣ User Story: {len(user_story_text)} characters")
    print(f"2️⃣ PDF Content: {len(pdf_content)} characters")  
    print(f"3️⃣ Figma Content: {len(figma_content)} characters")
    
    # Combine all inputs (as the system does)
    full_story = f"{user_story_text}\n\n{pdf_content}\n\n{figma_content}".strip()
    
    print(f"\n📊 COMBINED INPUT:")
    print(f"   Total length: {len(full_story):,} characters")
    print(f"   Word count: {len(full_story.split()):,} words")
    
    # Show how the system processes this
    print(f"\n🔄 PROCESSING STEPS:")
    print("   1. Extract text from PDF attachments")
    print("   2. Process Figma design and extract UI components")
    print("   3. Combine user story + PDF content + Figma analysis")
    print("   4. Retrieve similar test cases from RAG system")
    print("   5. Build optimized prompt with intelligent technique selection")
    print("   6. Compress if needed to fit API limits")
    
    # Now show the optimized prompt generation
    try:
        from optimized_prompt_engineering import OptimizedPromptEngineer
        
        print(f"\n🚀 OPTIMIZED PROMPT GENERATION:")
        print("-" * 60)
        
        # Analyze the story essentials
        story_essentials = OptimizedPromptEngineer.extract_story_essentials(full_story)
        applicable_techniques = OptimizedPromptEngineer.determine_applicable_techniques(story_essentials)
        
        print(f"📋 Story Analysis:")
        print(f"   Domain: {story_essentials['domain']}")
        print(f"   Complexity: {'High' if story_essentials['is_complex'] else 'Standard'}")
        print(f"   Has Inputs: {story_essentials['has_inputs']}")
        print(f"   Has States: {story_essentials['has_states']}")
        print(f"   Has Limits: {story_essentials['has_limits']}")
        print(f"   Has Categories: {story_essentials['has_categories']}")
        
        print(f"\n🎯 Applicable Techniques: {', '.join(applicable_techniques)}")
        
        # Mock similar test cases (what RAG system might return)
        mock_similar_cases = [
            {
                'id': 'TC_BANK_001',
                'title': 'Valid account transfer with sufficient balance',
                'priority': 'High',
                'preconditions': 'User logged in, sufficient balance available',
                'steps': '1. Select source account\n2. Enter transfer amount\n3. Confirm transfer',
                'expected': 'Transfer completed successfully with confirmation',
                'technique': 'Positive Testing'
            },
            {
                'id': 'TC_BANK_002',
                'title': 'Transfer exceeding daily limit',
                'priority': 'High', 
                'preconditions': 'User has already transferred maximum amount today',
                'steps': '1. Attempt transfer above limit\n2. System validates\n3. Check error handling',
                'expected': 'Daily limit exceeded error displayed',
                'technique': 'Boundary Testing'
            }
        ]
        
        # Generate the actual optimized prompt
        optimized_prompt = OptimizedPromptEngineer.build_concise_prompt(full_story, mock_similar_cases)
        
        print(f"\n📄 GENERATED OPTIMIZED PROMPT:")
        print("=" * 80)
        print(optimized_prompt)
        print("=" * 80)
        
        print(f"\n📊 PROMPT STATISTICS:")
        prompt_lines = optimized_prompt.split('\n')
        print(f"   Length: {len(optimized_prompt):,} characters")
        print(f"   Lines: {len(prompt_lines):,}")
        print(f"   Words: {len(optimized_prompt.split()):,}")
        print(f"   API Compliant: {'✅ Yes' if len(optimized_prompt) < 8000 else '❌ No'}")
        
        # Compare with standard prompt (if available)
        try:
            from prompt_engineering import AdvancedPromptEngineer
            standard_prompt = AdvancedPromptEngineer.build_enhanced_prompt(full_story, mock_similar_cases, {})
            
            size_reduction = ((len(standard_prompt) - len(optimized_prompt)) / len(standard_prompt)) * 100
            
            print(f"\n📈 OPTIMIZATION COMPARISON:")
            print(f"   Standard prompt: {len(standard_prompt):,} characters")
            print(f"   Optimized prompt: {len(optimized_prompt):,} characters")
            print(f"   Size reduction: {size_reduction:.1f}%")
            print(f"   Standard API compliant: {'✅ Yes' if len(standard_prompt) < 8000 else '❌ No'}")
            
        except Exception as e:
            print(f"   (Standard comparison unavailable: {e})")
            
    except Exception as e:
        print(f"❌ Optimization demo failed: {e}")
        return
    
    # Show how content is structured in the prompt
    print(f"\n🏗️ PROMPT STRUCTURE BREAKDOWN:")
    print("-" * 60)
    
    sections = optimized_prompt.split('## ')
    for i, section in enumerate(sections):
        if section.strip():
            lines = section.split('\n')
            title = lines[0] if lines else "Header"
            content_length = len(section)
            print(f"   {i+1}. {title}: {content_length} characters")

def demonstrate_content_flow():
    """Show how different input types flow through the system"""
    
    print(f"\n🌊 CONTENT FLOW DEMONSTRATION:")
    print("=" * 80)
    
    flow_steps = [
        ("User Story Text", "Direct text input from form field", "✅ Always present"),
        ("PDF Processing", "Extract requirements, specs, business rules", "📄 If PDF attached"),
        ("Figma Analysis", "Extract UI components, design patterns", "🎨 If Figma URL provided"),
        ("Content Combination", "Merge all inputs into full_story variable", "🔄 Always"),
        ("RAG Retrieval", "Find similar test cases from database", "🤖 If available"),
        ("Story Analysis", "Extract domain, complexity, techniques", "📊 Always"),
        ("Prompt Generation", "Build optimized or standard prompt", "⚙️ Always"),
        ("Size Compression", "Compress if exceeds API limits", "📦 If needed"),
        ("API Call", "Send to LLM for test case generation", "🚀 Always")
    ]
    
    for step, description, condition in flow_steps:
        print(f"📋 {step:18} → {description:40} ({condition})")

def show_example_scenarios():
    """Show different input combination scenarios"""
    
    print(f"\n🎯 INPUT COMBINATION SCENARIOS:")
    print("=" * 80)
    
    scenarios = [
        {
            "name": "Story Only",
            "inputs": "User story text",
            "prompt_size": "~1,500-2,000 chars",
            "techniques": "3-5 techniques",
            "api_safe": "✅ Always"
        },
        {
            "name": "Story + PDF",
            "inputs": "User story + Requirements PDF",
            "prompt_size": "~2,500-4,000 chars",
            "techniques": "4-7 techniques", 
            "api_safe": "✅ Usually"
        },
        {
            "name": "Story + Figma",
            "inputs": "User story + Design mockup",
            "prompt_size": "~2,000-3,500 chars",
            "techniques": "4-6 techniques",
            "api_safe": "✅ Usually"
        },
        {
            "name": "All Inputs",
            "inputs": "Story + PDF + Figma + RAG examples",
            "prompt_size": "~4,000-6,000 chars",
            "techniques": "5-8 techniques",
            "api_safe": "✅ With optimization"
        }
    ]
    
    print(f"{'Scenario':15} {'Inputs':30} {'Prompt Size':15} {'Techniques':12} {'API Safe':10}")
    print("-" * 85)
    
    for scenario in scenarios:
        print(f"{scenario['name']:15} {scenario['inputs']:30} {scenario['prompt_size']:15} {scenario['techniques']:12} {scenario['api_safe']:10}")

if __name__ == "__main__":
    demonstrate_full_prompt_construction()
    demonstrate_content_flow()
    show_example_scenarios()
    
    print(f"\n🎯 KEY TAKEAWAYS:")
    print("=" * 80)
    print("✅ System intelligently combines ALL input types into coherent prompts")
    print("✅ Optimized prompts stay within API limits even with multiple inputs")
    print("✅ Content is analyzed to select only relevant testing techniques")
    print("✅ PDF + Figma content enhances test case coverage and accuracy")
    print("✅ RAG system provides relevant examples for better context")
    print("✅ Automatic fallbacks ensure system always works")
    
    print(f"\n🚀 To see this in action:")
    print("   1. Start the Flask app: python app.py")
    print("   2. Upload user story + PDF + Figma URL via API")
    print("   3. Check console logs for detailed processing info")
    print("   4. Review generated test cases for comprehensive coverage")