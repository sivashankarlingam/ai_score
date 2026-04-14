# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Railway providing dynamic port, default to 8000 for local testing
ENV PORT 8000

# Set work directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data (optimized for smaller size)
RUN python -m nltk.downloader stopwords punkt

# Copy project
COPY . /code/

# Run as non-root user (standard for cloud safety)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Let Docker know which port we expect (informational)
EXPOSE 8000

# Run migrations then start the project using gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:$PORT Automatic_English_Essay_Scoring_Algorithm_Based_On_Ml.wsgi:application"]
