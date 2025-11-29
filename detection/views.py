# detection/views.py
from datetime import timedelta

from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required

from rest_framework.decorators import api_view

from .camera import gen_frames
from .models import Detection


# 🔐 Dashboard: only for logged-in users
@login_required  # will redirect to LOGIN_URL if not logged in
def dashboard(request):
    return render(request, "dashboard.html")


# 🎥 Live video feed
def video_feed(request):
    return StreamingHttpResponse(
        gen_frames(),
        content_type="multipart/x-mixed-replace; boundary=frame"
    )


# 🚨 Alerts: last 30 minutes (JSON)
@api_view(["GET"])
def latest_alerts(request):
    cutoff = now() - timedelta(minutes=30)
    qs = Detection.objects.filter(timestamp__gte=cutoff).order_by("-timestamp")[:200]

    data = []
    for d in qs:
        data.append({
            "timestamp": d.timestamp.isoformat(),
            "class": d.class_name,
            "confidence": d.confidence,
            "bbox": d.bbox,
            "location": d.location,
            "raw": d.raw,
        })
    return JsonResponse(data, safe=False)


# 📍 Latest location per class (JSON)
@api_view(["GET"])
def latest_locations(request):
    result = []
    for cls in ["animal", "human", "fire", "poaching"]:
        det = Detection.objects.filter(class_name__iexact=cls).order_by("-timestamp").first()
        if det:
            result.append({
                "_id": cls,
                "latest": {
                    "timestamp": det.timestamp.isoformat(),
                    "location": det.location,
                    "confidence": det.confidence,
                    "bbox": det.bbox,
                },
            })
    return JsonResponse(result, safe=False)
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, "dashboard.html")
