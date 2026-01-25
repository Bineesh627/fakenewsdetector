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
    path('admin-panel/users/add/', admin_views.admin_add_user, name='admin_add_user'),
    path('admin-panel/users/<int:user_id>/delete/', admin_views.admin_delete_user, name='admin_delete_user'),
    path('admin-panel/users/<int:user_id>/toggle-admin/', admin_views.admin_toggle_admin, name='admin_toggle_admin'),
    path('admin-panel/users/<int:user_id>/get/', admin_views.admin_get_user, name='admin_get_user'),
    path('admin-panel/users/<int:user_id>/edit/', admin_views.admin_edit_user, name='admin_edit_user'),
    path('admin-panel/activity/', admin_views.admin_activity, name='admin_activity'),
    path('admin-panel/feedback/', admin_views.admin_feedback, name='admin_feedback'),
    path('admin-panel/feedback/<int:feedback_id>/approve/', admin_views.admin_approve_feedback, name='admin_approve_feedback'),
    path('admin-panel/feedback/<int:feedback_id>/reject/', admin_views.admin_reject_feedback, name='admin_reject_feedback'),
    path('admin-panel/predictions/', admin_views.admin_predictions, name='admin_predictions'),
    path('admin-panel/predictions/export/', admin_views.admin_export_predictions, name='admin_export_predictions'),
    path('admin-panel/predictions/<int:pred_id>/get/', admin_views.admin_get_prediction, name='admin_get_prediction'),
    path('admin-panel/predictions/<int:pred_id>/edit/', admin_views.admin_edit_prediction, name='admin_edit_prediction'),
    path('admin-panel/predictions/<int:pred_id>/delete/', admin_views.admin_delete_prediction, name='admin_delete_prediction'),
    path('admin-panel/settings/', admin_views.admin_settings, name='admin_settings'),
]
