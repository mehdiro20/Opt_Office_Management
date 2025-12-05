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
from django.contrib import admin
from .models import LensBrand, SpectacleLens, LensPowerRange,LensFeature,SelectedSpectacleLens
from .forms import SpectacleLensForm

from django.contrib import admin
from .models import SpectacleFrame


from django.contrib import admin
from .models import SpectacleFrame, FrameColor


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


# ----------------------------
# 1) Power Range Inline
# ----------------------------
class LensPowerRangeInline(admin.TabularInline):
    model = LensPowerRange
    extra = 1

    fields = (
        'minus_sphere_group', 'plus_sphere_group',
        'minus_cylinder_group', 'plus_cylinder_group',
      
        'price',
        'notes'
    )


# ----------------------------
# 2) Lens Feature Admin
# ----------------------------
@admin.register(LensFeature)
class LensFeatureAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# ----------------------------
# 3) Spectacle Lens Admin
# ----------------------------
@admin.register(SpectacleLens)
class SpectacleLensAdmin(admin.ModelAdmin):
    
    form = SpectacleLensForm
   
    class Media:
        js = (
            "doctor/admin/tint_toggle10.js",
            "doctor/admin/material5.js",
        )
    list_display = (
        'brand','distributer', 'model_name','title','design',
        'lens_type', 'refractive_index',
        'material', 'base_price', 'availability'
    )

    list_filter = (
        'brand','distributer','title','design', 'lens_type', 'material',
        'refractive_index', 'availability'
    )

    search_fields = ('model_name','title', 'brand__name')

    inlines = [LensPowerRangeInline]

    fieldsets = (
        ("Basic Info", {
            'fields': (
                'brand', 'distributer','model_name','title','design',
                'lens_type',
                ('material','other_material'),
                
                'base_price',
                'availability',
                'remarkable_lens'
            )
        }),

        ("Optical Attributes", {
            'fields': (
                ('refractive_index',),
                ('basecurve',),
                ('tintable', 'tintcolors'),
                ('antireflex', 'antireflexcolor','antireflexfeature'),
                ('hydrophobe', 'hydrophobe_features'),

                ('uv_protection', 'uv400', 'uvblocking_features'),
                ('blue_light_filter','bluecontrol','bluecut','coating_features'),
                ('photochromic','transition','rayblock_precentage','photochromic_features',),
                ('polarized',),
                ('antiscratch', 'hard_coating'),
                ('occupational_lens', 'protections_features','best_occupational_use'),
                ('special_coatings'),
                ('diameter_mm',)
            ),
            'classes': ('collapse',),
        }),
        
        ("Progressives", {
            'fields': ('addition_range',),
            'classes': ('collapse',),
        }),
        
        
        
        
        ("Unique Features", {
            'fields': ('features',),
            'classes': ('collapse',),
        }),
    )

    filter_horizontal = ('features',)
  
# ----------------------------
# 4) Inline Lens list in Brand
# ----------------------------
class SpectacleLensInline(admin.TabularInline):
    model = SpectacleLens
    extra = 1
    show_change_link = True

    fields = (
        'model_name', 'lens_type','title',
        'refractive_index', 'material',
        'base_price', 'availability'
    )


@admin.register(LensBrand)
class LensBrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'website')
    search_fields = ('name', 'country')
    inlines = [SpectacleLensInline]
@admin.register(LensPowerRange)
class LensPowerRangeAdmin(admin.ModelAdmin):
    list_display = ('unique_slens_id', 'lens', 'price')
    readonly_fields = ('unique_slens_id',)
    class Media:
        js = ("doctor/admin/tint_toggle10.js",)   # load our custom JS
        
@admin.register(SelectedSpectacleLens)
class SelectedSpectacleLensAdmin(admin.ModelAdmin):
    list_display = ('title','eye','patient_id', 'refraction_id', 'unique_slens_id')



# Inline for frame colors
class FrameColorInline(admin.TabularInline):
    model = FrameColor
    extra = 1
    fields = ("color_name", "quantity", "hex_code")
    show_change_link = True

@admin.register(SpectacleFrame)
class SpectacleFrameAdmin(admin.ModelAdmin):
    list_display = (
        "unique_frame_id",
        "brand",
        "model_code",
        "material",
        "gender",
        "price",
        "total_stock",
        "created_at",
    )
    list_filter = ("brand", "material", "gender")
    search_fields = ("unique_frame_id", "brand", "model_code")
    ordering = ("-id",)
    readonly_fields = ("unique_frame_id", "created_at", "updated_at")

    inlines = [FrameColorInline]

    # Compute total stock across all colors
    def total_stock(self, obj):
        return sum(color.quantity for color in obj.colors.all())
    total_stock.short_description = "Total Stock"

    # ----------------------------
    # Load custom JS for admin
    # ----------------------------
    class Media:
        js = ("doctor/admin/frame_other_field_selected.js",)
