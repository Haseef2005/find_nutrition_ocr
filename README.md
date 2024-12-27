# Find Nutrition OCR

This project uses Optical Character Recognition (OCR) to detect and extract nutritional information from images of food labels. It leverages Tesseract OCR and a YOLO model for table detection to accurately identify and extract text from images.

## Project Structure

- `app.py`: The main Flask application file that handles the API endpoints.
- `Dockerfile`: The Dockerfile used to build the Docker image for the application.
- `images/`: Directory containing sample images for testing.
- `main.ipynb`: Jupyter notebook for testing the OCR and table detection functionality.
- `ocr.ipynb`: Jupyter notebook for testing the OCR functionality.
- `Procfile`: Configuration file for running the application with Gunicorn.
- `README.md`: This file.
- `render.yaml`: Configuration file for deploying the application on Render.
- `requirements.txt`: List of Python dependencies required for the project.
- `table_detection.ipynb`: Jupyter notebook for testing the table detection functionality.

## Requirements

- Python 3.12.8
- Docker
- Google Cloud SDK (for deployment on Google Cloud Run)

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/find-nutrition-ocr.git
    cd find-nutrition-ocr
    ```

2. Install the required Python packages:

    ```sh
    pip install -r requirements.txt
    ```

3. Install Tesseract OCR:

    - **Ubuntu**:
      ```sh
      sudo apt-get update
      sudo apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-all libtesseract-dev
      ```

    - **Windows**: Download and install Tesseract OCR from [here](https://github.com/tesseract-ocr/tesseract).

## Running the Application

1. **Locally**:

    ```sh
    python app.py
    ```

2. **Using Docker**:

    Build the Docker image:

    ```sh
    docker build -t find-nutrition-ocr .
    ```

    Run the Docker container:

    ```sh
    docker run -p 8080:8080 find-nutrition-ocr
    ```

## API Endpoints

1. **POST /ocr**: Perform OCR on the uploaded image.

    - **Request**:
      - `image`: The image file to be processed.
      - `text`: List of text strings to find in the image.

    - **Response**:
      - `ocr_data`: List of detected words and their bounding boxes.

2. **POST /plain_text**: Get plain text OCR for the uploaded image.

    - **Request**:
      - `image`: The image file to be processed.

    - **Response**:
      - `plain_text`: List of detected text strings.

3. **POST /find_text**: Find specific text in the uploaded image.

    - **Request**:
      - `image`: The image file to be processed.
      - `text`: List of text strings to find in the image.

    - **Response**:
      - `found_text`: List of found text strings.

4. **POST /final_info**: Extract nutritional content and get allergy information.

    - **Request**:
      - `image`: The image file to be processed.
      - `user_id`: The user ID.
      - `allergy`: List of allergies.

    - **Response**:
      - `final_result`: JSON object containing nutritional content and allergy information.

## Deployment

### Deploying to google cloud 

url service: https://find-nutrition-ocr-560152343412.asia-southeast1.run.app
Expires March 25, 2025 (Free Trial)

## Postman Collection

To make it easier to test the API endpoints, you can use the provided Postman collection.

### Importing the Postman Collection

1. Download the Postman collection file: [ocr-safebite.postman_collection.json]

2. Open Postman.

3. Click on the "Import" button in the top-left corner.

4. Select the "Upload Files" tab.

5. Choose the downloaded `find_nutrition_ocr.postman_collection.json` file and click "Open".

6. The collection will be imported into Postman, and you can now use it to test the API endpoints.

### Postman Collection File

You can find the Postman collection file in the repository: [ocr-safebite.postman_collection.json]

## License

This project is licensed under the MIT License. See the LICENSE file for details.