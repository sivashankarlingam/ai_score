from ninja import NinjaAPI, Schema
from django.shortcuts import get_object_or_404
from typing import List, Optional
from datetime import datetime
from .models import UserRegistrationModel, ScoreHistory
import json
import urllib.request
import urllib.parse
import base64
import io
from PIL import Image
import numpy as np
import re
from nltk.corpus import stopwords
from gensim.models import Word2Vec, KeyedVectors
import pandas as pd
from django.conf import settings
import os
import tensorflow as tf

api = NinjaAPI(title="AI Score API", version="1.0.0")

# --- Global Model Loading (Optimized for Production) ---
W2V_PATH = os.path.join(settings.BASE_DIR, "word2vecmodel.bin")
LSTM_PATH = os.path.join(settings.BASE_DIR, "final_lstm.h5")

# Load models once when the server starts
try:
    word2vec_model = KeyedVectors.load_word2vec_format(W2V_PATH, binary=True)
    lstm_model = tf.keras.models.load_model(LSTM_PATH, compile=False)
except Exception as e:
    print(f"ERROR: Could not load ML models: {e}")
    word2vec_model = None
    lstm_model = None

# --- Schemas ---
class LoginSchema(Schema):
    loginid: str
    password: str

class RegisterSchema(Schema):
    name: str
    loginid: str
    password: str
    mobile: str
    email: str
    locality: str
    address: str
    city: str
    state: str

class UserOutSchema(Schema):
    name: str
    loginid: str
    email: str
    city: str
    is_admin: bool = False

class AdminUserListSchema(Schema):
    id: int
    name: str
    loginid: str
    email: str
    mobile: str
    city: str
    state: str
    locality: str
    address: str
    status: str

class UserUpdateSchema(Schema):
    name: str
    email: str
    mobile: str
    locality: str
    address: str
    city: str
    state: str

class PredictSchema(Schema):
    loginid: str
    text: Optional[str] = None
    base64_image: Optional[str] = None  # Expected format: base64 string without data:image prefix

class ScoreHistoryOutSchema(Schema):
    score: str
    essay_snippet: str
    scored_at: datetime
    
class GenericMessage(Schema):
    message: str
    success: bool
    score: Optional[str] = None

# --- Helpers ---
def convert_and_clean(word):
    word = word.lower()
    word = re.sub(r'[^a-z0-9]', '', word)
    return word

def feature_vec(words, model, num_features):
    feature_vector = np.zeros((num_features,), dtype="float32")
    nwords = 0
    index2word_set = set(model.wv.index_to_key)
    for word in words:
        if word in index2word_set:
            nwords += 1
            feature_vector = np.add(feature_vector, model.wv[word])
    if nwords > 0:
        feature_vector = np.divide(feature_vector, nwords)
    return feature_vector

# --- Endpoints ---

@api.post("/auth/register", response={200: GenericMessage, 400: GenericMessage})
def register(request, payload: RegisterSchema):
    if UserRegistrationModel.objects.filter(loginid=payload.loginid).exists():
        return 400, {"message": "Login ID already exists", "success": False}
    if UserRegistrationModel.objects.filter(email=payload.email).exists():
        return 400, {"message": "Email already exists", "success": False}
    
    UserRegistrationModel.objects.create(
        name=payload.name, loginid=payload.loginid, password=payload.password,
        mobile=payload.mobile, email=payload.email, locality=payload.locality,
        address=payload.address, city=payload.city, state=payload.state,
        status="waiting"
    )
    return 200, {"message": "Registration successful. Please wait for admin approval.", "success": True}

@api.post("/auth/login", response={200: UserOutSchema, 401: GenericMessage, 403: GenericMessage})
def login(request, payload: LoginSchema):
    # Admin short-circuit: hardcoded admin credentials
    if payload.loginid == 'admin' and payload.password == 'admin':
        return 200, {
            "name": "Administrator", "loginid": "admin",
            "email": "admin@aesscore.com", "city": "Admin",
            "is_admin": True
        }

    user = UserRegistrationModel.objects.filter(loginid=payload.loginid, password=payload.password).first()
    if not user:
        return 401, {"message": "Invalid credentials", "success": False}
    if user.status != "activated":
        return 403, {"message": "Account not activated yet", "success": False}
    
    return 200, {
        "name": user.name, "loginid": user.loginid, "email": user.email, "city": user.city,
        "is_admin": False
    }

@api.get("/history/{loginid}", response=List[ScoreHistoryOutSchema])
def history(request, loginid: str):
    qs = ScoreHistory.objects.filter(loginid=loginid).order_by('-scored_at')
    return list(qs)

