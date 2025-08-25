
# Create your models here.
from django.db import models
from secretary.models import Patient  # link to your existing Patient model
import uuid

class Refraction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='refractions')
    od = models.CharField(max_length=50)
    os = models.CharField(max_length=50)
    axis = models.CharField(max_length=50)
    pd = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refraction for {self.patient.name} ({self.created_at.strftime('%Y-%m-%d')})"
