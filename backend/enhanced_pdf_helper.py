import warnings
# Suppress PDF processing warnings
warnings.filterwarnings('ignore', category=UserWarning, module='pdfminer')
warnings.filterwarnings('ignore', message='.*FontBBox.*')
warnings.filterwarnings('ignore', message='.*DataFrame columns are not unique.*')

import pdfplumber
import pandas as pd
import logging
import tempfile
import os
from typing import Dict, List, Optional, Union
import re

# Suppress pandas warnings
pd.options.mode.chained_assignment = None

# Optional dependencies - gracefully handle if not available
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("⚠️ PyMuPDF not available - advanced PDF processing disabled")

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️ Tesseract/PIL not available - OCR processing disabled")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedPDFProcessor:
    """
    🚀 Enhanced PDF processing with multiple extraction methods
    - Text extraction with fallback options
    - OCR for scanned documents  
    - Table extraction and parsing
    - Image extraction and OCR
    - Structured content organization
    """
    
    def __init__(self):
        self.supported_formats = ['.pdf']
        self.ocr_languages = 'eng'  # Add hindi: 'eng+hin'
        
    def extract_comprehensive_content(self, pdf_path: str) -> Dict[str, Union[str, List, Dict]]:
        """
        Extract all possible content from PDF
        Returns structured data with text, tables, images, metadata
        """
        result = {
            'text_content': '',
            'tables': [],
            'images_text': [],
            'metadata': {},
            'structured_sections': [],
            'extraction_method': [],
            'quality_score': 0.0
        }
        
        try:
            # Method 1: PDFPlumber (best for text + tables)
            plumber_result = self._extract_with_pdfplumber(pdf_path)
            
            # Method 2: PyMuPDF (best for complex layouts + images) - Optional
            if PYMUPDF_AVAILABLE:
                try:
                    pymupdf_result = self._extract_with_pymupdf(pdf_path)
                except Exception as e:
                    logger.warning(f"PyMuPDF extraction failed: {e}")
                    pymupdf_result = {'text_content': '', 'images_text': [], 'method': 'pymupdf_failed'}
            else:
                pymupdf_result = {'text_content': '', 'images_text': [], 'method': 'pymupdf_unavailable'}
            
            # Method 3: OCR fallback for scanned PDFs - Optional
            if OCR_AVAILABLE:
                try:
                    ocr_result = self._extract_with_ocr_if_needed(pdf_path, plumber_result['text_content'])
                except Exception as e:
                    logger.warning(f"OCR processing failed: {e}")
                    ocr_result = {'text_content': '', 'method': 'ocr_failed', 'was_needed': False}
            else:
                ocr_result = {'text_content': '', 'method': 'ocr_unavailable', 'was_needed': False}
            
            # Combine results intelligently
            result = self._combine_extraction_results(plumber_result, pymupdf_result, ocr_result)
            
            # Post-process and structure content
            result = self._post_process_content(result)
            
            logger.info(f"✅ PDF processing complete: {len(result['text_content'])} chars, "
                       f"{len(result['tables'])} tables, {len(result['images_text'])} images")
            
        except Exception as e:
            logger.error(f"❌ PDF processing failed: {e}")
            result['text_content'] = f"Error processing PDF: {str(e)}"
            
        return result
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Dict:
        """Extract using pdfplumber (excellent for tables and clean text)"""
        result = {
            'text_content': '',
            'tables': [],
            'metadata': {},
            'page_count': 0,
            'method': 'pdfplumber'
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                result['metadata'] = pdf.metadata or {}
                result['page_count'] = len(pdf.pages)
                
                all_text = []
                all_tables = []
                
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text
                    page_text = page.extract_text()
                    if page_text:
                        all_text.append(f"\n--- Page {page_num} ---\n{page_text}")
                    
                    # Extract tables
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables):
                        if table:
                            # Convert to DataFrame for better processing
                            try:
                                df = pd.DataFrame(table[1:], columns=table[0])  # First row as header
                                table_text = f"\n=== Table {table_idx+1} (Page {page_num}) ===\n{df.to_string()}\n"
                                all_tables.append({
                                    'page': page_num,
                                    'table_index': table_idx,
                                    'content': df.to_dict('records'),
                                    'text_representation': table_text
                                })
                            except:
                                # Fallback: simple text representation
                                table_text = f"\n=== Table {table_idx+1} (Page {page_num}) ===\n"
                                for row in table:
                                    table_text += " | ".join(str(cell) for cell in row if cell) + "\n"
                                all_tables.append({
                                    'page': page_num,
                                    'table_index': table_idx,
                                    'content': table,
                                    'text_representation': table_text
                                })
                
                result['text_content'] = '\n'.join(all_text)
                result['tables'] = all_tables
                
        except Exception as e:
            logger.error(f"PDFPlumber extraction failed: {e}")
            
        return result
    
    def _extract_with_pymupdf(self, pdf_path: str) -> Dict:
        """Extract using PyMuPDF (excellent for images and complex layouts)"""
        result = {
            'text_content': '',
            'images_text': [],
            'structured_sections': [],
            'method': 'pymupdf'
        }
        
        if not PYMUPDF_AVAILABLE:
            logger.warning("PyMuPDF not available")
            return result
        
        try:
            doc = fitz.open(pdf_path)
            all_text = []
            all_images_text = []
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Extract text with formatting info
                text = page.get_text()
                if text.strip():
                    all_text.append(f"\n--- Page {page_num + 1} (PyMuPDF) ---\n{text}")
                
                # Extract images and perform OCR
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    try:
                        # Get image data
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            # Convert to PIL Image
                            img_data = pix.tobytes("ppm")
                            pil_image = Image.open(fitz.io.BytesIO(img_data))
                            
                            # OCR on image
                            ocr_text = pytesseract.image_to_string(pil_image, lang=self.ocr_languages)
                            if ocr_text.strip():
                                all_images_text.append({
                                    'page': page_num + 1,
                                    'image_index': img_index,
                                    'ocr_text': ocr_text.strip(),
                                    'formatted': f"\n=== Image {img_index+1} (Page {page_num+1}) OCR ===\n{ocr_text.strip()}\n"
                                })
                        
                        pix = None  # Free memory
                        
                    except Exception as img_error:
                        logger.warning(f"Image extraction failed on page {page_num+1}, image {img_index}: {img_error}")
            
            result['text_content'] = '\n'.join(all_text)
            result['images_text'] = all_images_text
            doc.close()
            
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {e}")
            
        return result
    
    def _extract_with_ocr_if_needed(self, pdf_path: str, existing_text: str) -> Dict:
        """Perform OCR if extracted text is insufficient"""
        result = {
            'text_content': '',
            'method': 'ocr',
            'was_needed': False
        }
        
        if not OCR_AVAILABLE or not PYMUPDF_AVAILABLE:
            logger.warning("OCR or PyMuPDF not available for OCR processing")
            return result
        
        # Check if OCR is needed (very little text extracted)
        if len(existing_text.strip()) < 100:  # Less than 100 chars suggests scanned PDF
            logger.info("🔍 Low text content detected, performing OCR...")
            result['was_needed'] = True
            
            try:
                doc = fitz.open(pdf_path)
                ocr_pages = []
                
                for page_num in range(min(doc.page_count, 10)):  # Limit to first 10 pages for cost control
                    page = doc[page_num]
                    
                    # Convert page to image
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x resolution for better OCR
                    img_data = pix.tobytes("ppm")
                    pil_image = Image.open(fitz.io.BytesIO(img_data))
                    
                    # OCR
                    ocr_text = pytesseract.image_to_string(pil_image, lang=self.ocr_languages)
                    if ocr_text.strip():
                        ocr_pages.append(f"\n--- Page {page_num + 1} (OCR) ---\n{ocr_text}")
                    
                    pix = None  # Free memory
                
                result['text_content'] = '\n'.join(ocr_pages)
                doc.close()
                
                logger.info(f"✅ OCR completed: {len(result['text_content'])} characters extracted")
                
            except Exception as e:
                logger.error(f"OCR processing failed: {e}")
                result['text_content'] = f"OCR failed: {str(e)}"
        
        return result
    
    def _combine_extraction_results(self, plumber_result: Dict, pymupdf_result: Dict, ocr_result: Dict) -> Dict:
        """Intelligently combine results from different extraction methods"""
        combined = {
            'text_content': '',
            'tables': plumber_result.get('tables', []),
            'images_text': pymupdf_result.get('images_text', []),
            'metadata': plumber_result.get('metadata', {}),
            'structured_sections': [],
            'extraction_method': [],
            'quality_score': 0.0
        }
        
        # Choose best text extraction
        plumber_text = plumber_result.get('text_content', '')
        pymupdf_text = pymupdf_result.get('text_content', '')
        ocr_text = ocr_result.get('text_content', '')
        
        text_parts = []
        
        if len(plumber_text) > 100:  # PDFPlumber got good text
            text_parts.append("=== MAIN CONTENT ===")
            text_parts.append(plumber_text)
            combined['extraction_method'].append('pdfplumber')
            combined['quality_score'] += 0.4
            
        elif len(pymupdf_text) > 100:  # PyMuPDF as fallback
            text_parts.append("=== MAIN CONTENT (PyMuPDF) ===")
            text_parts.append(pymupdf_text)
            combined['extraction_method'].append('pymupdf')
            combined['quality_score'] += 0.3
            
        if ocr_result.get('was_needed') and len(ocr_text) > 50:  # OCR was used
            text_parts.append("=== OCR CONTENT ===")
            text_parts.append(ocr_text)
            combined['extraction_method'].append('ocr')
            combined['quality_score'] += 0.2
        
        # Add tables as text
        if combined['tables']:
            text_parts.append("=== EXTRACTED TABLES ===")
            for table in combined['tables']:
                text_parts.append(table['text_representation'])
            combined['quality_score'] += 0.3
        
        # Add image OCR text
        if combined['images_text']:
            text_parts.append("=== IMAGE OCR CONTENT ===")
            for img_text in combined['images_text']:
                text_parts.append(img_text['formatted'])
            combined['quality_score'] += 0.2
        
        combined['text_content'] = '\n\n'.join(text_parts)
        combined['quality_score'] = min(1.0, combined['quality_score'])  # Cap at 1.0
        
        return combined
    
    def _post_process_content(self, result: Dict) -> Dict:
        """Clean and structure the extracted content"""
        text = result['text_content']
        
        if not text:
            return result
        
        # Clean up text
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Structure content into sections
        sections = []
        current_section = ""
        
        for line in text.split('\n'):
            if line.strip().startswith('---') or line.strip().startswith('==='):
                if current_section.strip():
                    sections.append(current_section.strip())
                current_section = line + '\n'
            else:
                current_section += line + '\n'
        
        if current_section.strip():
            sections.append(current_section.strip())
        
        result['structured_sections'] = sections
        result['text_content'] = text
        
        return result

