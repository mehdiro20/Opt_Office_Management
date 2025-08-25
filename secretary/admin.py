# -*- coding: utf-8 -*-
"""
Created on Thu Aug 21 12:44:54 2025

@author: Mehdi
"""
from django.contrib import admin
from .models import Patient

# Unregister if already registered
try:
    admin.site.unregister(Patient)
except admin.sites.NotRegistered:
    pass

class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'phone', 'reason', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'patient_id')

admin.site.register(Patient, PatientAdmin)
