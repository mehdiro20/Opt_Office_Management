# -*- coding: utf-8 -*-
"""
Created on Tue Sep 23 11:26:58 2025

@author: Mehdi
"""

# core/context_processors.py
from .models import SiteSetting

def site_settings(request):
    settings = SiteSetting.objects.first()
    return {"site_settings": settings}