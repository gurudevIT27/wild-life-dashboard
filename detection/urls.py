# detection/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),            
    path('video_feed/', views.video_feed, name='video_feed'),
    path('alerts/', views.latest_alerts, name='latest_alerts'),
    path('locations/', views.latest_locations, name='latest_locations'),
]


