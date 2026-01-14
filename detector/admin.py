from django.contrib import admin
from .models import Prediction

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('prediction', 'confidence', 'approved', 'created_at')
    list_filter = ('prediction', 'approved', 'created_at')
    search_fields = ('text', 'link_url')
    actions = ['approve_corrections']

    def approve_corrections(self, request, queryset):
        queryset.update(approved=True)
    approve_corrections.short_description = "Approve selected predictions for retraining"
