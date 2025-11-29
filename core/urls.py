# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from detection import views as detection_views

urlpatterns = [
    # Auth routes
    path("login/",  auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Dashboard (home) – protected with @login_required in views.py
    path("", detection_views.dashboard, name="dashboard"),

    # Django admin (database)
    path("admin/", admin.site.urls),

    # API routes: /api/video_feed/, /api/alerts/, /api/locations/
    path("api/", include("detection.urls")),
]
