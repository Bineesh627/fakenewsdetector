from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

# Helper function to check if user is staff (admin)
def is_staff(user):
    return user.is_authenticated and user.is_staff

import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from .models import Prediction, User, Feedback, Vote

@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_dashboard(request):
    # 1. Stats Calculation
    total_predictions = Prediction.objects.count()
    active_users = User.objects.count()
    pending_feedback = Feedback.objects.filter(approved=False, rejected=False).count()
    
    # Calculate Accuracy (Simple metric: 100% - % of "Fake" labeled corrections)
    # Only counting feedbacks that correct the label as errors
    error_count = Feedback.objects.count()
    if total_predictions > 0:
        accuracy = ((total_predictions - error_count) / total_predictions) * 100
    else:
        accuracy = 100

    stats = {
        'total_predictions': total_predictions,
        'active_users': active_users,
        'pending_feedback': pending_feedback,
        'accuracy_rate': round(accuracy, 1)
    }

    # 2. Recent Predictions (Fetch last 20 for table)
    recent_preds = Prediction.objects.order_by('-created_at')[:20]
    predictions_data = []
    
    # For Distribution Chart (fetch all or a larger sample)
    # Using aggregate for efficiency
    real_count = Prediction.objects.filter(prediction__iexact='Real').count()
    fake_count = Prediction.objects.filter(prediction__iexact='Fake').count()
    
    for p in recent_preds:
        predictions_data.append({
            'id': str(p.id),
            'text': p.text,
            'prediction': p.prediction,
            'confidence': p.confidence,
            'votesUp': p.votes_up,
            'votesDown': p.votes_down,
            'createdAt': p.created_at.isoformat()
        })

    # 3. Activity Logs (Synthesized)
    activity_list = []
    
    # New Predictions
    for p in recent_preds[:5]:
        activity_list.append({
            'id': f'pred_{p.id}',
            'details': f"New prediction: {p.prediction}",
            'createdAt': p.created_at,
            'timestamp': p.created_at.timestamp()
        })
        
    # Feedback
    for f in Feedback.objects.select_related('prediction').order_by('-created_at')[:5]:
        feed_text = f"Feedback on prediction #{f.prediction.id}"
        activity_list.append({
            'id': f'feed_{f.id}',
            'details': feed_text,
            'createdAt': f.created_at,
            'timestamp': f.created_at.timestamp()
        })
        
    # Votes
    for v in Vote.objects.select_related('prediction').order_by('-created_at')[:5]:
        vote_text = f"User voted {v.vote_type} on prediction #{v.prediction.id}"
        activity_list.append({
            'id': f'vote_{v.id}',
            'details': vote_text,
            'createdAt': v.created_at,
            'timestamp': v.created_at.timestamp()
        })

    # Sort by timestamp desc and take top 10
    activity_list.sort(key=lambda x: x['timestamp'], reverse=True)
    activity_data = activity_list[:10]
    
    # Remove timestamp helper
    for item in activity_data:
        item['createdAt'] = item['createdAt'].isoformat()
        del item['timestamp']

    context = {
        'stats_json': json.dumps(stats, cls=DjangoJSONEncoder),
        'predictions_json': json.dumps(predictions_data, cls=DjangoJSONEncoder),
        'activity_json': json.dumps(activity_data, cls=DjangoJSONEncoder),
        'real_count': real_count,
        'fake_count': fake_count
    }

    return render(request, 'admin/Dashboard.html', context)

@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_users(request):
    # Fetch all users
    all_users = User.objects.all().order_by('-date_joined')
    
    users_data = []
    for u in all_users:
        users_data.append({
            'id': str(u.id),
            'username': u.username,
            'email': u.email,
            'isAdmin': u.is_staff,
            'createdAt': u.date_joined.isoformat() if u.date_joined else None
        })

    context = {
        'users_json': json.dumps(users_data, cls=DjangoJSONEncoder)
    }
    
    return render(request, 'admin/UsersManagement.html', context)

