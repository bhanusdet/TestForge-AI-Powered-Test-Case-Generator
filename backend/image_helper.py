"""
Enhanced Image Helper for AI Test Case Generator

Provides comprehensive image processing capabilities including:
- OCR text extraction
- UI element detection  
- Test case context generation
- Figma image analysis integration
"""

from PIL import Image, ImageEnhance
import pytesseract
import cv2
import numpy as np
import os
from typing import Dict, List, Any, Optional

def get_text_from_image(image_path: str) -> Optional[str]:
    """
    Enhanced text extraction from images with better preprocessing
    """
    try:
        # Load and preprocess image
        image = Image.open(image_path)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Enhance image for better OCR
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)
        
        # Configure OCR for better accuracy
        ocr_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?:;-_()[]{}@#$%^&*+=<>/\|~`"\'\ '
        
        # Extract text
        text = pytesseract.image_to_string(image, config=ocr_config)
        
        return text.strip() if text else None
        
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return None

def get_detailed_image_analysis(image_path: str) -> Dict[str, Any]:
    """
    Perform detailed image analysis for test case generation
    """
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise Exception("Could not load image")
        
        # Convert to PIL for OCR
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # Enhanced preprocessing
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(1.2)
        
        # Get OCR data with positions
        ocr_data = pytesseract.image_to_data(
            pil_image,
            output_type=pytesseract.Output.DICT
        )
        
        # Extract text elements with confidence
        text_elements = []
        for i in range(len(ocr_data['text'])):
            text = ocr_data['text'][i].strip()
            if text and int(ocr_data['conf'][i]) > 30:
                text_elements.append({
                    'text': text,
                    'confidence': int(ocr_data['conf'][i]),
                    'x': ocr_data['left'][i],
                    'y': ocr_data['top'][i],
                    'width': ocr_data['width'][i],
                    'height': ocr_data['height'][i]
                })
        
        # Detect UI elements using computer vision
        ui_elements = detect_ui_elements_cv(image, text_elements)
        
        # Generate test insights
        test_insights = generate_image_test_insights(text_elements, ui_elements)
        
        return {
            'text_content': ' '.join([elem['text'] for elem in text_elements]),
            'text_elements': text_elements,
            'ui_elements': ui_elements,
            'test_insights': test_insights,
            'analysis_quality': calculate_image_quality_score(text_elements, ui_elements),
            'recommendations': generate_image_test_recommendations(ui_elements, text_elements)
        }
        
    except Exception as e:
        print(f"❌ Error in detailed image analysis: {e}")
        return {
            'text_content': get_text_from_image(image_path) or '',
            'text_elements': [],
            'ui_elements': [],
            'test_insights': [],
            'analysis_quality': 0.0,
            'recommendations': []
        }

def detect_ui_elements_cv(image: np.ndarray, text_elements: List[Dict]) -> List[Dict]:
    """
    Detect UI elements using computer vision techniques
    """
    ui_elements = []
    
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Find contours (potential UI elements)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 100 < area < 50000:  # Filter reasonable sizes
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # Classify element based on shape
                element_type = classify_ui_element(aspect_ratio, area, text_elements, x, y, w, h)
                
                if element_type:
                    ui_elements.append({
                        'type': element_type,
                        'coordinates': (x, y, w, h),
                        'area': area,
                        'aspect_ratio': aspect_ratio,
                        'confidence': 0.7
                    })
        
        return ui_elements
        
    except Exception as e:
        print(f"❌ Error detecting UI elements: {e}")
        return []

def classify_ui_element(aspect_ratio: float, area: float, text_elements: List[Dict],
                       x: int, y: int, w: int, h: int) -> Optional[str]:
    """
    Classify UI element based on geometric and textual properties
    """
    # Check if there's text in this region
    overlapping_text = []
    for text_elem in text_elements:
        if (text_elem['x'] >= x and text_elem['x'] + text_elem['width'] <= x + w and
            text_elem['y'] >= y and text_elem['y'] + text_elem['height'] <= y + h):
            overlapping_text.append(text_elem['text'].lower())
    
    combined_text = ' '.join(overlapping_text)
    
    # Button detection
    if 2 < aspect_ratio < 8 and 500 < area < 5000:
        button_keywords = ['button', 'click', 'submit', 'save', 'cancel', 'ok', 'login', 'sign']
        if any(keyword in combined_text for keyword in button_keywords):
            return 'button'
        if len(combined_text.split()) <= 3 and combined_text:  # Short text likely button
            return 'button'
    
    # Input field detection
    if 3 < aspect_ratio < 10 and 300 < area < 3000:
        input_keywords = ['input', 'enter', 'search', 'email', 'password', 'name']
        if any(keyword in combined_text for keyword in input_keywords):
            return 'input_field'
        if not combined_text:  # Empty rectangle likely input field
            return 'input_field'
    
    # Checkbox detection
    if 0.8 < aspect_ratio < 1.2 and 100 < area < 1000:
        checkbox_keywords = ['check', 'agree', 'accept', 'terms']
        if any(keyword in combined_text for keyword in checkbox_keywords):
            return 'checkbox'
    
    return None

