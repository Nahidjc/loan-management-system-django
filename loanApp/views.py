from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required(login_url='/account/login-customer')
def home(request):
    print('This is a home page')
    return render(request, 'admin/adminbase.html', context={})


def LoanPage(request):
    return render(request, 'home.html', context={})