@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_activity(request):
    activity_list = []
    
    # 1. Predictions
    for p in Prediction.objects.select_related('user').order_by('-created_at')[:50]:
        username = p.user.username if p.user else "Anonymous"
        activity_list.append({
            'id': f'pred_{p.id}',
            'action': 'prediction_created',
            'userId': str(p.user.id) if p.user else None,
            'username': username,
            'details': f"{username} submitted a new article for analysis",
            'createdAt': p.created_at,
            'timestamp': p.created_at.timestamp()
        })

    # 2. Feedback
    for f in Feedback.objects.select_related('user', 'prediction').order_by('-created_at')[:50]:
        username = f.user.username if f.user else "Anonymous"
        activity_list.append({
            'id': f'feed_{f.id}',
            'action': 'feedback_submitted',
            'userId': str(f.user.id) if f.user else None,
            'username': username,
            'details': f"{username} flagged prediction #{f.prediction.id} as incorrect",
            'createdAt': f.created_at,
            'timestamp': f.created_at.timestamp()
        })

    # 3. Votes
    for v in Vote.objects.select_related('user', 'prediction').order_by('-created_at')[:50]:
        username = v.user.username if v.user else "Anonymous"
        action = 'vote_up' if v.vote_type == 'UP' else 'vote_down'
        activity_list.append({
            'id': f'vote_{v.id}',
            'action': action,
            'userId': str(v.user.id) if v.user else None,
            'username': username,
            'details': f"{username} {'upvoted' if v.vote_type == 'UP' else 'downvoted'} prediction #{v.prediction.id}",
            'createdAt': v.created_at,
            'timestamp': v.created_at.timestamp()
        })
        
    # 4. Updates (New Users - utilizing date_joined as a proxy for "User Login" category in this template context)
    for u in User.objects.all().order_by('-date_joined')[:50]:
        activity_list.append({
            'id': f'user_{u.id}',
            'action': 'user_login', # Mapping to existing template filter category
            'userId': str(u.id),
            'username': u.username,
            'details': f"User {u.username} joined the platform",
            'createdAt': u.date_joined,
            'timestamp': u.date_joined.timestamp()
        })

    # Sort & Slice
    activity_list.sort(key=lambda x: x['timestamp'], reverse=True)
    final_logs = activity_list[:100] # Cap at 100 mixed items
    
    # Text formatting
    for item in final_logs:
        item['createdAt'] = item['createdAt'].isoformat()
        del item['timestamp']

    context = {
        'activity_json': json.dumps(final_logs, cls=DjangoJSONEncoder)
    }
    return render(request, 'admin/ActivityLogs.html', context)

from django.utils import timezone
from datetime import timedelta

@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_feedback(request):
    # Stats
    start_of_week = timezone.now() - timedelta(days=7)
    start_of_week = timezone.now() - timedelta(days=7)
    approved_count = Feedback.objects.filter(approved=True, created_at__gte=start_of_week).count()
    rejected_count = Feedback.objects.filter(rejected=True, created_at__gte=start_of_week).count()
    
    # Fetch pending feedback (unapproved AND not rejected)
    pending_feedback = Feedback.objects.filter(approved=False, rejected=False).order_by('created_at')
    
    feedback_data = []
    for f in pending_feedback:
        feedback_data.append({
            'id': f.id,
            'prediction': {
                'id': f.prediction.id,
                'text': f.prediction.text,
                'prediction': f.prediction.prediction
            },
            'correctedLabel': f.corrected_label,
            'note': f.feedback_note,
            'userId': f.user.username if f.user else 'Anonymous',
            'createdAt': f.created_at.isoformat()
        })
        
    context = {
        'feedback_json': json.dumps(feedback_data, cls=DjangoJSONEncoder),
        'stats': {
            'approved_week': approved_count,
            'rejected_week': rejected_count
        }
    }
    return render(request, 'admin/FeedbackManagement.html', context)

@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_predictions(request):
    all_preds = Prediction.objects.all().order_by('-created_at')
    
    preds_data = []
    for p in all_preds:
        preds_data.append({
            'id': str(p.id),
            'text': p.text,
            'linkUrl': p.link_url,
            'prediction': p.prediction,
            'confidence': p.confidence,
            'votesUp': p.votes_up,
            'votesDown': p.votes_down,
            'isCorrection': p.corrections.exists(),
            'createdAt': p.created_at.isoformat(),
            'status': 'Flagged' if p.corrections.exists() else 'Active'
        })

    context = {
        'predictions_json': json.dumps(preds_data, cls=DjangoJSONEncoder)
    }

    return render(request, 'admin/PredictionsManagement.html', context)

@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_settings(request):
    return render(request, 'admin/Settings.html')

# --- API Endpoints for User Management ---

from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

