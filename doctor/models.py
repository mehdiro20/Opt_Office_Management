# doctor/models.py
from django.db import models
from secretary.models import Patient  # your existing Patient model
import uuid
import jdatetime
import pytz

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
    axis = models.CharField(max_length=50)
    pd = models.CharField(max_length=50)
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
