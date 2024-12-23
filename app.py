from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
from ultralyticsplus import YOLO

app = Flask(__name__)

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# Load the YOLO model for table detection
model = YOLO('foduucom/table-detection-and-extraction')

class FindNutrition:
    def __init__(self, image, text: list):
        self.image = image
        self.text = text

    def detect_tables(self):
        # Perform table detection
        results = model.predict(self.image)
        return results[0].boxes

    def crop_table(self, box):
        # Extract the bounding box coordinates and convert to integers
        left, top, right, bottom = map(int, box.xyxy[0])
        return self.image.crop((left, top, right, bottom))

    def ocr(self, image):
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
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

    def plain_text_ocr(self, image):
        return pytesseract.image_to_string(image)

    def find_text_ocr(self, image):
        found_text = []
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
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

    # Detect tables
    tables = nutrition_finder.detect_tables()

    # Perform OCR on each detected table or on the whole image if no tables are detected
    ocr_results = []
    if not tables:
        ocr_data = nutrition_finder.ocr(image)
        ocr_results.extend(ocr_data)
    else:
        for table in tables:
            cropped_table = nutrition_finder.crop_table(table)
            ocr_data = nutrition_finder.ocr(cropped_table)
            ocr_results.extend(ocr_data)

    # Convert results to lowercase and return as a set
    ocr_results = [l['word'].lower() for l in ocr_results if 'word' in l]
    results = set(ocr_results)

    return jsonify({"ocr_data": list(results)})

@app.route('/plain_text', methods=['POST'])
def plain_text():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    image_file = request.files['image']

    # Convert uploaded image to PIL format
    image = Image.open(image_file)

    # Initialize the OCR class
    nutrition_finder = FindNutrition(image, [])

    # Detect tables
    tables = nutrition_finder.detect_tables()

    # Get plain text OCR for each detected table or for the whole image if no tables are detected
    plain_text_results = []
    if not tables:
        text = nutrition_finder.plain_text_ocr(image)
        plain_text_results.append(text)
    else:
        for table in tables:
            cropped_table = nutrition_finder.crop_table(table)
            text = nutrition_finder.plain_text_ocr(cropped_table)
            plain_text_results.append(text)

    return jsonify({"plain_text": plain_text_results})

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

    # Detect tables
    tables = nutrition_finder.detect_tables()

    # Search for specific text in each detected table or in the whole image if no tables are detected
    found_text_results = []
    if not tables:
        found_text = nutrition_finder.find_text_ocr(image)
        found_text_results.extend(found_text)
    else:
        for table in tables:
            cropped_table = nutrition_finder.crop_table(table)
            found_text = nutrition_finder.find_text_ocr(cropped_table)
            found_text_results.extend(found_text)

    # Convert results to lowercase and return as a set
    found_text_results = [l['word'].lower() for l in found_text_results if 'word' in l]
    results = set(found_text_results)

    if not results:
        return jsonify({"message": "Nutrition not found. Please check the label manually before eating."}), 404

    return jsonify({"found_text": list(results)})

# Run the app (if not in Docker, use this line for debugging)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)