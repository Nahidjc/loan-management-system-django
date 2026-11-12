from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from managerApp.forms import AdminLoginForm
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from loanApp.models import loanCategory, loanRequest, CustomerLoan, loanTransaction
from .forms import LoanCategoryForm
from loginApp.models import CustomerSignUp
from django.contrib.auth.models import User
from datetime import date

from django.db.models import Sum

from .constants import (
    Endpoints, Loan, Messages, STATUS_DATE_FORMAT, Status, Templates,
)
# Create your views here.
# Create your views here.


def superuser_login_view(request):
    form = AdminLoginForm()
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse(Endpoints.HOME))
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
                        return HttpResponseRedirect(reverse(Endpoints.DASHBOARD))
                    else:
                        return render(request, Templates.ADMIN_LOGIN, context={'form': form, 'error': Messages.NOT_SUPERUSER})

            else:

                return render(request, Templates.ADMIN_LOGIN, context={'form': form, 'error': Messages.INVALID_LOGIN})
    return render(request, Templates.ADMIN_LOGIN, context={'form': form, 'user': "Admin Login"})


# @user_passes_test(lambda u: u.is_superuser)
@staff_member_required(login_url=Endpoints.LOGIN_URL)
def dashboard(request):

    totalCustomer = CustomerSignUp.objects.all().count(),
    requestLoan = loanRequest.objects.all().filter(status=Status.PENDING).count(),
    approved = loanRequest.objects.all().filter(status=Status.APPROVED).count(),
    rejected = loanRequest.objects.all().filter(status=Status.REJECTED).count(),
    totalLoan = CustomerLoan.objects.aggregate(Sum('total_loan'))[
        'total_loan__sum'],
    totalPayable = CustomerLoan.objects.aggregate(
        Sum('payable_loan'))['payable_loan__sum'],
    totalPaid = loanTransaction.objects.aggregate(Sum('payment'))[
        'payment__sum'],

    dict = {
        'totalCustomer': totalCustomer[0],
        'request': requestLoan[0],
        'approved': approved[0],
        'rejected': rejected[0],
        'totalLoan': totalLoan[0],
        'totalPayable': totalPayable[0],
        'totalPaid': totalPaid[0],

    }
    print(dict)

    return render(request, Templates.DASHBOARD, context=dict)


@staff_member_required(login_url=Endpoints.LOGIN_URL)
def add_category(request):
    form = LoanCategoryForm()
    if request.method == 'POST':
        form = LoanCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(Endpoints.DASHBOARD)
    return render(request, Templates.ADD_CATEGORY, {'form': form})


@staff_member_required(login_url=Endpoints.LOGIN_URL)
def total_users(request):
    users = CustomerSignUp.objects.all()

    return render(request, Templates.CUSTOMERS, context={'users': users})


@staff_member_required(login_url=Endpoints.LOGIN_URL)
def user_remove(request, pk):
    CustomerSignUp.objects.get(id=pk).delete()
    user = User.objects.get(id=pk)
    user.delete()
    return HttpResponseRedirect(Endpoints.USERS_REDIRECT)
    # return redirect('managerApp:users')


@staff_member_required(login_url=Endpoints.LOGIN_URL)
def loan_request(request):
    loanrequest = loanRequest.objects.filter(status=Status.PENDING)
    return render(request, Templates.REQUEST_USER, context={'loanrequest': loanrequest})


@staff_member_required(login_url=Endpoints.LOGIN_URL)
def approved_request(request, id):
    today = date.today()
    status_date = today.strftime(STATUS_DATE_FORMAT)
    loan_obj = loanRequest.objects.get(id=id)
    loan_obj.status_date = status_date
    loan_obj.save()
    year = loan_obj.year

    approved_customer = loanRequest.objects.get(id=id).customer
    if CustomerLoan.objects.filter(customer=approved_customer).exists():

        # find previous amount of customer
        PreviousAmount = CustomerLoan.objects.get(
            customer=approved_customer).total_loan
        PreviousPayable = CustomerLoan.objects.get(
            customer=approved_customer).payable_loan

        # update balance
        CustomerLoan.objects.filter(
            customer=approved_customer).update(total_loan=int(PreviousAmount)+int(loan_obj.amount))
        CustomerLoan.objects.filter(
            customer=approved_customer).update(payable_loan=int(PreviousPayable)+int(loan_obj.amount)+int(loan_obj.amount)*Loan.ANNUAL_INTEREST_RATE*int(year))

    else:

        # request customer

        # CustomerLoan object create
        save_loan = CustomerLoan()

        save_loan.customer = approved_customer
        save_loan.total_loan = int(loan_obj.amount)
        save_loan.payable_loan = int(
            loan_obj.amount)+int(loan_obj.amount)*Loan.ANNUAL_INTEREST_RATE*int(year)
        save_loan.save()

    loanRequest.objects.filter(id=id).update(status=Status.APPROVED)
    loanrequest = loanRequest.objects.filter(status=Status.PENDING)
    return render(request, Templates.REQUEST_USER, context={'loanrequest': loanrequest})


@staff_member_required(login_url=Endpoints.LOGIN_URL)
def rejected_request(request, id):

    today = date.today()
    status_date = today.strftime(STATUS_DATE_FORMAT)
    loan_obj = loanRequest.objects.get(id=id)
    loan_obj.status_date = status_date
    loan_obj.save()
    # rejected_customer = loanRequest.objects.get(id=id).customer
    # print(rejected_customer)
    loanRequest.objects.filter(id=id).update(status=Status.REJECTED)
    loanrequest = loanRequest.objects.filter(status=Status.PENDING)
    return render(request, Templates.REQUEST_USER, context={'loanrequest': loanrequest})


@staff_member_required(login_url=Endpoints.LOGIN_URL)
def approved_loan(request):
    # print(datetime.now())
    approvedLoan = loanRequest.objects.filter(status=Status.APPROVED)
    return render(request, Templates.APPROVED_LOAN, context={'approvedLoan': approvedLoan})


@staff_member_required(login_url=Endpoints.LOGIN_URL)
def rejected_loan(request):
    rejectedLoan = loanRequest.objects.filter(status=Status.REJECTED)
    return render(request, Templates.REJECTED_LOAN, context={'rejectedLoan': rejectedLoan})


@staff_member_required(login_url=Endpoints.LOGIN_URL)
def transaction_loan(request):
    transactions = loanTransaction.objects.all()
    return render(request, Templates.TRANSACTION, context={'transactions': transactions})
