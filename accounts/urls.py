# -*- coding: utf-8 -*-
"""
Created on Sun Aug 31 13:05:18 2025

@author: Mehdi
"""

from django.urls import path
from . import views
from .views import login_view

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    
    path("doctor_dashboard/", views.doctor_dashboard, name="doctor_dashboard")

]