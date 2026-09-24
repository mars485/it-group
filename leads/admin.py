from django.contrib import admin
from .models import Lead
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "company", "project_type", "created_at")
    list_filter = ("project_type", "created_at")
    search_fields = ("name", "phone", "company", "description")
    readonly_fields = ("created_at", "source")
