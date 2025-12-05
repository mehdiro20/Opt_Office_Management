# -*- coding: utf-8 -*-
"""
Created on Fri Nov 21 04:17:56 2025

@author: Mehdi
"""

from django import forms
from .models import SpectacleLens

class SpectacleLensForm(forms.ModelForm):
    class Meta:
        model = SpectacleLens
        fields = "__all__"

        # 👇 Turn material from dropdown to free-text box
        widgets = {
            "material": forms.TextInput()
        }

    # 👇 Allow anything as valid value
    def clean_material(self):
        return self.cleaned_data["material"]