
from PIL import Image
import pytesseract

def get_text_from_image(image_path):
    try:
        return pytesseract.image_to_string(Image.open(image_path))
    except Exception as e:
        print(f"Error processing image: {e}")
        return None