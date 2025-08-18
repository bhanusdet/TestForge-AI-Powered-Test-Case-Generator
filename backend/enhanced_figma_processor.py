"""
Enhanced Figma Image Processor for AI Test Case Generator

This module provides advanced Figma image processing capabilities including:
- Screenshot capture from Figma designs
- Visual element detection and analysis
- Enhanced OCR with design context
- Image-to-test-case mapping
"""

import requests
import json
import os
import base64
import tempfile
import io
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import cv2
import numpy as np

@dataclass
class VisualElement:
    """Represents a visual element detected in Figma screenshots"""
    element_type: str
    text_content: str
    coordinates: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float
    properties: Dict[str, Any]

@dataclass
class FigmaImageAnalysis:
    """Results of Figma image analysis"""
    screenshot_url: str
    visual_elements: List[VisualElement]
    extracted_text: str
    ui_patterns: List[str]
    test_recommendations: List[str]
    quality_score: float

class EnhancedFigmaProcessor:
    """
    Enhanced Figma processor with image analysis capabilities
    """
    
    def __init__(self, access_token: str = None):
        self.access_token = access_token or os.getenv('FIGMA_ACCESS_TOKEN')
        self.base_url = "https://api.figma.com/v1"
        self.headers = {
            'X-Figma-Token': self.access_token,
            'Content-Type': 'application/json'
        }
        
        # Configure OCR for better accuracy (simplified to avoid escape character issues)
        self.ocr_config = r'--oem 3 --psm 6'
        
        # UI element detection patterns
        self.ui_patterns = {
            'button': {
                'keywords': ['button', 'btn', 'click', 'submit', 'save', 'cancel', 'ok', 'confirm'],
                'visual_cues': ['rounded_rectangle', 'colored_background', 'centered_text']
            },
            'input_field': {
                'keywords': ['input', 'field', 'enter', 'type', 'search', 'email', 'password'],
                'visual_cues': ['rectangle_outline', 'placeholder_text', 'cursor_indicator']
            },
            'dropdown': {
                'keywords': ['select', 'choose', 'dropdown', 'menu', 'options'],
                'visual_cues': ['arrow_down', 'list_indicator', 'expandable']
            },
            'checkbox': {
                'keywords': ['check', 'select', 'agree', 'accept', 'enable'],
                'visual_cues': ['small_square', 'tick_mark', 'boolean_choice']
            },
            'navigation': {
                'keywords': ['home', 'back', 'next', 'menu', 'nav', 'breadcrumb'],
                'visual_cues': ['horizontal_list', 'arrow_indicators', 'menu_items']
            }
        }
    
    def capture_figma_screenshots(self, file_key: str, node_ids: List[str] = None, 
                                scale: float = 2.0, format: str = 'png') -> Dict[str, str]:
        """
        Capture screenshots from Figma designs
        
        Args:
            file_key: Figma file identifier
            node_ids: Specific nodes to capture (if None, captures entire file)
            scale: Image scale factor (1-4)
            format: Image format ('png' or 'jpg')
            
        Returns:
            Dictionary mapping node_id to image URL
        """
        try:
            # First, validate that the file exists and is accessible
            file_url = f"{self.base_url}/files/{file_key}"
            file_response = requests.get(file_url, headers=self.headers, timeout=30)
            
            if file_response.status_code == 404:
                raise Exception(f"Figma file not found: {file_key}. Check if the file ID is correct and accessible.")
            elif file_response.status_code == 403:
                raise Exception(f"Access denied to Figma file: {file_key}. Check if your token has permission to access this file.")
            
            file_response.raise_for_status()
            file_data = file_response.json()
            
            if file_data.get('err'):
                raise Exception(f"Figma file error: {file_data['err']}")
            
            # Build screenshot request URL
            url = f"{self.base_url}/images/{file_key}"
            params = {
                'format': format,
                'scale': str(min(4.0, max(1.0, scale)))  # Ensure scale is between 1-4
            }
            
            # Figma requires either specific node IDs or we need to get them from the file
            if node_ids:
                params['ids'] = ','.join(node_ids)
            else:
                # Get the root canvas nodes from the file to capture
                print("📋 Getting canvas nodes for screenshot capture...")
                canvas_nodes = self._get_canvas_nodes(file_key)
                if canvas_nodes:
                    params['ids'] = ','.join(canvas_nodes[:3])  # Limit to first 3 canvases
                    print(f"🎯 Using canvas nodes: {params['ids']}")
                else:
                    raise Exception("No canvas nodes found in the file for screenshot capture")
            
            print(f"🎨 Requesting Figma screenshots: {url}")
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 400:
                error_detail = response.json() if response.headers.get('content-type') == 'application/json' else response.text
                raise Exception(f"Bad request to Figma API. Details: {error_detail}")
            elif response.status_code == 403:
                raise Exception(f"Access denied. Your Figma token may not have permission to generate images for this file.")
            elif response.status_code == 404:
                raise Exception(f"File not found or nodes don't exist in the file.")
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('err'):
                raise Exception(f"Figma API error: {data['err']}")
            
            image_urls = data.get('images', {})
            
            if not image_urls:
                raise Exception("No images returned from Figma API. The file might be empty or inaccessible.")
            
            print(f"✅ Captured {len(image_urls)} screenshots from Figma")
            return image_urls
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error capturing Figma screenshots: {e}")
            return {}
        except Exception as e:
            print(f"❌ Error capturing Figma screenshots: {e}")
            return {}
    
    def _get_canvas_nodes(self, file_key: str) -> List[str]:
        """
        Get canvas node IDs from a Figma file
        
        Args:
            file_key: Figma file identifier
            
        Returns:
            List of canvas node IDs
        """
        try:
            url = f"{self.base_url}/files/{file_key}"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            document = data.get('document', {})
            
            canvas_nodes = []
            for child in document.get('children', []):
                if child.get('type') == 'CANVAS':
                    canvas_nodes.append(child.get('id'))
            
            print(f"📋 Found {len(canvas_nodes)} canvas nodes")
            return canvas_nodes
            
        except Exception as e:
            print(f"❌ Error getting canvas nodes: {e}")
            return []
    
    def download_and_preprocess_image(self, image_url: str) -> Optional[np.ndarray]:
        """
        Download Figma image and preprocess for analysis
        
        Args:
            image_url: URL of the Figma screenshot
            
        Returns:
            Preprocessed image as numpy array
        """
        try:
            # Download image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Convert to PIL Image
            image_data = io.BytesIO(response.content)
            pil_image = Image.open(image_data)
            
            # Convert to RGB if necessary
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Enhance image for better OCR
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(1.2)
            
            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(1.1)
            
            # Convert to numpy array for OpenCV processing
            cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            return cv_image
            
        except Exception as e:
            print(f"❌ Error downloading/preprocessing image: {e}")
            return None
    
    def extract_text_with_context(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extract text from image with positional context
        
        Args:
            image: Preprocessed image as numpy array
            
        Returns:
            Dictionary with extracted text and positional data
        """
        try:
            # Convert back to PIL for Tesseract
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Try detailed OCR first, fallback to simple if it fails
            try:
                ocr_data = pytesseract.image_to_data(
                    pil_image, 
                    config=self.ocr_config,
                    output_type=pytesseract.Output.DICT
                )
            except Exception as ocr_error:
                print(f"⚠️ Detailed OCR failed ({ocr_error}), trying simple OCR...")
                # Fallback to simple text extraction
                simple_text = pytesseract.image_to_string(pil_image)
                return {
                    'full_text': simple_text.strip(),
                    'text_elements': [],
                    'total_words': len(simple_text.split()) if simple_text else 0,
                    'average_confidence': 50  # Default confidence for simple OCR
                }
            
            # Extract text with coordinates
            text_elements = []
            full_text = []
            
            for i in range(len(ocr_data['text'])):
                text = ocr_data['text'][i].strip()
                if text and int(ocr_data['conf'][i]) > 30:  # Confidence threshold
                    text_elements.append({
                        'text': text,
                        'x': ocr_data['left'][i],
                        'y': ocr_data['top'][i],
                        'width': ocr_data['width'][i],
                        'height': ocr_data['height'][i],
                        'confidence': int(ocr_data['conf'][i])
                    })
                    full_text.append(text)
            
            return {
                'full_text': ' '.join(full_text),
                'text_elements': text_elements,
                'total_words': len([t for t in text_elements if len(t['text']) > 1]),
                'average_confidence': np.mean([t['confidence'] for t in text_elements]) if text_elements else 0
            }
            
        except Exception as e:
            print(f"❌ Error extracting text: {e}")
            return {
                'full_text': '',
                'text_elements': [],
                'total_words': 0,
                'average_confidence': 0
            }
    
    def detect_ui_elements(self, image: np.ndarray, text_data: Dict[str, Any]) -> List[VisualElement]:
        """
        Detect UI elements using computer vision and text analysis
        
        Args:
            image: Preprocessed image
            text_data: OCR text data with positions
            
        Returns:
            List of detected visual elements
        """
        visual_elements = []
        
        try:
            # Convert to grayscale for contour detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Find rectangles (potential buttons, input fields)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Analyze text elements for UI patterns
            for text_element in text_data['text_elements']:
                element_type = self._classify_text_element(text_element['text'])
                
                if element_type:
                    visual_elements.append(VisualElement(
                        element_type=element_type,
                        text_content=text_element['text'],
                        coordinates=(
                            text_element['x'],
                            text_element['y'],
                            text_element['width'],
                            text_element['height']
                        ),
                        confidence=text_element['confidence'] / 100.0,
                        properties={
                            'detection_method': 'text_analysis',
                            'area': text_element['width'] * text_element['height']
                        }
                    ))
            
            # Analyze geometric shapes for UI elements
            for contour in contours:
                area = cv2.contourArea(contour)
                if 100 < area < 50000:  # Filter reasonable sizes
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Classify based on shape characteristics
                    aspect_ratio = w / h if h > 0 else 0
                    element_type = self._classify_geometric_element(aspect_ratio, area)
                    
                    if element_type:
                        visual_elements.append(VisualElement(
                            element_type=element_type,
                            text_content='',
                            coordinates=(x, y, w, h),
                            confidence=0.7,  # Medium confidence for geometric detection
                            properties={
                                'detection_method': 'geometric_analysis',
                                'aspect_ratio': aspect_ratio,
                                'area': area
                            }
                        ))
            
            print(f"✅ Detected {len(visual_elements)} UI elements")
            return visual_elements
            
        except Exception as e:
            print(f"❌ Error detecting UI elements: {e}")
            return []
    
    def _classify_text_element(self, text: str) -> Optional[str]:
        """Classify text element based on content"""
        text_lower = text.lower()
        
        for element_type, pattern_data in self.ui_patterns.items():
            for keyword in pattern_data['keywords']:
                if keyword in text_lower:
                    return element_type
        
        # Additional heuristics
        if len(text) < 3 and text.isalnum():
            return 'label'
        elif '@' in text or 'email' in text_lower:
            return 'input_field'
        elif any(word in text_lower for word in ['click', 'tap', 'press']):
            return 'button'
        
        return None
    
    def _classify_geometric_element(self, aspect_ratio: float, area: float) -> Optional[str]:
        """Classify element based on geometric properties"""
        if 2 < aspect_ratio < 8 and 500 < area < 5000:
            return 'button'
        elif 3 < aspect_ratio < 10 and 300 < area < 3000:
            return 'input_field'
        elif 0.8 < aspect_ratio < 1.2 and 100 < area < 1000:
            return 'checkbox'
        
        return None
    
    def analyze_figma_image(self, file_key: str, node_id: str = None) -> Optional[FigmaImageAnalysis]:
        """
        Comprehensive analysis of Figma image for test case generation
        
        Args:
            file_key: Figma file identifier
            node_id: Specific node to analyze
            
        Returns:
            Complete image analysis results
        """
        try:
            print(f"🎨 Starting Figma image analysis for file: {file_key}")
            
            # Capture screenshots
            node_ids = [node_id] if node_id else None
            image_urls = self.capture_figma_screenshots(file_key, node_ids)
            
            if not image_urls:
                return None
            
            # Process the first available image
            screenshot_url = list(image_urls.values())[0]
            
            # Download and preprocess
            image = self.download_and_preprocess_image(screenshot_url)
            if image is None:
                return None
            
            # Extract text with context
            text_data = self.extract_text_with_context(image)
            
            # Detect UI elements
            visual_elements = self.detect_ui_elements(image, text_data)
            
            # Identify UI patterns
            ui_patterns = self._identify_ui_patterns(visual_elements, text_data)
            
            # Generate test recommendations
            test_recommendations = self._generate_image_based_test_recommendations(
                visual_elements, text_data, ui_patterns
            )
            
            # Calculate quality score
            quality_score = self._calculate_analysis_quality(text_data, visual_elements)
            
            analysis = FigmaImageAnalysis(
                screenshot_url=screenshot_url,
                visual_elements=visual_elements,
                extracted_text=text_data['full_text'],
                ui_patterns=ui_patterns,
                test_recommendations=test_recommendations,
                quality_score=quality_score
            )
            
            print(f"✅ Image analysis complete: {len(visual_elements)} elements, "
                  f"quality: {quality_score:.2f}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error in Figma image analysis: {e}")
            return None
    
    def _identify_ui_patterns(self, visual_elements: List[VisualElement], 
                            text_data: Dict[str, Any]) -> List[str]:
        """Identify UI patterns from visual elements"""
        patterns = []
        element_types = [elem.element_type for elem in visual_elements]
        
        # Form patterns
        if 'input_field' in element_types and 'button' in element_types:
            patterns.append('form_submission')
        
        # Navigation patterns
        if len([e for e in visual_elements if e.element_type == 'navigation']) > 2:
            patterns.append('multi_step_navigation')
        
        # Data entry patterns
        input_count = len([e for e in visual_elements if e.element_type == 'input_field'])
        if input_count > 3:
            patterns.append('complex_form')
        
        # Choice patterns
        if 'checkbox' in element_types or 'dropdown' in element_types:
            patterns.append('user_choice')
        
        return patterns
    
    def _generate_image_based_test_recommendations(self, visual_elements: List[VisualElement],
                                                 text_data: Dict[str, Any], 
                                                 ui_patterns: List[str]) -> List[str]:
        """Generate test recommendations based on image analysis"""
        recommendations = []
        
        # Element-specific recommendations
        for element in visual_elements:
            if element.element_type == 'button':
                recommendations.append(f"Test {element.text_content or 'button'} click functionality")
                recommendations.append(f"Verify {element.text_content or 'button'} hover states")
            
            elif element.element_type == 'input_field':
                recommendations.append(f"Test {element.text_content or 'input field'} with valid data")
                recommendations.append(f"Test {element.text_content or 'input field'} with invalid data")
                recommendations.append(f"Verify {element.text_content or 'input field'} validation messages")
            
            elif element.element_type == 'dropdown':
                recommendations.append(f"Test {element.text_content or 'dropdown'} option selection")
                recommendations.append(f"Verify {element.text_content or 'dropdown'} keyboard navigation")
        
        # Pattern-specific recommendations
        for pattern in ui_patterns:
            if pattern == 'form_submission':
                recommendations.append("Test complete form submission workflow")
                recommendations.append("Test form validation and error handling")
            
            elif pattern == 'multi_step_navigation':
                recommendations.append("Test navigation flow between steps")
                recommendations.append("Test back/forward navigation functionality")
            
            elif pattern == 'complex_form':
                recommendations.append("Test form auto-save functionality")
                recommendations.append("Test form data persistence")
        
        # Text-based recommendations
        if text_data['total_words'] > 10:
            recommendations.append("Test text readability and accessibility")
            recommendations.append("Test text content localization")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _calculate_analysis_quality(self, text_data: Dict[str, Any], 
                                  visual_elements: List[VisualElement]) -> float:
        """Calculate quality score for the analysis"""
        score = 0.0
        
        # Text quality (40% of score)
        text_score = min(1.0, text_data['average_confidence'] / 80.0)
        score += text_score * 0.4
        
        # Element detection quality (40% of score)
        element_score = min(1.0, len(visual_elements) / 10.0)
        score += element_score * 0.4
        
        # Coverage quality (20% of score)
        coverage_score = 1.0 if (text_data['total_words'] > 5 and len(visual_elements) > 2) else 0.5
        score += coverage_score * 0.2
        
        return round(score, 2)
    
    def generate_enhanced_test_context_from_image(self, analysis: FigmaImageAnalysis) -> str:
        """
        Generate enhanced context for test case generation from image analysis
        """
        if not analysis:
            return "Image analysis not available"
        
        context = f"""## FIGMA IMAGE ANALYSIS

**Visual Quality Score:** {analysis.quality_score}/1.0

**Detected UI Elements ({len(analysis.visual_elements)}):**
"""
        
        # Group elements by type
        element_groups = {}
        for element in analysis.visual_elements:
            if element.element_type not in element_groups:
                element_groups[element.element_type] = []
            element_groups[element.element_type].append(element)
        
        for element_type, elements in element_groups.items():
            names = [e.text_content for e in elements if e.text_content]
            context += f"- {element_type}: {len(elements)} found"
            if names:
                context += f" ({', '.join(names[:3])})"
            context += "\n"
        
        context += f"\n**UI Patterns:** {', '.join(analysis.ui_patterns)}\n"
        
        context += f"\n**Extracted Text Content:**\n{analysis.extracted_text[:200]}...\n"
        
        context += f"\n**Image-Based Test Recommendations:**\n"
        for rec in analysis.test_recommendations[:5]:  # Limit to top 5
            context += f"- {rec}\n"
        
        context += "\n**Focus:** Generate test cases that cover visual interactions and UI element behaviors identified from the Figma design.\n"
        
        return context

    def create_visual_test_mapping(self, analysis: FigmaImageAnalysis) -> Dict[str, Any]:
        """
        Create a mapping between visual elements and test cases
        """
        if not analysis:
            return {}
        
        mapping = {
            'visual_elements': [],
            'test_scenarios': [],
            'coverage_matrix': {}
        }
        
        # Map each visual element to test scenarios
        for element in analysis.visual_elements:
            element_data = {
                'element_id': f"{element.element_type}_{hash(element.text_content) % 1000}",
                'type': element.element_type,
                'text': element.text_content,
                'coordinates': element.coordinates,
                'confidence': element.confidence,
                'test_scenarios': []
            }
            
            # Generate specific test scenarios for this element
            if element.element_type == 'button':
                element_data['test_scenarios'] = [
                    f"Verify {element.text_content or 'button'} is clickable",
                    f"Test {element.text_content or 'button'} visual feedback on hover",
                    f"Validate {element.text_content or 'button'} action triggers correctly"
                ]
            
            elif element.element_type == 'input_field':
                element_data['test_scenarios'] = [
                    f"Test {element.text_content or 'input'} accepts valid input",
                    f"Test {element.text_content or 'input'} rejects invalid input",
                    f"Verify {element.text_content or 'input'} placeholder text displays"
                ]
            
            mapping['visual_elements'].append(element_data)
        
        return mapping