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
from django.contrib import admin
from .models import  GH_HealthCondition,GH_Medication,GH_Allergies,GH_FamilialHistory,GH_GeneticalHistory,GH_LifestyleHistory,GH_OcularHistory    
from .models import Register_Order
from .models import GeneralHealthRecord
from .models import ImpMenuParts
@admin.register(Refraction)
class RefractionAdmin(admin.ModelAdmin):
    list_display = ('subject','patient', 'od', 'os','pd', 'created_at')
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
    


# Register HealthCondition
@admin.register( GH_HealthCondition)
class HealthConditionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# Register Medication
@admin.register( GH_Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
@admin.register( GH_FamilialHistory)
class FamilialHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register( GH_GeneticalHistory)
class GeneticalHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(GH_Allergies)
class AllergiesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    
    
@admin.register(GH_OcularHistory)
class OcularHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    
@admin.register(GH_LifestyleHistory)
class LifestyleHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    
    



@admin.register(GeneralHealthRecord)
class GeneralHealthRecordAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'patient',
        'systemic_diseases',
        'ocular_history',
        'medications',
        'allergies',
        'familial_history',
        'genetical_history',
        'lifestyle_history',
        'created_at',
    )
    list_filter = ('created_at',)
    search_fields = ('patient__patient_id', 'patient__name')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    
    
@admin.register(ImpMenuParts)
class ImpMenuPartsRecordAdmin(admin.ModelAdmin):
    list_display = ('patient','imp_menu_parts')
    search_fields = ('patient__patient_id', 'patient__name')
