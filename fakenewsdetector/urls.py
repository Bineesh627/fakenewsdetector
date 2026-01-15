from django.contrib import admin
from django.urls import path
from detector.views import home, signup, login_view, feedback_view, vote, predictions_list, prediction_detail
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('feedback/<int:pred_id>/', feedback_view, name='feedback'),
    path('vote/<int:pred_id>/<str:vote_type>/', vote, name='vote'),
    path('predictions/', predictions_list, name='predictions_list'),
    path('prediction/<int:pred_id>/', prediction_detail, name='prediction_detail'),
]
