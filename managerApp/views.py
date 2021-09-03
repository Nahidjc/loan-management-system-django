from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from managerApp.forms import AdminLoginForm
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from loanApp.models import loanCategory, loanRequest
from .forms import LoanCategoryForm
from loginApp.models import CustomerSignUp
from django.contrib.auth.models import User
# Create your views here.
# Create your views here.


def superuser_login_view(request):
    form = AdminLoginForm()
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))
    else:
        if request.method == 'POST':
            form = AdminLoginForm(data=request.POST)

            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']

                user = authenticate(
                    request, username=username, password=password)

                if user is not None:

                    if user.is_superuser:
                        login(request, user)
                        return HttpResponseRedirect(reverse('managerApp:dashboard'))
                    else:
                        return render(request, 'admin/adminLogin.html', context={'form': form, 'error': "You are not Super User"})

            else:
                print("invalid password")
                return render(request, 'admin/adminLogin.html', context={'form': form, 'error': "Invalid Username or Password "})
    return render(request, 'admin/adminLogin.html', context={'form': form, 'user': "Admin Login"})


# @user_passes_test(lambda u: u.is_superuser)
@staff_member_required(login_url='/manager/admin-login')
def dashboard(request):
    return render(request, 'admin/dashboard.html', context={})


@staff_member_required(login_url='/manager/admin-login')
def add_category(request):
    form = LoanCategoryForm()
    if request.method == 'POST':
        form = LoanCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('managerApp:dashboard')
    return render(request, 'admin/admin_add_category.html', {'form': form})


@staff_member_required(login_url='/manager/admin-login')
def total_users(request):
    users = CustomerSignUp.objects.all()

    return render(request, 'admin/customer.html', context={'users': users})


@staff_member_required(login_url='/manager/admin-login')
def user_remove(request, pk):
    CustomerSignUp.objects.get(id=pk).delete()
    user = User.objects.get(id=pk)
    user.delete()
    return HttpResponseRedirect('/manager/users')
    # return redirect('managerApp:users')


def loan_request(request):
    users = loanRequest.objects.all()
    return render(request, 'admin/request_user.html', context={'users': users, 'i': 1})
