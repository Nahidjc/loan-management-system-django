from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import LoanRequestForm
# Create your views here.


# @login_required(login_url='/account/login-customer')
def home(request):

    return render(request, 'home.html', context={})


@login_required()
def LoanRequest(request):
    form = LoanRequestForm()
    return render(request, 'loanApp/loanrequest.html', context={'form': form})
