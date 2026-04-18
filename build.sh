#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Download NLTK stopwords
python -m nltk.downloader stopwords

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate
