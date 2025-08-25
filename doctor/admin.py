from django.contrib import admin
from .models import Refraction

@admin.register(Refraction)
class RefractionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'od', 'os','axis','pd', 'created_at')
    list_filter = ('created_at', 'patient')
    search_fields = ('patient__name', 'patient__patient_id')
    

