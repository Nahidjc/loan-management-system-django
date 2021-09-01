from django.shortcuts import render

# Create your views here.


def home(request):
    print('This is a home page')
    return render(request, 'home.html', context={})


def LoanPage(request):
    return render(request, 'home.html', context={})
