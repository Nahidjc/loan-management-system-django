from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from .forms import CustomerSignUpForm, CustomerLoginForm
from django.shortcuts import redirect
from .models import CustomerSignUp
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
# Create your views here.


def sign_up_view(request):
    form = CustomerSignUpForm()
    if request.method == 'POST':
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(user)
            print("valid form")
            # username = form.cleaned_data['username']
            # email = form.cleaned_data['email']
            # password1 = form.cleaned_data['password1']
            # password2 = form.cleaned_data['password2']
            user_profile = CustomerSignUp(user=user)
            user_profile.save()
            print(user_profile)
            return HttpResponseRedirect(reverse('login_App:login_customer'))
    return render(request, 'loginApp/signup.html', context={'form': form})


def login_view(request):
    form = CustomerLoginForm()
    # if request.method == 'GET':
    #     print('Get Method')
    if request.method == 'POST':
        form = CustomerLoginForm(data=request.POST)
        # username = request.POST['username']
        # password = request.POST['password']
        # print(username, password)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print('Username: %s Password: %s' % (username, password))
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('home'))

    else:
        print('Pai nai')
    return render(request, 'loginApp/login.html', context={'form': form})


@login_required()
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))
