# Essay Scoring System & OCR Engine

This is a comprehensive Django-based application for automatically scoring English essays using Machine Learning (LSTM & Word2Vec) and extracting text from handwritten images using Tesseract OCR.

## Features
- **AI Scoring**: Evaluation of semantic depth and coherence.
- **Handwriting OCR**: Image-to-text processing via Tesseract.
- **Voice Features**: Built-in speech recognition for essay dictation.

## Deployment Details (Railway.app)
This project is configured for deployment on Railway using a **Dockerfile**.

### Environment Variables
For production, you should set these in your Railway dashboard:
- `DEBUG`: Set to `False`
- `SECRET_KEY`: Your production secret key
- `DATABASE_URL`: Automatically provided if you add a PostgreSQL service

### Local Setup
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Install Tesseract OCR locally.
4. Run migrations: `python manage.py migrate`
5. Run server: `python manage.py runserver`
