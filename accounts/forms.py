# -*- coding: utf-8 -*-
"""
Created on Sun Aug 31 23:53:29 2025

@author: Mehdi
"""

# accounts/forms.py
from django import forms
from captcha.fields import CaptchaField
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    captcha = CaptchaField()  # this will automatically generate a CAPTCHA