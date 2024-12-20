# Use an official Python 3.12.8 runtime as a parent image
FROM python:3.12.8-slim

# Install dependencies for GPU support
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install CUDA and cuDNN
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-repo-ubuntu1804_10.1.243-1_amd64.deb && \
    dpkg -i cuda-repo-ubuntu1804_10.1.243-1_amd64.deb && \
    apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub && \
    apt-get update && apt-get install -y cuda

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set the Tesseract command path
ENV TESSERACT_CMD=/usr/bin/tesseract

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]