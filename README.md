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

2. Install the required Python packages:

```sh
pip install -r requirements.txt

3. Install Tesseract OCR:

```sh
Ubuntu:
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-all libtesseract-dev

Windows: Download and install Tesseract OCR from here.

## API Endpoints

POST /ocr: Perform OCR on the uploaded image.

Request:
image: The image file to be processed.
text: List of text strings to find in the image.
Response:
ocr_data: List of detected words and their bounding boxes.
POST /plain_text: Get plain text OCR for the uploaded image.

Request:
image: The image file to be processed.
Response:
plain_text: List of detected text strings.
POST /find_text: Find specific text in the uploaded image.

Request:
image: The image file to be processed.
text: List of text strings to find in the image.
Response:
found_text: List of found text strings.
