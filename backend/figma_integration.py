# figma_integration.py

import requests
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import base64
import tempfile

@dataclass
class FigmaNode:
    """Represents a Figma design node"""
    id: str
    name: str
    type: str
    visible: bool = True
    children: List['FigmaNode'] = None
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.properties is None:
            self.properties = {}

@dataclass
class FigmaComponent:
    """Represents a UI component extracted from Figma"""
    name: str
    type: str
    description: str
    interactions: List[str] = None
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.interactions is None:
            self.interactions = []
        if self.properties is None:
            self.properties = {}

class FigmaIntegration:
    """
    Integration with Figma API for extracting design information
    """
    
    def __init__(self, access_token: str = None):
        self.access_token = access_token or os.getenv('FIGMA_ACCESS_TOKEN')
        self.base_url = "https://api.figma.com/v1"
        self.headers = {
            'X-Figma-Token': self.access_token,
            'Content-Type': 'application/json'
        }
        
        # UI component patterns for test case generation
        self.ui_component_patterns = {
            'button': ['button', 'btn', 'cta', 'submit', 'click'],
            'input': ['input', 'field', 'textbox', 'text field', 'form'],
            'dropdown': ['dropdown', 'select', 'picker', 'menu'],
            'checkbox': ['checkbox', 'check', 'tick'],
            'radio': ['radio', 'option', 'choice'],
            'link': ['link', 'anchor', 'navigation'],
            'modal': ['modal', 'dialog', 'popup', 'overlay'],
            'tab': ['tab', 'navigation', 'switcher'],
            'card': ['card', 'item', 'tile'],
            'list': ['list', 'table', 'grid', 'collection']
        }
    
    def validate_figma_url(self, figma_url: str) -> Tuple[bool, str, str]:
        """
        Validate and extract file key and node ID from Figma URL
        
        Returns:
            Tuple of (is_valid, file_key, node_id)
        """
        import re
        
        # Figma URL patterns
        patterns = [
            r'https://www\.figma\.com/file/([a-zA-Z0-9\-_]+)/[^?]*(?:\?[^#]*)?(?:#(.+))?',
            r'https://www\.figma\.com/design/([a-zA-Z0-9\-_]+)/[^?]*(?:\?[^#]*)?(?:#(.+))?',
            r'figma://file/([a-zA-Z0-9\-_]+)(?:#(.+))?'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, figma_url)
            if match:
                file_key = match.group(1)
                node_id = match.group(2) if match.group(2) else None
                return True, file_key, node_id
        
        return False, "", ""
    
    def validate_figma_file_access(self, file_key: str) -> Tuple[bool, str]:
        """
        Validate that we can access a Figma file
        
        Returns:
            Tuple of (is_accessible, error_message)
        """
        try:
            url = f"{self.base_url}/files/{file_key}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('err'):
                    return False, f"Figma API error: {data['err']}"
                return True, "File is accessible"
            elif response.status_code == 403:
                return False, "Access denied - check if your token has permission to access this file"
            elif response.status_code == 404:
                return False, "File not found - check if the file ID is correct"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, f"Network error: {str(e)}"
    
    def get_file_info(self, file_key: str) -> Dict[str, Any]:
        """
        Get basic file information from Figma
        """
        try:
            url = f"{self.base_url}/files/{file_key}"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return {
                'name': data.get('name', 'Unknown'),
                'lastModified': data.get('lastModified', ''),
                'version': data.get('version', ''),
                'thumbnailUrl': data.get('thumbnailUrl', ''),
                'document': data.get('document', {})
            }
        except Exception as e:
            print(f"❌ Error fetching Figma file info: {e}")
            return {}
    
    def extract_design_components(self, file_key: str, node_id: str = None) -> List[FigmaComponent]:
        """
        Extract UI components and interactions from Figma file
        """
        try:
            # Get file data
            url = f"{self.base_url}/files/{file_key}"
            if node_id:
                url += f"?ids={node_id}"
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            document = data.get('document', {})
            
            # Extract components
            components = []
            if node_id:
                # Extract specific node
                nodes = data.get('nodes', {})
                if node_id in nodes:
                    node_data = nodes[node_id]['document']
                    components.extend(self._extract_components_from_node(node_data))
            else:
                # Extract from entire document
                components.extend(self._extract_components_from_node(document))
            
            return components
            
        except Exception as e:
            print(f"❌ Error extracting Figma components: {e}")
            return []
    
    def _extract_components_from_node(self, node: Dict[str, Any]) -> List[FigmaComponent]:
        """
        Recursively extract components from a Figma node
        """
        components = []
        
        node_name = node.get('name', '').lower()
        node_type = node.get('type', '')
        
        # Check if this node represents a UI component
        component_type = self._identify_component_type(node_name, node_type)
        if component_type:
            component = FigmaComponent(
                name=node.get('name', 'Unnamed'),
                type=component_type,
                description=self._generate_component_description(node, component_type),
                interactions=self._extract_interactions(node, component_type),
                properties={
                    'figma_type': node_type,
                    'visible': node.get('visible', True),
                    'id': node.get('id', ''),
                    'bounds': node.get('absoluteBoundingBox', {})
                }
            )
            components.append(component)
        
        # Recursively process children
        children = node.get('children', [])
        for child in children:
            components.extend(self._extract_components_from_node(child))
        
        return components
    
    def _identify_component_type(self, name: str, figma_type: str) -> Optional[str]:
        """
        Identify UI component type based on name and Figma type
        """
        name_lower = name.lower()
        
        # Check against known patterns
        for component_type, patterns in self.ui_component_patterns.items():
            if any(pattern in name_lower for pattern in patterns):
                return component_type
        
        # Fallback based on Figma type
        figma_type_mapping = {
            'FRAME': 'container',
            'GROUP': 'group',
            'TEXT': 'text',
            'RECTANGLE': 'shape',
            'ELLIPSE': 'shape',
            'VECTOR': 'icon',
            'INSTANCE': 'component'
        }
        
        return figma_type_mapping.get(figma_type, 'element')
    
    def _generate_component_description(self, node: Dict[str, Any], component_type: str) -> str:
        """
        Generate description for UI component
        """
        name = node.get('name', 'Unnamed')
        
        descriptions = {
            'button': f"Interactive button element '{name}' that users can click",
            'input': f"Input field '{name}' where users can enter text",
            'dropdown': f"Dropdown menu '{name}' for selecting options",
            'checkbox': f"Checkbox '{name}' for boolean selection",
            'radio': f"Radio button '{name}' for single option selection",
            'link': f"Clickable link '{name}' for navigation",
            'modal': f"Modal dialog '{name}' that appears over main content",
            'tab': f"Tab element '{name}' for content switching",
            'card': f"Card component '{name}' displaying grouped information",
            'list': f"List component '{name}' showing collection of items"
        }
        
        return descriptions.get(component_type, f"UI element '{name}' of type {component_type}")
    
    def _extract_interactions(self, node: Dict[str, Any], component_type: str) -> List[str]:
        """
        Extract possible interactions for a component
        """
        interactions = []
        
        # Default interactions based on component type
        interaction_map = {
            'button': ['click', 'tap', 'press'],
            'input': ['type', 'enter text', 'focus', 'blur'],
            'dropdown': ['click', 'select option', 'expand', 'collapse'],
            'checkbox': ['check', 'uncheck', 'toggle'],
            'radio': ['select', 'choose option'],
            'link': ['click', 'navigate'],
            'modal': ['open', 'close', 'dismiss'],
            'tab': ['click', 'switch', 'activate'],
            'card': ['click', 'view details'],
            'list': ['scroll', 'select item', 'browse']
        }
        
        base_interactions = interaction_map.get(component_type, ['interact'])
        interactions.extend(base_interactions)
        
        # Check for prototyping interactions (if available)
        prototype_interactions = node.get('prototypeInteractions', [])
        for interaction in prototype_interactions:
            action = interaction.get('action', {}).get('type', '')
            if action:
                interactions.append(f"prototype: {action}")
        
        return list(set(interactions))  # Remove duplicates
    
    def get_design_context_for_story(self, figma_url: str) -> Dict[str, Any]:
        """
        Extract design context that's relevant for test case generation
        """
        is_valid, file_key, node_id = self.validate_figma_url(figma_url)
        
        if not is_valid:
            return {'error': 'Invalid Figma URL format'}
        
        if not self.access_token:
            return {'error': 'Figma access token not configured'}
        
        try:
            # Get file info
            file_info = self.get_file_info(file_key)
            
            # Extract components
            components = self.extract_design_components(file_key, node_id)
            
            # Generate test-relevant context
            context = {
                'file_info': {
                    'name': file_info.get('name', 'Unknown'),
                    'url': figma_url,
                    'last_modified': file_info.get('lastModified', ''),
                    'node_id': node_id
                },
                'ui_components': [],
                'user_flows': [],
                'test_scenarios': [],
                'design_patterns': []
            }
            
            # Process components for test context
            for component in components:
                ui_info = {
                    'name': component.name,
                    'type': component.type,
                    'description': component.description,
                    'testable_interactions': component.interactions,
                    'test_considerations': self._generate_test_considerations(component)
                }
                context['ui_components'].append(ui_info)
            
            # Generate user flows based on components
            context['user_flows'] = self._identify_user_flows(components)
            
            # Generate test scenarios
            context['test_scenarios'] = self._generate_test_scenarios(components)
            
            # Identify design patterns
            context['design_patterns'] = self._identify_design_patterns(components)
            
            return context
            
        except Exception as e:
            print(f"❌ Error processing Figma design: {e}")
            return {'error': f'Failed to process Figma design: {str(e)}'}
    
    def _generate_test_considerations(self, component: FigmaComponent) -> List[str]:
        """
        Generate test considerations for a UI component
        """
        considerations = []
        
        consideration_map = {
            'button': [
                'Test enabled/disabled states',
                'Verify button text and styling',
                'Test click functionality',
                'Check loading states if applicable'
            ],
            'input': [
                'Test with valid input',
                'Test with invalid input',
                'Test field validation',
                'Test placeholder text',
                'Test character limits'
            ],
            'dropdown': [
                'Test option selection',
                'Test dropdown opening/closing',
                'Test with no options available',
                'Test keyboard navigation'
            ],
            'checkbox': [
                'Test checked/unchecked states',
                'Test in form contexts',
                'Verify label association'
            ],
            'modal': [
                'Test modal opening',
                'Test modal closing',
                'Test modal backdrop behavior',
                'Test keyboard navigation (ESC key)'
            ]
        }
        
        considerations.extend(consideration_map.get(component.type, ['Test basic functionality']))
        
        return considerations
    
    def _identify_user_flows(self, components: List[FigmaComponent]) -> List[str]:
        """
        Identify potential user flows based on components
        """
        flows = []
        
        component_types = [c.type for c in components]
        
        # Common flow patterns
        if 'input' in component_types and 'button' in component_types:
            flows.append('Form submission flow')
        
        if 'modal' in component_types:
            flows.append('Modal interaction flow')
        
        if 'tab' in component_types:
            flows.append('Tab navigation flow')
        
        if 'dropdown' in component_types:
            flows.append('Selection and filtering flow')
        
        if len([c for c in components if c.type == 'button']) > 2:
            flows.append('Multi-step interaction flow')
        
        return flows
    
    def _generate_test_scenarios(self, components: List[FigmaComponent]) -> List[str]:
        """
        Generate test scenarios based on design components
        """
        scenarios = []
        
        for component in components:
            for interaction in component.interactions:
                scenario = f"Test {interaction} on {component.name} ({component.type})"
                scenarios.append(scenario)
        
        # Add cross-component scenarios
        if len(components) > 1:
            scenarios.append("Test component interactions")
            scenarios.append("Test responsive behavior across components")
        
        return scenarios
    
    def _identify_design_patterns(self, components: List[FigmaComponent]) -> List[str]:
        """
        Identify design patterns that affect testing
        """
        patterns = []
        
        component_types = [c.type for c in components]
        
        if 'card' in component_types:
            patterns.append('Card-based layout')
        
        if 'list' in component_types:
            patterns.append('List/Grid pattern')
        
        if 'tab' in component_types:
            patterns.append('Tabbed interface')
        
        if 'modal' in component_types:
            patterns.append('Modal/Overlay pattern')
        
        if len([c for c in components if c.type == 'input']) > 2:
            patterns.append('Form-heavy interface')
        
        return patterns

    def generate_figma_enhanced_prompt_context(self, figma_context: Dict[str, Any], max_length: int = 2000) -> str:
        """
        Generate compressed prompt context from Figma design information
        """
        if 'error' in figma_context:
            return f"Figma Error: {figma_context['error']}"
        
        # Start with essential context
        file_info = figma_context.get('file_info', {})
        context = f"## FIGMA DESIGN: {file_info.get('name', 'Unknown')}\n\n"
        
        # Compress UI Components (most important)
        ui_components = figma_context.get('ui_components', [])
        if ui_components:
            context += "**UI Components:**\n"
            # Group components by type for efficiency
            component_groups = {}
            for comp in ui_components[:15]:  # Limit to 15 components
                comp_type = comp['type']
                if comp_type not in component_groups:
                    component_groups[comp_type] = []
                component_groups[comp_type].append(comp['name'])
            
            for comp_type, names in component_groups.items():
                context += f"- {comp_type}: {', '.join(names[:5])}\n"  # Max 5 names per type
            context += "\n"
        
        # Compress patterns and flows
        design_patterns = figma_context.get('design_patterns', [])
        user_flows = figma_context.get('user_flows', [])
        
        if design_patterns or user_flows:
            context += "**Design Elements:**\n"
            if design_patterns:
                context += f"- Patterns: {', '.join(design_patterns[:3])}\n"
            if user_flows:
                context += f"- Flows: {', '.join(user_flows[:3])}\n"
            context += "\n"
        
        # Essential instructions (shortened)
        context += "**Focus:** Generate UI-focused test cases covering component interactions and user flows.\n"
        
        # Truncate if still too long
        if len(context) > max_length:
            context = context[:max_length - 50] + "...\n[Truncated for size limit]\n"
        
        return context

    def generate_figma_summary_context(self, figma_context: Dict[str, Any]) -> str:
        """
        Generate ultra-compressed summary for prompt context
        """
        if 'error' in figma_context:
            return f"Figma: Error - {figma_context['error'][:100]}"
        
        ui_components = figma_context.get('ui_components', [])
        component_types = list(set([comp['type'] for comp in ui_components[:10]]))
        
        file_name = figma_context.get('file_info', {}).get('name', 'Design')[:20]  # Limit file name length
        
        return f"Figma ({file_name}): {len(ui_components)} components ({', '.join(component_types[:3])}). Test UI interactions."

    def generate_figma_micro_context(self, figma_context: Dict[str, Any]) -> str:
        """
        Generate minimal summary for very constrained contexts
        """
        if 'error' in figma_context:
            return f"Figma: Error"

        ui_components = figma_context.get('ui_components', [])
        component_count = len(ui_components)

        if component_count == 0:
            return "Figma: No components found"

        # Get most common component type
        component_types = [comp['type'] for comp in ui_components[:5]]
        most_common = max(set(component_types), key=component_types.count) if component_types else 'unknown'

        return f"Figma: {component_count} UI elements ({most_common}+). Test interactions."

    def get_enhanced_design_context_with_images(self, figma_url: str) -> Dict[str, Any]:
        """
        Get enhanced design context including image analysis if available
        """
        # Start with basic design context
        basic_context = self.get_design_context_for_story(figma_url)
        
        if 'error' in basic_context:
            return basic_context
        
        # Try to enhance with image analysis if available
        try:
            from enhanced_figma_processor import EnhancedFigmaProcessor
            
            # Extract file info for image processing
            is_valid, file_key, node_id = self.validate_figma_url(figma_url)
            if not is_valid:
                basic_context['image_analysis'] = {
                    'error': 'Invalid Figma URL format',
                    'enhanced_available': False
                }
                return basic_context
            
            print(f"🎨 Attempting enhanced image analysis for file: {file_key}")
            processor = EnhancedFigmaProcessor(self.access_token)
            analysis = processor.analyze_figma_image(file_key, node_id)
            
            if analysis and analysis.quality_score > 0:
                # Add image analysis results to context
                basic_context['image_analysis'] = {
                    'image_url': analysis.screenshot_url,
                    'visual_elements_count': len(analysis.visual_elements),
                    'extracted_text': analysis.extracted_text,
                    'quality_score': analysis.quality_score,
                    'ui_patterns': analysis.ui_patterns,
                    'enhanced_available': True
                }
                
                # Merge test recommendations
                image_recommendations = analysis.test_recommendations
                existing_scenarios = basic_context.get('test_scenarios', [])
                basic_context['test_scenarios'] = existing_scenarios + image_recommendations
                
                # Add enhanced context for prompt generation
                enhanced_context = processor.generate_enhanced_test_context_from_image(analysis)
                basic_context['image_enhanced_context'] = enhanced_context
                
                print(f"✅ Enhanced analysis successful: {len(analysis.visual_elements)} elements detected")
            else:
                print("⚠️ Enhanced analysis failed - falling back to basic context")
                basic_context['image_analysis'] = {
                    'enhanced_available': False,
                    'message': 'Image analysis failed or returned no results',
                    'fallback_reason': 'Low quality analysis or no visual elements detected'
                }
            
        except ImportError:
            # Enhanced processor not available, continue with basic context
            print("⚠️ Enhanced Figma image processing not available (missing dependencies)")
            basic_context['image_analysis'] = {
                'enhanced_available': False,
                'message': 'Install opencv-python numpy for enhanced image analysis'
            }
        except Exception as e:
            error_msg = str(e)
            print(f"⚠️ Enhanced Figma processing error: {error_msg}")
            
            # Provide specific guidance based on error type
            if "400 Client Error" in error_msg or "Bad Request" in error_msg:
                guidance = "Check if the Figma file is public or your token has access to it"
            elif "403" in error_msg or "Access denied" in error_msg:
                guidance = "Your Figma token doesn't have permission to access this file"
            elif "404" in error_msg or "not found" in error_msg:
                guidance = "The Figma file ID might be incorrect or the file doesn't exist"
            else:
                guidance = "Check your Figma URL and token permissions"
            
            basic_context['image_analysis'] = {
                'error': error_msg,
                'enhanced_available': False,
                'guidance': guidance
            }
        
        return basic_context