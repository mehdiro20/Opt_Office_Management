# -*- coding: utf-8 -*-
"""
Created on Tue Aug 19 05:49:40 2025

@author: Mehdi
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.doctor_dashboard, name='doctor_dashboard'),

    

    path('profile/<str:patient_id>/', views.patient_profile, name='patient_profile'),
    path('submit_refraction/<str:patient_id>/', views.submit_refraction, name='submit_refraction'),

    path('submit_refraction/<str:patient_id>/', views.submit_refraction, name='submit_refraction'),
    path('delete/<int:patient_id>/', views.delete_patient, name='delete_patient'),
    path('remove/<str:patient_id>/', views.remove_from_accepted, name='remove_from_accepted'),
    path('patients/', views.doctor_patient_list, name='doctor_patient_list'),
    # urls.py
    path('remove_from_accepted_profile/<str:patient_id>/', views.remove_from_accepted_profile, name='remove_from_accepted_profile'),

]
