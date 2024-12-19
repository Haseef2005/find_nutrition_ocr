from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import io

app = Flask(__name__)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class FindNutrition:
    def __init__(self, image, text: list):
        self.image = image
        self.text = text

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
                        found = True
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
        if not found:
            return {"message": "Nutrition not found, Please check the label by yourself again before you eat."}
        return results

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image_file = request.files['image']
    image = Image.open(io.BytesIO(image_file.read()))
    text_to_find = request.form.getlist('text')

    nutrition_finder = FindNutrition(image, text_to_find)
    results = nutrition_finder.find_text_ocr()

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)