def generate_image_test_insights(text_elements: List[Dict], ui_elements: List[Dict]) -> List[str]:
    """
    Generate test insights based on image analysis
    """
    insights = []
    
    # Text-based insights
    if text_elements:
        total_confidence = sum(elem['confidence'] for elem in text_elements)
        avg_confidence = total_confidence / len(text_elements)
        
        if avg_confidence > 80:
            insights.append("High text recognition quality - reliable for automated testing")
        elif avg_confidence > 60:
            insights.append("Moderate text recognition - may need manual verification")
        else:
            insights.append("Low text recognition - consider image quality improvements")
    
    # UI element insights
    button_count = len([elem for elem in ui_elements if elem['type'] == 'button'])
    input_count = len([elem for elem in ui_elements if elem['type'] == 'input_field'])
    
    if button_count > 0 and input_count > 0:
        insights.append("Form interface detected - test form submission workflows")
    
    if button_count > 3:
        insights.append("Multiple buttons detected - test button interaction sequences")
    
    if input_count > 2:
        insights.append("Multiple input fields - test data validation and field interactions")
    
    return insights

def generate_image_test_recommendations(ui_elements: List[Dict], text_elements: List[Dict]) -> List[str]:
    """
    Generate specific test recommendations based on detected elements
    """
    recommendations = []
    
    # Element-specific recommendations
    for element in ui_elements:
        if element['type'] == 'button':
            recommendations.append(f"Test button click functionality at coordinates ({element['coordinates'][0]}, {element['coordinates'][1]})")
            recommendations.append(f"Verify button hover and focus states")
        
        elif element['type'] == 'input_field':
            recommendations.append(f"Test input field with valid data")
            recommendations.append(f"Test input field with invalid data")
            recommendations.append(f"Verify input field validation messages")
        
        elif element['type'] == 'checkbox':
            recommendations.append(f"Test checkbox selection and deselection")
            recommendations.append(f"Verify checkbox state persistence")
    
    # Pattern-based recommendations
    if len(ui_elements) > 1:
        recommendations.append("Test element interaction sequences")
        recommendations.append("Verify responsive behavior across different screen sizes")
    
    return recommendations

def calculate_image_quality_score(text_elements: List[Dict], ui_elements: List[Dict]) -> float:
    """
    Calculate overall quality score for image analysis
    """
    score = 0.0
    
    # Text quality (50% of score)
    if text_elements:
        avg_confidence = sum(elem['confidence'] for elem in text_elements) / len(text_elements)
        score += (avg_confidence / 100.0) * 0.5
    
    # Element detection quality (30% of score)
    element_score = min(1.0, len(ui_elements) / 5.0)  # Max score with 5+ elements
    score += element_score * 0.3
    
    # Coverage quality (20% of score)
    coverage_score = 1.0 if (len(text_elements) > 3 and len(ui_elements) > 1) else 0.5
    score += coverage_score * 0.2
    
    return round(score, 2)

def create_image_test_context(image_analysis: Dict[str, Any], max_length: int = 1000) -> str:
    """
    Create compressed test context from image analysis
    """
    if not image_analysis:
        return "Image analysis not available"
    
    context = f"## IMAGE ANALYSIS\n\n"
    context += f"**Quality Score:** {image_analysis.get('analysis_quality', 0.0)}/1.0\n\n"
    
    # UI Elements summary
    ui_elements = image_analysis.get('ui_elements', [])
    if ui_elements:
        element_types = {}
        for elem in ui_elements:
            elem_type = elem['type']
            element_types[elem_type] = element_types.get(elem_type, 0) + 1
        
        context += "**UI Elements Detected:**\n"
        for elem_type, count in element_types.items():
            context += f"- {elem_type}: {count}\n"
        context += "\n"
    
    # Text content (limited)
    text_content = image_analysis.get('text_content', '')
    if text_content:
        context += f"**Text Content:** {text_content[:200]}...\n\n"
    
    # Top recommendations
    recommendations = image_analysis.get('recommendations', [])
    if recommendations:
        context += "**Test Recommendations:**\n"
        for rec in recommendations[:3]:  # Limit to top 3
            context += f"- {rec}\n"
    
    # Truncate if too long
    if len(context) > max_length:
        context = context[:max_length-50] + "...\n[Truncated for size limit]\n"
    
    return context