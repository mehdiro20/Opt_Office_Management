from django.contrib import admin
from .models import Patient

# Unregister if already registered
try:
    admin.site.unregister(Patient)
except admin.sites.NotRegistered:
    pass


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'phone', 'reason', 'status', 'updated_date')  # ✅ added updated_date
    list_filter = ('status', 'updated_date')  # ✅ optional: filter by update time
    search_fields = ('name', 'patient_id', 'phone', 'melli_code')

    # Optional: make updated_date read-only in admin form
    readonly_fields = ('updated_date', 'created_at')