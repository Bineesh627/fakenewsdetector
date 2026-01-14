from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse
from django.db import models
from django.db.models import Count, Q, F
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import requests
from bs4 import BeautifulSoup
from .models import Prediction, Vote, Feedback
import joblib

# Load LSTM model, tokenizer, max_seq_len
model = tf.keras.models.load_model('model/fake_news_lstm.h5')
with open('model/tokenizer.pickle', 'rb') as handle:
    tokenizer = joblib.load(handle)
with open('model/max_seq_len.txt', 'r') as f:
    max_seq_len = int(f.read())

def preprocess(text):
    return text.lower()

def predict_fake_news(text):
    processed_text = preprocess(text)
    seq = tokenizer.texts_to_sequences([processed_text])
    padded = pad_sequences(seq, maxlen=max_seq_len)
    pred = model.predict(padded)[0][0]
    result = 'Real' if pred > 0.5 else 'Fake'
    confidence = pred if pred > 0.5 else (1 - pred)
    return result, confidence

def scrape_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text() for p in paragraphs if p.get_text().strip()])
        return text[:5000]  # Limit length
    except Exception:
        return None

@login_required
def home(request):
    if request.method == 'POST':
        link_url = request.POST.get('news_link')
        input_text = request.POST.get('news_text')
        text = input_text or scrape_text_from_url(link_url)
        if text:
            result, confidence = predict_fake_news(text)
            pred = Prediction.objects.create(
                user=request.user,
                link_url=link_url,
                text=text,
                prediction=result,
                confidence=confidence
            )
            return render(request, 'result.html', {'pred': pred})
        else:
            return HttpResponse("Invalid link or text.")
    
    # Popular: Order by net votes (up - down)
    popular = Prediction.objects.annotate(
        up_votes=Count('vote', filter=Q(vote__vote_type='UP')),
        down_votes=Count('vote', filter=Q(vote__vote_type='DOWN'))
    ).annotate(
        net_votes=F('up_votes') - F('down_votes')
    ).order_by('-net_votes')[:10]
    return render(request, 'home.html', {'popular': popular})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def feedback_view(request, pred_id):
    pred = Prediction.objects.get(id=pred_id)
    if request.method == 'POST':
        corrected_label = request.POST.get('corrected_label')
        note = request.POST.get('note')
        Feedback.objects.create(
            prediction=pred,
            user=request.user,
            corrected_label=corrected_label,
            feedback_note=note
        )
        return redirect('home')
    return render(request, 'feedback.html', {'pred': pred})

@login_required
def vote(request, pred_id, vote_type):
    pred = Prediction.objects.get(id=pred_id)
    vote_type = vote_type.upper()
    if vote_type in ['UP', 'DOWN']:
        Vote.objects.update_or_create(
            prediction=pred,
            user=request.user,
            defaults={'vote_type': vote_type}
        )
    return redirect('home')

def predictions_list(request):
    preds = Prediction.objects.all().order_by('-created_at')
    return render(request, 'list.html', {'predictions': preds})