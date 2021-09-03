from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import LoanRequestForm
from .models import loanRequest
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, HttpResponse
# Create your views here.


# @login_required(login_url='/account/login-customer')
def home(request):

    return render(request, 'home.html', context={})


@login_required()
def LoanRequest(request):
    print(request.user)
    form = LoanRequestForm()

    if request.method == 'POST':
        form = LoanRequestForm(request.POST)
        print(form)
        if form.is_valid():
            loan_obj = form.save(commit=False)
            loan_obj.customer = request.user.customer
            loan_obj.save()
            return redirect('/')

    return render(request, 'loanApp/loanrequest.html', context={'form': form})

    # reason = request.POST.get('reason')
    # amount = request.POST.get('amount')
    # category = request.POST.get('category')
    # year = request.POST.get('year')
    # customer = request.user.customer

    # loan_request = LoanRequest(request)
    # loan_request.customer = customer
    # loan_request.save()
    # if form.is_valid():
    #     loan_request = form.save(commit=False)
    #     loan_request.customer = request.user.customer
    #     print(loan_request)
    #     return redirect('/')