@require_POST
@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_add_user(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')

        if not all([username, email, password]):
            return JsonResponse({'success': False, 'message': 'Missing fields'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': 'Username already exists'}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        if role == 'admin':
            user.is_staff = True
            user.save()

        return JsonResponse({'success': True, 'message': 'User created successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_POST
@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_delete_user(request, user_id):
    try:
        # Prevent deleting self
        if request.user.id == user_id:
            return JsonResponse({'success': False, 'message': 'Cannot delete your own account'}, status=403)
            
        user = User.objects.get(id=user_id)
        user.delete()
        return JsonResponse({'success': True})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_POST
@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_toggle_admin(request, user_id):
    try:
        # Prevent changing own status
        if request.user.id == user_id:
            return JsonResponse({'success': False, 'message': 'Cannot change your own role'}, status=403)

        user = User.objects.get(id=user_id)
        user.is_staff = not user.is_staff
        user.save()
        return JsonResponse({'success': True, 'is_admin': user.is_staff})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

from django.views.decorators.http import require_GET

@require_GET
@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_get_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': 'Admin' if user.is_staff else 'User',
            'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else 'N/A'
        }
        return JsonResponse({'success': True, 'user': data})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)

@require_POST
@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_edit_user(request, user_id):
    try:
        data = json.loads(request.body)
        user = User.objects.get(id=user_id)
        
        # basic validation / update
        username = data.get('username')
        email = data.get('email')
        
        if username:
            if User.objects.filter(username=username).exclude(id=user_id).exists():
                 return JsonResponse({'success': False, 'message': 'Username already taken'}, status=400)
            user.username = username
            
        if email:
            user.email = email
            
        user.save()
        return JsonResponse({'success': True})
    except User.DoesNotExist:
         return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# --- API Endpoints for Predictions Management ---

import csv
from django.http import HttpResponse

@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_export_predictions(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="predictions_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Text', 'Prediction', 'Confidence', 'Votes Up', 'Votes Down', 'Created At'])

    for p in Prediction.objects.all().order_by('-created_at'):
        writer.writerow([
            p.id,
            p.text,
            p.prediction,
            f"{p.confidence:.2f}",
            p.votes_up,
            p.votes_down,
            p.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    return response

@require_GET
@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_get_prediction(request, pred_id):
    try:
        p = Prediction.objects.get(id=pred_id)
        data = {
            'id': p.id,
            'text': p.text,
            'prediction': p.prediction,
            'confidence': p.confidence,
            'votesUp': p.votes_up,
            'votesDown': p.votes_down,
            'createdAt': p.created_at.isoformat(),
            'linkUrl': p.link_url
        }
        return JsonResponse({'success': True, 'prediction': data})
    except Prediction.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Prediction not found'}, status=404)

@require_POST
@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_edit_prediction(request, pred_id):
    try:
        data = json.loads(request.body)
        p = Prediction.objects.get(id=pred_id)
        
        new_prediction = data.get('prediction')
        if new_prediction in ['Real', 'Fake']:
            p.prediction = new_prediction
            p.save()
            return JsonResponse({'success': True})
        else:
             return JsonResponse({'success': False, 'message': 'Invalid value'}, status=400)
             
    except Prediction.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Prediction not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_POST
@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_delete_prediction(request, pred_id):
    try:
        p = Prediction.objects.get(id=pred_id)
        p.delete()
        return JsonResponse({'success': True})
    except Prediction.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Prediction not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# --- API Endpoints for Feedback Management ---

@require_POST
@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_approve_feedback(request, feedback_id):
    try:
        feedback = Feedback.objects.get(id=feedback_id)
        
        # 1. Update Feedback status
        feedback.approved = True
        feedback.save()
        
        # 2. Update the actual Prediction
        prediction = feedback.prediction
        prediction.prediction = feedback.corrected_label
        # We might want to track that this was manually corrected?
        # prediction.isCorrection = True # If such field existed
        prediction.save()
        
        return JsonResponse({'success': True, 'message': 'Feedback approved and prediction updated.'})
    except Feedback.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Feedback not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_POST
@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_reject_feedback(request, feedback_id):
    try:
        feedback = Feedback.objects.get(id=feedback_id)
        feedback.rejected = True
        feedback.save()
        return JsonResponse({'success': True, 'message': 'Feedback rejected.'})
    except Feedback.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Feedback not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
