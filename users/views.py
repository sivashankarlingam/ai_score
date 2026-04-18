from django.shortcuts import render, HttpResponse
from django.contrib import messages

from .forms import UserRegistrationForm
from .models import UserRegistrationModel, ScoreHistory

import pandas as pd
import numpy as np
import re

from nltk.corpus import stopwords
from gensim.models import Word2Vec
from gensim.models import KeyedVectors

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

from PIL import Image
import pytesseract

import os

# Set path for windows/linux
if os.name == 'posix':  # Linux (Hugging Face)
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
else:  # Windows (Local)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# =========================
# USER REGISTRATION
# =========================
def UserRegisterActions(request):

    if request.method == 'POST':

        form = UserRegistrationForm(request.POST)

        if form.is_valid():

            form.save()
            messages.success(request, 'You have been successfully registered')

            form = UserRegistrationForm()
            return render(request, 'UserRegistrations.html', {'form': form})

        else:
            messages.success(request, 'Email or Mobile Already Exists')

    else:
        form = UserRegistrationForm()

    return render(request, 'UserRegistrations.html', {'form': form})


# =========================
# LOGIN
# =========================
def UserLoginCheck(request):

    if request.method == "POST":

        loginid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')

        try:

            check = UserRegistrationModel.objects.get(
                loginid=loginid,
                password=pswd
            )

            if check.status == "activated":

                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid

                return render(request, 'users/UserHomePage.html')

            else:

                messages.success(request, 'Your Account Not Activated')

        except:

            messages.success(request, 'Invalid Login ID and Password')

    return render(request, 'UserLogin.html')


# =========================
# USER HOME
# =========================
def UserHome(request):

    return render(request, 'users/UserHomePage.html')


# =========================
# DATASET VIEW
# =========================
def DatasetView(request):

    dataset_path = os.path.join(settings.BASE_DIR, 'media', 'training_set_rel3.tsv')
    
    df = pd.read_csv(
        dataset_path,
        sep='\t',
        encoding='ISO-8859-1'
    )

    df.dropna(axis=1, inplace=True)
    if 'essay' in df.columns:
        df['essay'] = df['essay'].str[:120] + '...'

    # Convert to HTML to avoid ambiguous truth value error in template
    # We limit to 100 rows to ensure the browser doesn't freeze with large datasets
    data_html = df.head(100).to_html(index=False) if not df.empty else None

    return render(
        request,
        'users/viewdataset.html',
        {'data': data_html}
    )


# =========================
# TRAINING
# =========================
def training(request):

    df = pd.read_csv(
        "media/training_set_rel3.tsv",
        sep='\t',
        encoding='ISO-8859-1'
    )

    df.dropna(axis=1, inplace=True)

    temp = pd.read_csv("media/Processed_data.csv")
    temp.drop(columns=["Unnamed: 0"], inplace=True)

    df['domain1_score'] = temp['final_score']

    y = df['domain1_score']
    X = df['essay']

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.3,
        random_state=42
    )

    stop_words = set(stopwords.words('english'))

    def clean(text):

        text = re.sub("[^A-Za-z]", " ", text)
        words = text.lower().split()

        return [w for w in words if w not in stop_words]

    train_words = [clean(e) for e in X_train]
    test_words = [clean(e) for e in X_test]

    # =========================
    # WORD2VEC
    # =========================

    word2vec_model = Word2Vec(
        train_words,
        vector_size=300,
        window=10,
        min_count=40,
        workers=4
    )

    word2vec_model.wv.save_word2vec_format(
        "word2vecmodel.bin",
        binary=True
    )

    def makeVec(words, model):

        vec = np.zeros((300,), dtype="float32")
        count = 0

        for w in words:

            if w in model.wv:
                vec += model.wv[w]
                count += 1

        if count != 0:
            vec /= count

        return vec

    train_vec = np.array([makeVec(w, word2vec_model) for w in train_words])
    test_vec = np.array([makeVec(w, word2vec_model) for w in test_words])

    train_vec = train_vec.reshape(train_vec.shape[0], 1, 300)
    test_vec = test_vec.reshape(test_vec.shape[0], 1, 300)

    # =========================
    # LSTM MODEL
    # =========================

    model = Sequential()

    model.add(LSTM(300, input_shape=(1, 300), return_sequences=True))
    model.add(LSTM(64))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='relu'))

    model.compile(
        loss='mean_squared_error',
        optimizer='rmsprop',
        metrics=['mae']
    )

    model.fit(
        train_vec,
        y_train,
        batch_size=64,
        epochs=5
    )

    model.save("final_lstm.h5")

    preds = model.predict(test_vec)

    mse = mean_squared_error(y_test, preds)
    rmse = np.sqrt(mse)

    return render(
        request,
        "users/ml.html",
        {
            'MSE': round(mse, 4),
            'RMSE': round(rmse, 4)
        }
    )


# =========================
# LOAD TRAINED MODELS
# =========================

word2vec_model = KeyedVectors.load_word2vec_format(
    "word2vecmodel.bin",
    binary=True
)

lstm_model = load_model("final_lstm.h5", compile=False)


# =========================
# PREDICTION
# =========================
def prediction(request):

    score = None

    if request.method == "POST":

        final_text = request.POST.get("final_text")
        image_file = request.FILES.get("essay_image")

        # OCR
        if image_file:

            try:
                img = Image.open(image_file)
                # Fallback path if pytesseract isn't in PATH natively
                final_text = pytesseract.image_to_string(img)
            except Exception as e:
                return render(
                    request,
                    "users/predictForm.html",
                    {"score": "OCR Error: Tesseract is not installed or configured correctly."}
                )

        if not final_text or str(final_text).strip() == "":

            return render(
                request,
                "users/predictForm.html",
                {"score": "Please enter essay text", "final_text": final_text}
            )

        stop_words = set(stopwords.words("english"))

        text = re.sub("[^A-Za-z]", " ", final_text)
        words = text.lower().split()
        words = [w for w in words if w not in stop_words]

        vec = np.zeros((300,), dtype="float32")
        count = 0

        for w in words:

            if w in word2vec_model.key_to_index:

                vec += word2vec_model[w]
                count += 1

        if count == 0:

            score = "No valid words found"

        else:

            vec /= count
            vec = vec.reshape(1, 1, 300)

            pred = lstm_model.predict(vec)

            score = str(round(float(pred[0][0])))

        # Save to history if score is numeric
        if score and score not in ["No valid words found", "Please enter essay text"]:
            loginid = request.session.get('loginid', 'anonymous')
            username = request.session.get('loggeduser', 'Unknown')
            snippet = (final_text[:200] + '...') if len(final_text) > 200 else final_text
            ScoreHistory.objects.create(
                loginid=loginid,
                username=username,
                essay_snippet=snippet,
                score=score
            )

        return render(
            request,
            "users/predictForm.html",
            {"score": score, "final_text": final_text}   # keep text in form
        )

    return render(request, "users/predictForm.html")


# =========================
# SCORE HISTORY
# =========================
def score_history(request):
    loginid = request.session.get('loginid', '')
    history = ScoreHistory.objects.filter(loginid=loginid)
    return render(request, 'users/score_history.html', {'history': history})


# =========================
# RECENT HISTORY
# =========================
def recent_history(request):
    loginid = request.session.get('loginid', '')
    recent = ScoreHistory.objects.filter(loginid=loginid)[:5]
    return render(request, 'users/recent_history.html', {'recent': recent})