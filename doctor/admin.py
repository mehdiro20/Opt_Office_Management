from django.contrib import admin
from .models import Refraction
from .models import BrandsFrames, BrandsSplenss
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import OpticsFeature

from .models import BrandsSplenss, BrandPrice
from .models import OpticsDescription
import os
from .models import Order
    
from .models import Register_Order
@admin.register(Refraction)
class RefractionAdmin(admin.ModelAdmin):
    list_display = ('subject','patient', 'od', 'os','axis','pd', 'created_at')
    list_filter = ('created_at', 'patient')
    search_fields = ('subject','patient__name', 'patient__patient_id')
    


@admin.register(BrandsFrames)
class BrandsFrameAdmin(admin.ModelAdmin):
    list_display = ("brand_name", "brand_material", "brand_type", "brand_size", "brand_price", "brand_avg_age", "created_at")
    search_fields = ("brand_name", "brand_material", "brand_type")
    list_filter = ("brand_material", "brand_type")
    ordering = ("-created_at",)



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



@admin.register(OpticsFeature)
class OpticsFeatureAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    
    
@receiver(post_delete, sender=BrandsSplenss)
def delete_brand_image_on_delete(sender, instance, **kwargs):
    if instance.brand_img:
        instance.brand_img.delete(save=False)
        
@receiver(pre_save, sender=BrandsSplenss)
def delete_old_brand_image_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return False  # skip for new objects (no old file exists)
    
    try:
        old_instance = BrandsSplenss.objects.get(pk=instance.pk)
    except BrandsSplenss.DoesNotExist:
        return False

    old_file = old_instance.brand_img
    new_file = instance.brand_img
    if old_file and old_file != new_file:
        if os.path.isfile(old_file.path):
            old_file.delete(save=False)
            
            



@admin.register(OpticsDescription)
class OpticsDescriptionAdmin(admin.ModelAdmin):
    list_display = ("id","patient_id", "description", "created_at")   # show these columns in the list
    search_fields = ("description",)                     # enable search by description
    list_filter = ("created_at",)               
            


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Register_Order)
class RegisterOrderAdmin(admin.ModelAdmin):
    list_display = ('patient_id','order_name', 'duration', 'priority', 'unique_id')    
    