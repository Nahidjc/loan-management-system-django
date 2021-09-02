from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomerSignUp
from django import forms


class CustomerSignUpForm(UserCreationForm):
    # username = forms.CharField(required=True, label="Username", widget=forms.TextInput(
    #     attrs={'placeholder': 'username'}))
    # email = forms.EmailField(required=True, label="Email", widget=forms.EmailInput(
    #     attrs={'placeholder': 'Enter your Email'}))
    # password1 = forms.CharField(required=True, label="Password", widget=forms.PasswordInput(
    #     attrs={'placeholder': 'password'}))
    # password2 = forms.CharField(required=True, label="Password", widget=forms.PasswordInput(
    #     attrs={'placeholder': 'password'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class CustomerLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ('username', 'password')


class UpdateCustomerForm(forms.ModelForm):
    # information = forms.CharField(widget=forms.Textarea(attrs={"rows": 4, "cols": 10})
    information = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = CustomerSignUp
        exclude = ['user']
