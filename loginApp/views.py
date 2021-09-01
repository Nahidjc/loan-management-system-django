from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import CustomerSignUpForm, CustomerLoginForm
from django.shortcuts import redirect
# Create your views here.


def sign_up_view(request):

    return render(request, 'base.html', context={})


def login_view(request):
    print("Login page")
    form = CustomerLoginForm()
    if request.method == 'GET':
        print('Get Method')
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
                return redirect('')
            else:
                return redirect('account/login-customer')

    else:
        print('Pai nai')
    return render(request, 'loginApp/login.html', context={'form': form})
