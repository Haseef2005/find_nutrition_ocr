from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import io

app = Flask(__name__)

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

class FindNutrition:
    def __init__(self, image, text: list):
        self.image = image
        self.text = text

    def ocr(self):
        data = pytesseract.image_to_data(self.image, output_type=pytesseract.Output.DICT)
        result = []
        for i, word in enumerate(data['text']):
            if word.strip():  # Filter out empty results
                result.append({
                    "word": word,
                    "confidence": data['conf'][i],
                    "bounding_box": {
                        "left": data['left'][i],
                        "top": data['top'][i],
                        "width": data['width'][i],
                        "height": data['height'][i]
                    }
                })
        return result

    def plain_text_ocr(self):
        return pytesseract.image_to_string(self.image)

    def find_text_ocr(self):
        found_text = []
        data = pytesseract.image_to_data(self.image, output_type=pytesseract.Output.DICT)
        for i, word in enumerate(data['text']):
            if word.strip():  # Filter out empty results
                for j in self.text:
                    if j.lower() in word.lower():
                        found_text.append({
                            "word": word,
                            "confidence": data['conf'][i],
                            "bounding_box": {
                                "left": data['left'][i],
                                "top": data['top'][i],
                                "width": data['width'][i],
                                "height": data['height'][i]
                            }
                        })
        return found_text


@app.route('/ocr', methods=['POST'])
def ocr():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    image_file = request.files['image']
    text_to_find = request.form.getlist('text')

    # Convert uploaded image to PIL format
    image = Image.open(image_file)

    # Initialize the OCR class
    nutrition_finder = FindNutrition(image, text_to_find)

    # Perform OCR
    ocr_data = nutrition_finder.ocr()

    return jsonify({"ocr_data": ocr_data})


@app.route('/find_text', methods=['POST'])
def find_text():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    image_file = request.files['image']
    text_to_find = request.form.getlist('text')

    # Convert uploaded image to PIL format
    image = Image.open(image_file)

    # Initialize the OCR class
    nutrition_finder = FindNutrition(image, text_to_find)

    # Search for specific text
    found_text = nutrition_finder.find_text_ocr()

    if not found_text:
        return jsonify({"message": "Nutrition not found. Please check the label manually before eating."}), 404

    return jsonify({"found_text": found_text})


@app.route('/plain_text', methods=['POST'])
def plain_text():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    image_file = request.files['image']

    # Convert uploaded image to PIL format
    image = Image.open(image_file)

    # Initialize the OCR class
    nutrition_finder = FindNutrition(image, [])

    # Get plain text OCR
    text = nutrition_finder.plain_text_ocr()

    return jsonify({"plain_text": text})


# Run the app (if not in Docker, use this line for debugging)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)