# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies including Tesseract OCR and language packs (Bengali and English)
# Also install libgl1-mesa-glx (often a dependency for image processing libraries)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-ben \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir reduces image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code (main.py) into the container
COPY main.py .

# BOT_TOKEN এনভায়রনমেন্ট ভেরিয়েবলটি প্ল্যাটফর্ম থেকে পাস করা হবে (যেমন সিনোড.কম)
# main.py ফাইলটি os.environ.get("BOT_TOKEN") ব্যবহার করে এটি পড়ে নেবে।

# Application runs on this command
CMD ["python", "main.py"]