from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django import forms


class AdminLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ('username', 'password')