# Updated main function for backward compatibility
def get_text_from_pdf(filepath: str) -> str:
    """
    Enhanced PDF text extraction with multiple methods
    Backward compatible with existing code
    """
    processor = EnhancedPDFProcessor()
    result = processor.extract_comprehensive_content(filepath)
    
    # Return just the text for backward compatibility
    text_content = result.get('text_content', '')
    
    # Add summary of extraction quality
    quality_score = result.get('quality_score', 0.0)
    methods_used = ', '.join(result.get('extraction_method', ['unknown']))
    
    if text_content:
        summary = f"\n--- EXTRACTION SUMMARY ---\n"
        summary += f"Quality Score: {quality_score:.2f}/1.0\n"
        summary += f"Methods Used: {methods_used}\n"
        summary += f"Tables Found: {len(result.get('tables', []))}\n"
        summary += f"Images with Text: {len(result.get('images_text', []))}\n"
        summary += f"Total Characters: {len(text_content)}\n"
        summary += "--- END SUMMARY ---\n\n"
        
        return summary + text_content
    
    return text_content

# New function for detailed extraction
def get_detailed_pdf_content(filepath: str) -> Dict:
    """
    Get detailed PDF content with all extracted elements
    Use this for advanced processing
    """
    processor = EnhancedPDFProcessor()
    return processor.extract_comprehensive_content(filepath)