# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Railway/Render providing dynamic port, default to 8000
ENV PORT 8000
ENV MALLOC_ARENA_MAX 2

# Set work directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

# Set NLTK data directory and environment variable
ENV NLTK_DATA /usr/local/share/nltk_data
RUN mkdir -p $NLTK_DATA && \
    python -m nltk.downloader -d $NLTK_DATA stopwords punkt

# Copy project 
COPY . /code/

# Run collectstatic for Whitenoise BEFORE switching users to avoid permission errors
RUN python manage.py collectstatic --noinput

# Run as non-root user (standard for cloud safety)
RUN useradd -m -u 1000 user && chown -R user:user /code

USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Let Docker know which port we expect (informational)
EXPOSE 8000

# Run migrations then start the project using gunicorn optimized for low memory
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 --worker-tmp-dir /dev/shm Automatic_English_Essay_Scoring_Algorithm_Based_On_Ml.wsgi:application"]
