from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import io

app = Flask(__name__)

pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\tesseract.exe'

class FindNutrition:
    def __init__(self, image, text: list):
        self.image = image
        self.text = text

    def plain_text_ocr(self):
        text_ocr = pytesseract.image_to_string(self.image)
        return text_ocr

    def find_text_ocr(self):
        found = False
        data = pytesseract.image_to_data(self.image, output_type=pytesseract.Output.DICT)
        results = []
        for i, word in enumerate(data['text']):
            if word.strip():  # Filter out empty results
                for j in self.text:
                    j = j.lower()
                    word = word.lower()
                    if j in word:
                        results.append({
                            "word": word,
                            "confidence": data['conf'][i],
                            "bounding_box": {
                                "left": data['left'][i],
                                "top": data['top'][i],
                                "width": data['width'][i],
                                "height": data['height'][i]
                            }
                        })
                        found = True
        return results if found else "No matching text found."

@app.route('/plain_text_ocr', methods=['POST'])
def plain_text_ocr():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    image_file = request.files['image']
    image = Image.open(io.BytesIO(image_file.read()))
    ocr = FindNutrition(image, [])
    text_ocr = ocr.plain_text_ocr()
    return jsonify({"text": text_ocr})

@app.route('/find_text_ocr', methods=['POST'])
def find_text_ocr():
    if 'image' not in request.files or 'text' not in request.json:
        return jsonify({"error": "Image file or text not provided"}), 400
    image_file = request.files['image']
    text_list = request.json['text']
    image = Image.open(io.BytesIO(image_file.read()))
    ocr = FindNutrition(image, text_list)
    results = ocr.find_text_ocr()
    return jsonify({"results": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)