from django.db import models



class SiteSetting(models.Model):
    site_name = models.CharField(max_length=200, default="My Project")
    logo = models.ImageField(upload_to="logos/", blank=True, null=True)
    favicon = models.ImageField(upload_to="logos/",default="optomanage.png", blank=True, null=False)  # small icon for browser tab
    theme_color = models.CharField(max_length=20, default="#3498db")
    pp_button_color = models.CharField(max_length=20, default="#2980b9")
    maintenance_mode = models.BooleanField(default=False)

    def __str__(self):
        return "Site Settings"

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"