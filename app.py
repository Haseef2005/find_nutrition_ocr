from flask import Flask, request, jsonify
from PIL import Image, UnidentifiedImageError
import pytesseract
from ultralyticsplus import YOLO
import base64
from io import BytesIO
import requests

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

    def extract_nutritional_content(self, ocr_results):
        keywords = [
            # Macronutrients
            'dietary fiber', 'sugars', 'soluble fiber', 'insoluble fiber',
            'monounsaturated fat', 'polyunsaturated fat', 'trans fat',
            'saturated fat', 'total fat', 'total carbohydrate', 'protein',
            'total calories', 'calories from fat', 'fat',

            # Vitamins
            'vitamin a', 'vitamin c', 'vitamin d', 'vitamin e',
            'vitamin k', 'vitamin b6', 'vitamin b12',
            'thiamin', 'riboflavin', 'niacin', 'folic acid', 'folate',
            'biotin', 'pantothenic acid',

            # Minerals
            'calcium', 'iron', 'magnesium', 'potassium',
            'sodium', 'zinc', 'phosphorus', 'copper', 'manganese',
            'selenium', 'iodine', 'chromium', 'molybdenum',

            # Other Nutrition Components
            'cholesterol', 'added sugars', 'sugar alcohols',
            'omega-3 fatty acids', 'omega-6 fatty acids',
            'other carbohydrate', 'alcohol', 'total sugars', 'dietary fiber',

            # Common Ingredients
            'milk', 'eggs', 'fish', 'shellfish', 'tree nuts',
            'peanuts', 'wheat', 'soy', 'gluten', 'sesame', 'corn',
            'rice', 'yeast', 'flour', 'sugar', 'salt', 'oil',
            'butter', 'cream', 'honey', 'vinegar', 'cheese',
            'yogurt', 'gelatin', 'beef', 'pork', 'chicken', 'lamb',

            # Additives and Flavorings
            'artificial flavors', 'natural flavors', 'preservatives',
            'coloring', 'emulsifiers', 'stabilizers', 'additives',
            'sweeteners', 'lecithin', 'sorbitol', 'maltodextrin',
            'xanthan gum', 'agar', 'pectin', 'caramel color',

            # Spices and Herbs
            'cinnamon', 'basil', 'oregano', 'parsley', 'pepper',
            'turmeric', 'ginger', 'garlic', 'onion', 'coriander',
            'paprika', 'cardamom', 'clove', 'nutmeg', 'bay leaf',

            # Serving Information
            'serving size', 'servings per container', 'daily value',
            'percent daily value', 'calories per serving',

            # Labels (for Identification)
            'non-gmo', 'organic', 'vegan', 'kosher', 'halal', 'gluten-free',
            'low fat', 'low sodium', 'sugar-free', 'no added sugar',

            # Common Allergens
            'milk', 'eggs', 'fish', 'shellfish', 'tree nuts',
            'peanuts', 'wheat', 'soy', 'gluten', 'sesame',

            # Specific Tree Nuts
            'almonds', 'cashews', 'walnuts', 'pecans',
            'hazelnuts', 'pistachios', 'macadamia nuts',

            # Shellfish and Seafood
            'shrimp', 'crab', 'lobster', 'oysters', 'scallops',
            'mussels', 'squid', 'clams', 'anchovies', 'cod',
            'salmon', 'tuna', 'sardines', 'trout', 'haddock',

            # Dairy Products
            'butter', 'cream', 'cheese', 'yogurt', 'whey', 'casein',
            'lactose', 'milk powder', 'skim milk', 'whole milk',

            # Grains (Potential Allergens)
            'wheat', 'barley', 'rye', 'oats', 'corn', 'rice',
            'buckwheat', 'spelt', 'quinoa', 'millet', 'amaranth',

            # Soy Products
            'soybeans', 'soy milk', 'tofu', 'soy sauce', 'edamame',
            'soy protein', 'soy lecithin',

            # Food Additives
            'artificial flavors', 'natural flavors', 'preservatives',
            'coloring', 'stabilizers', 'emulsifiers', 'sweeteners',
            'lecithin', 'sorbitol', 'xanthan gum', 'maltodextrin',
            'carrageenan', 'gelatin', 'pectin', 'aspartame',
            'sucralose', 'acesulfame potassium',

            # Common Oils and Fats
            'vegetable oil', 'palm oil', 'canola oil', 'soybean oil',
            'olive oil', 'coconut oil', 'sunflower oil', 'butter',

            # Sweeteners and Sugars
            'sugar', 'high fructose corn syrup', 'honey', 'agave',
            'maple syrup', 'molasses', 'brown sugar', 'cane sugar',
            'invert sugar', 'glucose', 'fructose', 'lactose',
            'maltose', 'dextrose', 'sucrose',

            # Eggs and Egg Products
            'whole egg', 'egg whites', 'egg yolks', 'powdered egg',

            # Meat and Meat Byproducts
            'beef', 'pork', 'chicken', 'turkey', 'lamb',
            'gelatin', 'broth', 'stock', 'sausage', 'bacon',

            # Spices and Seasonings
            'salt', 'pepper', 'garlic', 'onion', 'cinnamon',
            'nutmeg', 'clove', 'paprika', 'cumin', 'turmeric',
            'oregano', 'basil', 'parsley', 'thyme', 'chili',

            # Legumes (Potential Allergens)
            'lentils', 'chickpeas', 'peas', 'black beans',
            'kidney beans', 'pinto beans', 'lupin',

            # Seeds
            'sesame', 'sunflower seeds', 'pumpkin seeds', 'chia seeds',
            'flaxseeds', 'hemp seeds', 'poppy seeds',

            # Miscellaneous Ingredients
            'yeast', 'vinegar', 'cocoa', 'chocolate', 'coffee',
            'tea', 'mushrooms', 'lemon', 'lime', 'apple',
            'banana', 'strawberry', 'blueberry', 'orange',

            # Gluten-Free Alternatives
            'corn starch', 'potato starch', 'tapioca', 'arrowroot',
            'almond flour', 'coconut flour'
        ]

        nutritional_content = set()
        for word in ocr_results:
            word_lower = word['word'].lower()
            if any(keyword in word_lower for keyword in keywords):
                nutritional_content.add(word['word'])
        return nutritional_content
