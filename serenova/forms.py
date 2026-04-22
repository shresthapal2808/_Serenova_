from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models
from .models import COUNTRY_CHOICES

class CustomUserRegisterForm(UserCreationForm):
    country = forms.ChoiceField(choices=COUNTRY_CHOICES)
    phone = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'country', 'phone']



