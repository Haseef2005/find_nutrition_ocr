from PIL import Image
from PIL import ImageOps
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class find_nutrition:
    def __init__(self, image, text: list):
        self.image = image
        self.text = text

        
    def ocr(self):
        data = pytesseract.image_to_data(self.image, output_type=pytesseract.Output.DICT)
        for i, word in enumerate(data['text']):
            if word.strip():  # Filter out empty results
                print(f"Word: {word}, Confidence: {data['conf'][i]}, Bounding Box: {data['left'][i]}, {data['top'][i]}, {data['width'][i]}, {data['height'][i]}")


    def plain_text_ocr(self):
        text_ocr = pytesseract.image_to_string(self.image)
        print(text_ocr)


    def find_text_ocr(self):
        found = False
        data = pytesseract.image_to_data(self.image, output_type=pytesseract.Output.DICT)
        for i, word in enumerate(data['text']):
            if word.strip():  # Filter out empty results
                for j in self.text:
                    j = j.lower()
                    word = word.lower()
                    if j in word:
                        found = True
                        print(f"Word: {word}, Confidence: {data['conf'][i]}, Bounding Box: {data['left'][i]}, {data['top'][i]}, {data['width'][i]}, {data['height'][i]}")
        if not found:
            print("Nutrition not found, Please check the label by yourself again before you eat.")