def final_info(image_data_base64, user_id, allergy: list):
    # Decode base64 image
    try:
        image = Image.open(BytesIO(base64.b64decode(image_data_base64)))
    except (base64.binascii.Error, UnidentifiedImageError) as e:
        return {"error": "Invalid image data"}

    # Initialize the OCR class
    nutrition_finder = FindNutrition(image, [])

    # Get plain text OCR results
    ocr_results = nutrition_finder.ocr(image)

    # Extract nutritional content
    nutritional_content = nutrition_finder.extract_nutritional_content(ocr_results)

    # Prepare the payload for the allergy API
    payload = {
        "ingredients": ["Egg", "Coconut milk"]  # Replace with actual ingredients if needed
    }

    # Make a request to the other API to get allergy information
    allergy_api_url = "https://recommend-api-production.up.railway.app/allergy/ingredient"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(allergy_api_url, json=payload, headers=headers)
    if response.status_code != 200:
        return {"error": "Failed to fetch allergy information"}

    allergy_info = response.json()

    # Make a request to the other API to get option
    pop_option = "https://recommend-api-production.up.railway.app/recommend/popularity"  # Replace with the actual URL of the other API
    response = requests.get(pop_option)
    if response.status_code != 200:
        return {"error": "Failed to fetch pop option information"}

    pop_option_info = response.json()

    # Check for common allergens
    warning = False
    allergens = {allergen.lower() for allergen in allergy_info.get("allergy", [])}
    user_allergens = {allergen.lower() for allergen in allergy}
    common_allergens = allergens.intersection(user_allergens)
    if common_allergens:
        warning = True

    # Combine the results
    final_result = {
        "user_id": user_id,
        "allergy": allergy,
        "warning": warning,
        "allergy_info": allergy_info.get("allergy", []),
        "best_restaurant": pop_option_info.get("best_restaurant", []),
        "nutritional_content": list(nutritional_content)
    }
    return final_result

@app.route('/final_info', methods=['POST'])
def final_info_endpoint():
    data = request.json
    if 'image' not in data or 'user_id' not in data or 'allergy' not in data:
        return jsonify({"error": "Missing required parameters"}), 400

    image_data_base64 = data['image']
    user_id = data['user_id']
    allergy = data['allergy']

    result = final_info(image_data_base64, user_id, allergy)
    return jsonify(result)

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'image' not in request.json:
        return jsonify({"error": "No image file provided"}), 400
    image_data = request.json['image']
    text_to_find = request.json.get('text', [])

    # Decode base64 image
    image = Image.open(BytesIO(base64.b64decode(image_data)))

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
    if 'image' not in request.json:
        return jsonify({"error": "No image file provided"}), 400
    image_data = request.json['image']

    # Decode base64 image
    image = Image.open(BytesIO(base64.b64decode(image_data)))

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
    if 'image' not in request.json:
        return jsonify({"error": "No image file provided"}), 400
    image_data = request.json['image']
    text_to_find = request.json.get('text', [])

    # Decode base64 image
    image = Image.open(BytesIO(base64.b64decode(image_data)))

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

@app.route('/extract_nutritional_content', methods=['POST'])
def extract_nutritional_content():
    if 'image' not in request.json:
        return jsonify({"error": "No image file provided"}), 400
    image_data = request.json['image']

    # Decode base64 image
    image = Image.open(BytesIO(base64.b64decode(image_data.split)))

    # Initialize the OCR class
    nutrition_finder = FindNutrition(image, [])

    # Get plain text OCR results
    ocr_results = nutrition_finder.ocr(image)

    # Extract nutritional content
    nutritional_content = nutrition_finder.extract_nutritional_content(ocr_results)

    return jsonify({"nutritional_content": list(nutritional_content)})

# Run the app (if not in Docker, use this line for debugging)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)