@api.post("/predict", response={200: GenericMessage, 400: GenericMessage})
def predict(request, payload: PredictSchema):
    final_text = payload.text
    
    # Process Image if text is not provided but image is
    if payload.base64_image and not final_text:
        try:
            img_data = base64.b64decode(payload.base64_image)
            img = Image.open(io.BytesIO(img_data))
            if img.mode != 'RGB': img = img.convert('RGB')
            max_dim = 1200
            if max(img.size) > max_dim:
                ratio = max_dim / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                
            quality = 85
            img_byte_arr = io.BytesIO()
            while quality > 10:
                img_byte_arr.seek(0)
                img_byte_arr.truncate()
                img.save(img_byte_arr, format='JPEG', optimize=True, quality=quality)
                if len(img_byte_arr.getvalue()) < 700000: break
                quality -= 15
                
            base64_str = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            data = urllib.parse.urlencode({
                'apikey': 'helloworld', 'language': 'eng', 'base64Image': 'data:image/jpeg;base64,' + base64_str
            }).encode('utf-8')
            
            req = urllib.request.Request('https://api.ocr.space/parse/image', data=data)
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                if not result.get("IsErroredOnProcessing"):
                    parsed = result.get("ParsedResults", [])
                    final_text = parsed[0].get("ParsedText", "") if parsed else ""
                else:
                    return 400, {"message": f"OCR API Error: {result.get('ErrorMessage')}", "success": False}
        except Exception as e:
            return 400, {"message": f"OCR Error: {str(e)}", "success": False}
            
    if not final_text or str(final_text).strip() == "":
        return 400, {"message": "Please enter essay text or upload a valid image", "success": False}
        
    if not word2vec_model or not lstm_model:
        return 400, {"message": "Server error: ML models not loaded correctly", "success": False}

    try:
        # ML Preprocessing
        stop_words = set(stopwords.words("english"))
        text = re.sub("[^A-Za-z]", " ", final_text)
        words = text.lower().split()
        cleaned_words = [convert_and_clean(word) for word in words if word not in stop_words]
        
        num_features = 300
        
        # Calculate feature vector using the globally loaded model
        feature_vector = np.zeros((num_features,), dtype="float32")
        nwords = 0
        for word in cleaned_words:
            if word in word2vec_model.key_to_index:
                nwords += 1
                feature_vector = np.add(feature_vector, word2vec_model[word])
        if nwords > 0:
            feature_vector = np.divide(feature_vector, nwords)
            
        test_data = np.reshape(feature_vector, (1, 1, num_features))
        predicted_score = lstm_model.predict(test_data)[0][0]
        score_val = str(round(predicted_score))
        
        # Record history
        user = UserRegistrationModel.objects.filter(loginid=payload.loginid).first()
        if user:
            ScoreHistory.objects.create(
                loginid=user.loginid,
                username=user.name,
                essay_snippet=final_text[:200] + "...",
                score=score_val
            )
            
        return 200, {"message": "Success", "success": True, "score": score_val}
    except Exception as e:
        return 400, {"message": f"Prediction Error: {str(e)}", "success": False}

@api.get("/health", response={200: GenericMessage})
def health_check(request):
    return 200, {"message": "API is online", "success": True}

# --- Admin Endpoints ---

@api.get("/admin/users", response=List[AdminUserListSchema])
def admin_list_users(request):
    return list(UserRegistrationModel.objects.all().order_by('-id'))

@api.put("/admin/users/{uid}/activate", response={200: GenericMessage, 404: GenericMessage})
def admin_activate_user(request, uid: int):
    updated = UserRegistrationModel.objects.filter(id=uid).update(status='activated')
    if updated:
        return 200, {"message": "User activated successfully", "success": True}
    return 404, {"message": "User not found", "success": False}

@api.put("/admin/users/{uid}", response={200: GenericMessage, 404: GenericMessage})
def admin_update_user(request, uid: int, payload: UserUpdateSchema):
    updated = UserRegistrationModel.objects.filter(id=uid).update(
        name=payload.name, email=payload.email, mobile=payload.mobile,
        locality=payload.locality, address=payload.address,
        city=payload.city, state=payload.state
    )
    if updated:
        return 200, {"message": "User updated successfully", "success": True}
    return 404, {"message": "User not found", "success": False}

@api.delete("/admin/users/{uid}", response={200: GenericMessage, 404: GenericMessage})
def admin_delete_user(request, uid: int):
    deleted, _ = UserRegistrationModel.objects.filter(id=uid).delete()
    if deleted:
        return 200, {"message": "User deleted successfully", "success": True}
    return 404, {"message": "User not found", "success": False}
