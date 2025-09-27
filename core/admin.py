from django.contrib import admin
from .models import SiteSetting

# Register your models here.

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("site_name", "theme_color", "maintenance_mode","pp_button_color")