# detection/models.py
from django.db import models
from django.utils import timezone

class Detection(models.Model):
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    class_name = models.CharField(max_length=64)
    confidence = models.FloatField()
    bbox = models.JSONField()      # [x1, y1, x2, y2]
    location = models.JSONField(null=True, blank=True)  # {"lat": .., "lng": ..}
    raw = models.JSONField(null=True, blank=True)       # store extra metadata if needed

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.class_name} ({self.confidence:.2f}) @ {self.timestamp.isoformat()}"
