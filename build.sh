#!/usr/bin/env bash
# exit on error
set -o errexit
python --version
pip --version

# Install dependencies
pip install -r requirements.txt

# Download NLTK stopwords
python -m nltk.downloader -d nltk_data stopwords

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate
