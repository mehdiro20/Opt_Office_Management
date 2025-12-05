# doctor/models.py
from django.db import models
from secretary.models import Patient  # your existing Patient model
import uuid
import jdatetime
import pytz
from django.db import models, transaction
from django.utils import timezone
# -------------------- Refraction --------------------
class Refraction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, to_field='patient_id', db_column='patient_id', on_delete=models.CASCADE, related_name='refractions')
    subject = models.CharField(max_length=50)
    od = models.CharField(max_length=50)
    oducva = models.CharField(max_length=50, null=True, blank=True)
    odbcva = models.CharField(max_length=50, null=True, blank=True)
    os = models.CharField(max_length=50)
    osucva = models.CharField(max_length=50, null=True, blank=True)
    osbcva = models.CharField(max_length=50, null=True, blank=True)
    odcl = models.CharField(max_length=50)
    oscl = models.CharField(max_length=50)
    addition = models.CharField(max_length=50, null=True, blank=True)
    pd = models.CharField(max_length=50)
    odkmax=models.CharField(max_length=50, null=True, blank=True)
    odkmin=models.CharField(max_length=50, null=True, blank=True)
    oskmax=models.CharField(max_length=50, null=True, blank=True)
    oskmin=models.CharField(max_length=50, null=True, blank=True)
    refraction_id = models.CharField(max_length=50, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refraction for {self.patient.name} ({self.created_at.strftime('%Y-%m-%d')})"

    @property
    def created_at_tehran_jalali(self):
        tehran_tz = pytz.timezone('Asia/Tehran')
        tehran_dt = self.created_at.astimezone(tehran_tz)
        jalali_dt = jdatetime.datetime.fromgregorian(datetime=tehran_dt)
        return jalali_dt.strftime('%Y-%m-%d %H:%M:%S')


# -------------------- Optics --------------------
class Optics(models.Model):
    patient = models.ForeignKey(Patient, to_field='patient_id', db_column='patient_id', on_delete=models.CASCADE, related_name='optics')
    brand_name_frame = models.CharField(max_length=50)
    brand_name_lens = models.CharField(max_length=50)
    frame_type = models.CharField(max_length=50)
    frame_size = models.CharField(max_length=50)
    frame_base = models.CharField(max_length=50)
    photochromic = models.CharField(max_length=50)
    photochromic_color = models.CharField(max_length=50)
    n_index = models.CharField(max_length=50)
    coating = models.CharField(max_length=50)
    sized_lens = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Optics for {self.patient.name} ({self.created_at.strftime('%Y-%m-%d')})"


# -------------------- Brands Frames --------------------
class BrandsFrames(models.Model):
    brand_name = models.CharField(max_length=50)
    brand_img = models.ImageField(upload_to="frames/")
    brand_material = models.CharField(max_length=50)
    brand_type = models.CharField(max_length=50)
    brand_size = models.CharField(max_length=50)
    brand_price = models.DecimalField(max_digits=10, decimal_places=2)
    brand_avg_age = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand_name} ({self.brand_material}, {self.brand_type})"


# -------------------- Brands Splenss --------------------
class BrandsSplenss(models.Model):
    brand_name = models.CharField(max_length=50)
    brand_img = models.ImageField(upload_to="splens/")
    brand_material = models.CharField(max_length=50)
    brand_index = models.CharField(max_length=50)
    brand_color = models.CharField(max_length=50)
    brand_coating = models.CharField(max_length=50)
    brand_price = models.DecimalField(max_digits=10, decimal_places=2)
    brand_avg_age = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand_name} ({self.brand_material}, {self.brand_color})"


# -------------------- Brand Price --------------------
class BrandPrice(models.Model):
    brand = models.ForeignKey(BrandsSplenss, on_delete=models.CASCADE, related_name='prices')
    description = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"{self.brand.brand_name} - {self.description}: {self.price}"


# -------------------- Optics Feature --------------------
class OpticsFeature(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# -------------------- Optics Description --------------------
class OpticsDescription(models.Model):
    patient = models.ForeignKey(Patient, to_field='patient_id', db_column='patient_id', on_delete=models.CASCADE, related_name='optics_descriptions')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Optics Description for {self.patient.name}"


# -------------------- Orders --------------------
class Order(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Register_Order(models.Model):
    patient = models.ForeignKey(Patient, to_field='patient_id', db_column='patient_id', on_delete=models.CASCADE, related_name='register_orders')
    order_name = models.CharField(max_length=200)
    duration = models.PositiveIntegerField(null=True, blank=True)
    priority = models.CharField(max_length=20)
    unique_id = models.CharField(max_length=50, unique=True)
    start_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.order_name} for {self.patient.name}"
class GH_HealthCondition(models.Model):
    name = models.CharField(max_length=100)
    related_px = models.ForeignKey(Patient,to_field='patient_id',on_delete=models.CASCADE, null=True, blank=True)
class  GH_Medication(models.Model):
    name = models.CharField(max_length=100)
    related_px = models.ForeignKey(Patient,to_field='patient_id',on_delete=models.CASCADE, null=True, blank=True)
class  GH_Allergies(models.Model):
    name = models.CharField(max_length=100)
    related_px = models.ForeignKey(Patient,to_field='patient_id',on_delete=models.CASCADE, null=True, blank=True)
class  GH_FamilialHistory(models.Model):
    name = models.CharField(max_length=100)
    related_px = models.ForeignKey(Patient,to_field='patient_id',on_delete=models.CASCADE, null=True, blank=True)
class  GH_GeneticalHistory(models.Model):
    name = models.CharField(max_length=100)
    related_px = models.ForeignKey(Patient,to_field='patient_id',on_delete=models.CASCADE, null=True, blank=True)
class  GH_LifestyleHistory(models.Model):
    name = models.CharField(max_length=100)
    related_px = models.ForeignKey(Patient,to_field='patient_id',on_delete=models.CASCADE, null=True, blank=True)
class  GH_OcularHistory(models.Model):
    name = models.CharField(max_length=100)
    related_px = models.ForeignKey(Patient,to_field='patient_id',on_delete=models.CASCADE, null=True, blank=True)
class GeneralHealthRecord(models.Model):
    patient = models.ForeignKey(
        Patient,
        to_field='patient_id',
        db_column='patient_id',
        on_delete=models.CASCADE,
        related_name='general_health_records'
    )
    systemic_diseases = models.TextField(blank=True, null=True)
    ocular_history = models.TextField(blank=True, null=True)
    medications = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    familial_history = models.TextField(blank=True, null=True)
    genetical_history = models.TextField(blank=True, null=True)
    lifestyle_history = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.name} — General Health Record"
    
    
  
class  ImpMenuParts(models.Model):
    patient = models.ForeignKey(Patient, to_field='patient_id', db_column='patient_id', on_delete=models.CASCADE, related_name='ImpMenuParts')
    imp_menu_parts = models.CharField(max_length=200)


# ---------------------------
# 1) Lens Brand
# ---------------------------
from decimal import Decimal
from django.db import models



class LensBrand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    remarkable_brand = models.BooleanField(default=False)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # One-time percent increase
    price_increase_percent = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        help_text="Enter percent to increase all prices one time"
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        # Store value before save
  

        old_percent = None
        if self.pk:
            old = LensBrand.objects.get(pk=self.pk)
            
            old_percent = old.price_increase_percent

        super().save(*args, **kwargs)

        # If new value is zero or unchanged → do nothing
        if not self.price_increase_percent or self.price_increase_percent == old_percent:
            return

        increase_percent = Decimal(self.price_increase_percent)

        # Import here to avoid circular dependency

        # ----------------------------------------------------
        # Update SpectacleLens.base_price
        # ----------------------------------------------------
        lenses = SpectacleLens.objects.filter(brand=self)

        for lens in lenses:
            clean = str(lens.base_price).replace(",", "")
            if clean.isdigit():
                value = Decimal(clean)
                value = value + (value * increase_percent / 100)

                lens.base_price = f"{int(value):,}"
                lens.save(update_fields=['base_price'])

        # ----------------------------------------------------
        # Update LensPowerRange.price
        # ----------------------------------------------------
        ranges = LensPowerRange.objects.filter(lens__brand=self)

        for rng in ranges:
            clean = str(rng.price).replace(",", "")
            if clean.isdigit():
                value = Decimal(clean)
                value = value + (value * increase_percent / 100)

                rng.price = f"{int(value):,}"
                rng.save(update_fields=['price'])

        # ----------------------------------------------------
        # Finally reset percent to zero
        # ----------------------------------------------------
        self.price_increase_percent = 0
        super().save(update_fields=['price_increase_percent'])

class LensFeature(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# ---------------------------
# 3) Main Lens Model
# ---------------------------
class SpectacleLens(models.Model):
    LENS_TYPES = [
        ('unknown', 'Unknown'),
        ('single_vision', 'Single Vision'),
        ('bifocal', 'Bifocal'),
        ('progressive', 'Progressive'),
        ('photochromic', 'Photochromic'),
        ('polarized', 'Polarized'),
        ('other', 'Other')
    ]

    MATERIALS = [
        ('unknown', 'Unknown'),
        ('cr39', 'CR-39'),
        ('polycarbonate', 'Polycarbonate'),
        ('trivex', 'Trivex'),
        ('high_index', 'High Index'),
        ('glass', 'Glass'),
        ('other', 'Other'),
    ]

    brand = models.ForeignKey(
        LensBrand,
        on_delete=models.CASCADE,
        related_name="lenses"
    )

    model_name = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    design=models.CharField(max_length=100, blank=True, null=True)
    distributer=models.CharField(max_length=100, blank=True, null=True)
    lens_type = models.CharField(max_length=50, choices=LENS_TYPES, default="single_vision")
    refractive_index = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    material = models.CharField(max_length=50, choices=MATERIALS, blank=True)
    other_material = models.CharField(max_length=50, blank=True, null=True)
    special_coatings = models.CharField(max_length=100, blank=True)

    # Optical features
    basecurve=models.CharField(max_length=50, blank=True, null=True)
    tintable = models.BooleanField(default=False)
    tintcolors = models.CharField(max_length=50, blank=True, null=True)
    antireflex = models.BooleanField(default=False)
    antireflexcolor = models.CharField(max_length=50, blank=True, null=True)
    antireflexfeature = models.CharField(max_length=50, blank=True, null=True)

    hydrophobe = models.BooleanField(default=False)
    hydrophobe_features = models.CharField(max_length=50, blank=True, null=True)
    
    
    uv_protection = models.BooleanField(default=False)
    uv400 = models.BooleanField(default=False)
    uvblocking_features = models.CharField(max_length=50, blank=True, null=True)
    blue_light_filter = models.BooleanField(default=False)
    bluecontrol = models.BooleanField(default=False)
    bluecut = models.BooleanField(default=False)
    coating_features = models.CharField(max_length=50, blank=True, null=True)
    photochromic = models.BooleanField(default=False)
    rayblock_precentage = models.CharField(max_length=50, blank=True, null=True)
    photochromic_features = models.CharField(max_length=50, blank=True, null=True)

    transition = models.BooleanField(default=False)
    polarized = models.BooleanField(default=False)
    hard_coating = models.BooleanField(default=False)
    antiscratch = models.BooleanField(default=False)

    occupational_lens = models.BooleanField(default=False)
    protections_features = models.CharField(max_length=50, blank=True, null=True)
    best_occupational_use=models.CharField(max_length=50, blank=True, null=True)
    diameter_mm = models.PositiveIntegerField(blank=True, null=True)
    addition_range=models.CharField(max_length=50, blank=True, null=True)
    # base price stored as formatted string
    base_price = models.CharField(max_length=50, default="0")
    availability = models.BooleanField(default=True)
    remarkable_lens=models.BooleanField(default=False)
    # Many-to-many to features
    features = models.ManyToManyField(LensFeature, blank=True, related_name="lenses")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['brand', 'model_name']

    def __str__(self):
        return f"{self.brand.name} - {self.model_name}"

    def save(self, *args, **kwargs):
        # Format base_price with commas before saving
        if self.base_price:
            numeric_value = str(self.base_price).replace(",", "")
            if numeric_value.isdigit():
                self.base_price = f"{int(numeric_value):,}"
        super().save(*args, **kwargs)


# ---------------------------
# 4) Power Limitations + Price per Range
# ---------------------------
class LensPowerRange(models.Model):
    lens = models.ForeignKey(
        SpectacleLens,
        on_delete=models.CASCADE,
        related_name="power_ranges"
    )

    # Short auto-increment unique ID
    unique_slens_id = models.CharField(max_length=50, unique=True, editable=False)

    minus_sphere_group = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    plus_sphere_group = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    minus_cylinder_group = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    plus_cylinder_group = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

    # price stored as formatted string
    price = models.CharField(max_length=50, default="0")
    notes = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):

        # -------------------------------------------------
        # Generate unique short ID
        # -------------------------------------------------
        if not self.unique_slens_id:
            last = LensPowerRange.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.unique_slens_id = f"LPR-{next_id:06d}"

        # -------------------------------------------------
        # Format price with commas
        # -------------------------------------------------
        if self.price:
            numeric_value = str(self.price).replace(",", "")
            if numeric_value.isdigit():
                self.price = f"{int(numeric_value):,}"

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.lens.model_name} | "
            f"Price: {self.price} | "
            f"ID: {self.unique_slens_id}"
        )

