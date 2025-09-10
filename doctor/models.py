
# Create your models here.
from django.db import models
from secretary.models import Patient  # link to your existing Patient model
import uuid

class Refraction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='refractions')
    od = models.CharField(max_length=50)
    os = models.CharField(max_length=50)
    odcl = models.CharField(max_length=50)
    oscl = models.CharField(max_length=50)
    axis = models.CharField(max_length=50)
    pd = models.CharField(max_length=50)
   
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refraction for {self.patient.name} ({self.created_at.strftime('%Y-%m-%d')})"

class Optics(models.Model):
    patient_id = models.CharField(max_length=50)
    brand_name_frame = models.CharField(max_length=50)
    brand_name_lens = models.CharField(max_length=50)
    frame_type = models.CharField(max_length=50)
    frame_size = models.CharField(max_length=50)
    frame_base = models.CharField(max_length=50)
    photochromic=models.CharField(max_length=50)
    photochromic_color=models.CharField(max_length=50)
    n_index = models.CharField(max_length=50)
    coating = models.CharField(max_length=50)
    sized_lens = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refraction for {self.patient.name} ({self.created_at.strftime('%Y-%m-%d')})"


class BrandsFrames(models.Model):
    brand_name = models.CharField(max_length=50)
    brand_img = models.ImageField(upload_to="frames/")  # stores image in MEDIA_ROOT/frames/
    brand_material = models.CharField(max_length=50)
    brand_type = models.CharField(max_length=50)
    brand_size = models.CharField(max_length=50)

    # Numeric fields
    brand_price = models.DecimalField(max_digits=10, decimal_places=2)  # e.g. 199.99
    brand_avg_age = models.PositiveIntegerField()  # e.g. recommended age group

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand_name} ({self.brand_material}, {self.brand_type})"


class BrandsSplenss(models.Model):
    brand_name = models.CharField(max_length=50)
    brand_img = models.ImageField(upload_to="splens/")  # stores image in MEDIA_ROOT/splens/
    brand_material = models.CharField(max_length=50)
    brand_index = models.CharField(max_length=50)
    brand_color = models.CharField(max_length=50)
    brand_coating = models.CharField(max_length=50)
    
    # Numeric fields
    brand_price = models.DecimalField(max_digits=10, decimal_places=2)
    brand_avg_age = models.PositiveIntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand_name} ({self.brand_material}, {self.brand_color})"
    
    
class BrandPrice(models.Model):
    brand = models.ForeignKey('BrandsSplenss', on_delete=models.CASCADE, related_name='prices')
    description = models.CharField(max_length=100, blank=True)  # e.g., "Single Vision", "Progressive"
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.brand.brand_name} - {self.description}: ${self.price}"    