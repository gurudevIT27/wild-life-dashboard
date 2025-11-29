from django.contrib import admin
from .models import Detection


@admin.register(Detection)
class DetectionAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "class_name", "confidence", "short_location")
    list_filter = ("class_name",)
    search_fields = ("class_name",)
    ordering = ("-timestamp",)
    readonly_fields = ("timestamp",)

    def short_location(self, obj):
        loc = obj.location or {}
        lat = loc.get("lat")
        lng = loc.get("lng")
        if lat is None or lng is None:
            return "-"
        return f"{lat:.4f}, {lng:.4f}"

    short_location.short_description = "Location"




