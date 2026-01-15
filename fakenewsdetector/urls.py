from django.contrib import admin
from django.urls import path
from detector.views import home, signup, login_view, feedback_view, vote, predictions_list, prediction_detail
from detector import admin_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('feedback/<int:pred_id>/', feedback_view, name='feedback'),
    path('vote/<int:pred_id>/<str:vote_type>/', vote, name='vote'),
    path('predictions/', predictions_list, name='predictions_list'),
    path('predictions/', predictions_list, name='predictions_list'),
    path('prediction/<int:pred_id>/', prediction_detail, name='prediction_detail'),

    # Admin Panel URLs
    path('admin-panel/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', admin_views.admin_users, name='admin_users'),
    path('admin-panel/activity/', admin_views.admin_activity, name='admin_activity'),
    path('admin-panel/feedback/', admin_views.admin_feedback, name='admin_feedback'),
    path('admin-panel/predictions/', admin_views.admin_predictions, name='admin_predictions'),
    path('admin-panel/settings/', admin_views.admin_settings, name='admin_settings'),
]
