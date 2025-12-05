from django import forms
from .models import SpectacleLens

class SpectacleLensForm(forms.ModelForm):
    class Meta:
            model = SpectacleLens
            fields = "__all__"
        
    def clean(self):
        cleaned_data = super().clean()
        material = cleaned_data.get("material")
        other_material = cleaned_data.get("other_material")
    
        # If "Other" is selected and user typed a value, overwrite material
        if material == "other" and other_material:
            cleaned_data["material"] = "other"
    
        return cleaned_data