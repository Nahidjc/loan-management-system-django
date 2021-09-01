from django.shortcuts import render
from .forms import CustomerSignUpForm, CustomerLoginForm
# Create your views here.


def sign_up_view(request):

    return render(request, 'base.html', context={})


def login_view(request):
    return render(request, 'base.html', context={})
