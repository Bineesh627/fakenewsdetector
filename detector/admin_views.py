from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

# Helper function to check if user is staff (admin)
def is_staff(user):
    return user.is_authenticated and user.is_staff

import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from .models import Prediction, User, Feedback, Vote, DashboardStats, ActivityLog
from django.utils import timezone
from datetime import timedelta

def refresh_dashboard_stats():
    # Helper to calculate and save stats
    total_predictions = Prediction.objects.count()
    active_users = User.objects.count()
    pending_feedback = Feedback.objects.filter(approved=False, rejected=False).count()
    
    error_count = Feedback.objects.count()
    if total_predictions > 0:
        accuracy = ((total_predictions - error_count) / total_predictions) * 100
    else:
        accuracy = 100.0
        
    real_count = Prediction.objects.filter(prediction__iexact='Real').count()
    fake_count = Prediction.objects.filter(prediction__iexact='Fake').count()
    
    stats, created = DashboardStats.objects.get_or_create(id=1)
    stats.total_predictions = total_predictions
    stats.active_users = active_users
    stats.pending_feedback = pending_feedback
    stats.accuracy_rate = round(accuracy, 1)
    stats.real_count = real_count
    stats.fake_count = fake_count
    stats.save()
    return stats

@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_dashboard(request):
    # 1. Get or Refresh Stats
    # For now, we refresh on load to ensure accuracy, or we could check a timestamp
    stats_obj = refresh_dashboard_stats()
    
    # 2. Recent Predictions (QuerySet for SSR)
    recent_preds = Prediction.objects.order_by('-created_at')[:20]

    stats_dict = {
        'total_predictions': stats_obj.total_predictions,
        'active_users': stats_obj.active_users,
        'pending_feedback': stats_obj.pending_feedback,
        'accuracy_rate': stats_obj.accuracy_rate
    }

    # 3. Activity Logs (Real from DB)
    activity_list = []
    # Fetch recent logs
    recent_logs = ActivityLog.objects.select_related('actor').order_by('-created_at')[:10]
    
    for log in recent_logs:
        activity_list.append({
            'id': str(log.id),
            'details': log.details,
            'createdAt': log.created_at.isoformat()
        })

    context = {
        'stats_json': json.dumps(stats_dict, cls=DjangoJSONEncoder),
        # 'predictions_json': json.dumps(predictions_data, cls=DjangoJSONEncoder), # REMOVED for SSR
        'recent_preds': recent_preds, # NEW for SSR
        'activity_json': json.dumps(activity_list, cls=DjangoJSONEncoder),
        'real_count': stats_obj.real_count,
        'fake_count': stats_obj.fake_count
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
    # Fetch logs from the database
    logs = ActivityLog.objects.select_related('actor').order_by('-created_at')[:100]
    
    activity_list = []
    for log in logs:
        activity_list.append({
            'id': str(log.id),
            'action': log.action_type,
            'userId': str(log.actor.id) if log.actor else None,
            'username': log.actor.username if log.actor else "Anonymous",
            'details': log.details,
            'createdAt': log.created_at.isoformat()
        })

    context = {
        'activity_json': json.dumps(activity_list, cls=DjangoJSONEncoder)
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
