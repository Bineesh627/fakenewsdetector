from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

# Helper function to check if user is staff (admin)
def is_staff(user):
    return user.is_authenticated and user.is_staff

@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home') # Redirect non-staff to home
def admin_dashboard(request):
    return render(request, 'admin/Dashboard.html')

@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_users(request):
    return render(request, 'admin/UsersManagement.html')

@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_activity(request):
    return render(request, 'admin/ActivityLogs.html')

@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_feedback(request):
    return render(request, 'admin/FeedbackManagement.html')

@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_predictions(request):
    return render(request, 'admin/PredictionsManagement.html')

@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def admin_settings(request):
    return render(request, 'admin/Settings.html')
