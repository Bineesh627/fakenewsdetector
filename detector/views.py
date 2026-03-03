from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse
from django.db import models
from django.db.models import Count, Q, F
from django.contrib import messages
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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        body = soup.find('body')
        if body:
            # Remove unwanted tags
            for tag in body(["script", "style", "header", "footer", "nav", "aside", "form", "iframe", "ads", "advertisement"]):
                tag.decompose()

            # Capture specific content block tags.
            # We exclude 'div' to avoid capturing menus/sidebars/footers which often are just divs with links.
            # Valid inline tags like strong, mark, em etc. will be captured if they are inside these blocks.
            content_tags = body.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'blockquote', 'article', 'section'])
            text = ' '.join([tag.get_text(separator=' ', strip=True) for tag in content_tags if tag.get_text(strip=True)])
            # Clean up extra spaces
            text = ' '.join(text.split())
            return text[:5000]
            
        return None
    except Exception:
        return None

def home(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
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
            # Serialize for result page
            prediction_data = [{
                'id': str(pred.id),
                'text': pred.text,
                'linkUrl': pred.link_url if pred.link_url else '',
                'prediction': pred.prediction,
                'confidence': float(pred.confidence),
                'votesUp': 0,
                'votesDown': 0,
                'userId': str(pred.user.id) if pred.user else '',
                'userName': pred.user.username if pred.user else 'Anonymous',
                'createdAt': pred.created_at.isoformat(), 
                'isCorrection': False 
            }]
            predictions_json = json.dumps(prediction_data, cls=DjangoJSONEncoder)

            return render(request, 'users/Results.html', {'predictions_json': predictions_json})
        else:
            return HttpResponse("Invalid link or text.")
    
    # Popular: Order by net votes (up - down)
    popular = Prediction.objects.annotate(
        up_votes=Count('vote', filter=Q(vote__vote_type='UP')),
        down_votes=Count('vote', filter=Q(vote__vote_type='DOWN'))
    ).annotate(
        net_votes=F('up_votes') - F('down_votes')
    ).order_by('-net_votes')[:10]
    return render(request, 'users/home.html', {'popular': popular})

def signup(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
             return render(request, 'auth/signup.html', {'error': 'Username already taken'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'auth/signup.html', {'error': 'Email already registered'})
            
        try:
            # Create user with username and email
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('home')
        except Exception as e:
            return render(request, 'auth/signup.html', {'error': 'Error creating account'})
            
    return render(request, 'auth/signup.html')

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('home')
        
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            # Find user by email
            user_obj = User.objects.get(email=email)
            # Authenticate using the username (which is the email in our case)
            user = authenticate(request, username=user_obj.username, password=password)
            
            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect('admin_dashboard')
                return redirect('home')
            else:
                 return render(request, 'auth/login.html', {'error': 'Invalid email or password'})
        except User.DoesNotExist:
             return render(request, 'auth/login.html', {'error': 'Invalid email or password'})

    return render(request, 'auth/login.html')

@login_required(login_url='login')
def feedback_view(request, pred_id):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    try:
        pred = Prediction.objects.annotate(
            up_votes=Count('vote', filter=Q(vote__vote_type='UP')),
            down_votes=Count('vote', filter=Q(vote__vote_type='DOWN'))
        ).get(id=pred_id)
    except Prediction.DoesNotExist:
        return redirect('predictions_list')

    if request.method == 'POST':
        # Handle form submission
        corrected_label = request.POST.get('corrected_label')
        feedback_note = request.POST.get('feedback_note')
        
        Feedback.objects.create(
            prediction=pred,
            user=request.user,
            corrected_label=corrected_label,
            feedback_note=feedback_note
        )
        # Return JSON success for JS fetch or redirect
        return JsonResponse({'status': 'success', 'message': 'Feedback submitted'})

    # Serialize for template
    prediction_data = [{
        'id': str(pred.id),
        'text': pred.text,
        'linkUrl': pred.link_url if pred.link_url else '',
        'prediction': pred.prediction,
        'confidence': float(pred.confidence),
        'votesUp': pred.up_votes,
        'votesDown': pred.down_votes,
        'userId': str(pred.user.id) if pred.user else '',
        'createdAt': pred.created_at.isoformat(), 
        'isCorrection': False 
    }]
    predictions_json = json.dumps(prediction_data, cls=DjangoJSONEncoder)

    return render(request, 'users/Feedback.html', {'predictions_json': predictions_json, 'pred_id': pred_id})

@login_required(login_url='login')
def vote(request, pred_id, vote_type):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    pred = Prediction.objects.get(id=pred_id)
    vote_type = vote_type.upper()
    if vote_type in ['UP', 'DOWN']:
        Vote.objects.update_or_create(
            prediction=pred,
            user=request.user,
            defaults={'vote_type': vote_type}
        )
    return redirect(request.META.get('HTTP_REFERER', 'home'))

import json
from django.core.serializers.json import DjangoJSONEncoder

@login_required(login_url='login')
def predictions_list(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    # Annotate with vote counts
    preds_qs = Prediction.objects.annotate(
        up_votes=Count('vote', filter=Q(vote__vote_type='UP')),
        down_votes=Count('vote', filter=Q(vote__vote_type='DOWN'))
    ).order_by('-created_at')

    # Serialize to list of dicts for JS
    predictions_data = []
    for p in preds_qs:
        predictions_data.append({
            'id': str(p.id),
            'text': p.text,
            'linkUrl': p.link_url if p.link_url else '',
            'prediction': p.prediction,
            'confidence': float(p.confidence),
            'votesUp': p.up_votes,
            'votesDown': p.down_votes,
            'userId': str(p.user.id),
            'userName': p.user.username,
            'createdAt': p.created_at.isoformat(), # ISO format for JS Date parsing
            'isCorrection': False # helper logic if needed
        })
    
    # Dump to JSON string
    predictions_json = json.dumps(predictions_data, cls=DjangoJSONEncoder)
    
    return render(request, 'users/PredictionList.html', {'predictions_json': predictions_json})

@login_required(login_url='login')
def prediction_detail(request, pred_id):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    # Get specific prediction and annotate
    p = Prediction.objects.annotate(
        up_votes=Count('vote', filter=Q(vote__vote_type='UP')),
        down_votes=Count('vote', filter=Q(vote__vote_type='DOWN'))
    ).get(id=pred_id)

    # Serialize to list of ONE dict (to match template array structure)
    prediction_data = [{
        'id': str(p.id),
        'text': p.text,
        'linkUrl': p.link_url if p.link_url else '',
        'prediction': p.prediction,
        'confidence': float(p.confidence),
        'votesUp': p.up_votes,
        'votesDown': p.down_votes,
        'userId': str(p.user.id),
        'userName': p.user.username,
        'createdAt': p.created_at.isoformat(), 
        'isCorrection': False 
    }]

    predictions_json = json.dumps(prediction_data, cls=DjangoJSONEncoder)
    
    return render(request, 'users/PredictionDetails.html', {'predictions_json': predictions_json})

@login_required(login_url='login')
def profile_view(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        # Handle profile update
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Validate email
        if not email:
            messages.error(request, 'Email is required')
        elif User.objects.filter(email=email).exclude(id=request.user.id).exists():
            messages.error(request, 'Email is already in use by another account')
        else:
            # Update user profile
            request.user.email = email
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
    
    # Get user statistics
    total_predictions = Prediction.objects.filter(user=request.user).count()
    total_votes = Vote.objects.filter(user=request.user).count()
    member_since = request.user.date_joined.strftime('%b %Y')
    
    context = {
        'total_predictions': total_predictions,
        'total_votes': total_votes,
        'member_since': member_since
    }
    
    return render(request, 'users/profile.html', context)

@login_required(login_url='login')
def password_change_view(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate passwords
        if not old_password or not new_password or not confirm_password:
            messages.error(request, 'All password fields are required')
        elif not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match')
        elif len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long')
        else:
            # Change password
            request.user.set_password(new_password)
            request.user.save()
            # Re-authenticate the user with new password
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
    
    return render(request, 'users/password_change.html')