class SelectedSpectacleLens(models.Model):
    
    patient = models.ForeignKey(
        Patient,
        to_field='patient_id',
        db_column='patient_id',
        on_delete=models.CASCADE,
        related_name='selected_spectacle_lens'
    )
     
    refraction_id = models.CharField(max_length=50)

    unique_slens_id = models.CharField(max_length=50)
    
    eye= models.CharField(max_length=10)
    
    title=  models.CharField(max_length=50)
    
    


class SpectacleFrame(models.Model):
    MATERIAL_CHOICES = [
        ("metal", "Metal"),
        ("plastic", "Plastic"),
        ("titanium", "Titanium"),
        ("wood", "Wood"),
        ("other", "Other"),
    ]

    GENDER_CHOICES = [
        ("men", "Men"),
        ("women", "Women"),
        ("unisex", "Unisex"),
        ("kids", "Kids"),
    ]

    # Auto-generated unique frame ID
    unique_frame_id = models.CharField(max_length=50, unique=True, editable=False)

    # Frame information
    model_code = models.CharField(max_length=50, unique=True, verbose_name="Model Code")
    brand = models.CharField(max_length=100, verbose_name="Brand")
    material = models.CharField(max_length=20, choices=MATERIAL_CHOICES, verbose_name="Frame Material")
    other_material_details = models.CharField(max_length=100, blank=True, null=True)
    
    
    
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="Target Gender")
    # Spectacle dispensing measurements
    a = models.PositiveIntegerField(blank=True, null=True, verbose_name="A (Lens Width / Eye Size) mm")
    b = models.PositiveIntegerField(blank=True, null=True, verbose_name="B (Lens Height) mm")
    dbl = models.PositiveIntegerField(blank=True, null=True, verbose_name="DBL (Bridge Width) mm")
    ed = models.PositiveIntegerField(blank=True, null=True, verbose_name="ED (Effective Diameter) mm")
    temple_length = models.PositiveIntegerField(blank=True, null=True, verbose_name="Temple / Arm Length mm")

    # Price (general or default)
    price = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2, verbose_name="Price")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    # -------------------------------------------------
    # Auto-generate unique Frame ID
    # -------------------------------------------------
    def save(self, *args, **kwargs):
        if not self.unique_frame_id:
            with transaction.atomic():
                last = SpectacleFrame.objects.all().order_by('id').last()
                next_id = (last.id + 1) if last else 1
                self.unique_frame_id = f"FRM-{next_id:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} - {self.model_code} | ID: {self.unique_frame_id}"


# -------------------------------------------------
# Frame colors with individual quantities
# -------------------------------------------------
class FrameColor(models.Model):
    frame = models.ForeignKey(SpectacleFrame, on_delete=models.CASCADE, related_name="colors")
    color_name = models.CharField(max_length=50, verbose_name="Color Name")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Quantity / Stock")
    hex_code = models.CharField(max_length=7, blank=True, null=True, verbose_name="Hex Code (#RRGGBB)")

    class Meta:
        unique_together = ("frame", "color_name")  # Ensure no duplicate colors for same frame

    def __str__(self):
        return f"{self.frame.model_code} - {self.color_name} ({self.quantity})"
