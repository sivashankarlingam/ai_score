---
title: AI English Essay Scoring System
emoji: 📝
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 7860
---

# Automatic English Essay Scoring Algorithm

This space hosts a Django-based web application that uses Machine Learning (LSTM & Word2Vec) to automatically score English essays. It also features handwritten essay recognition using Tesseract OCR.

## Features
- **AI Scoring**: Intelligent evaluation based on pre-trained LSTM models.
- **Handwriting OCR**: Upload images of handwritten essays for automatic text extraction.
- **Voice-to-Text**: Dictate your essay directly in the browser (Chrome recommended).

## Technical Stack
- **Backend**: Django (Python)
- **ML Engine**: TensorFlow, Gensim, Scikit-learn
- **OCR Engine**: Tesseract OCR
- **Deployment**: Dockerized on Hugging Face Spaces
