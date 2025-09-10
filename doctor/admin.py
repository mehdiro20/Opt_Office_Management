from django.contrib import admin
from .models import Refraction
from .models import BrandsFrames, BrandsSplenss
@admin.register(Refraction)
class RefractionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'od', 'os','axis','pd', 'created_at')
    list_filter = ('created_at', 'patient')
    search_fields = ('patient__name', 'patient__patient_id')
    


@admin.register(BrandsFrames)
class BrandsFrameAdmin(admin.ModelAdmin):
    list_display = ("brand_name", "brand_material", "brand_type", "brand_size", "brand_price", "brand_avg_age", "created_at")
    search_fields = ("brand_name", "brand_material", "brand_type")
    list_filter = ("brand_material", "brand_type")
    ordering = ("-created_at",)


from .models import BrandsSplenss, BrandPrice

# Inline admin for prices
class BrandPriceInline(admin.TabularInline):
    model = BrandPrice
    extra = 1  # Number of empty price forms shown by default
    fields = ('description', 'price')
    readonly_fields = ()
    show_change_link = True

# Admin for BrandsSplenss
@admin.register(BrandsSplenss)
class BrandsSplenssAdmin(admin.ModelAdmin):
    list_display = ('brand_name', 'brand_material', 'brand_color', 'brand_index', 'brand_avg_age')
    search_fields = ('brand_name', 'brand_material', 'brand_color')
    list_filter = ("brand_material","brand_index", "brand_color", "brand_coating")
    ordering = ("-created_at",)
    inlines = [BrandPriceInline]  # Add the inline here




