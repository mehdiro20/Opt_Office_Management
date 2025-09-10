# -*- coding: utf-8 -*-
"""
Created on Sun Aug 31 13:00:10 2025

@author: Mehdi
"""

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('secretary', 'Secretary'),
        ('doctor', 'Doctor'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='secretary')
    
    
    
    