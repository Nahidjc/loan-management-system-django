from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from loanApp.models import CustomerLoan, loanRequest, loanTransaction
from loginApp.models import CustomerSignUp

from .constants import Endpoints, Messages, Status, Templates
from .forms import AdminLoginForm, LoanCategoryForm
from .services import (
    approve_loan, authenticate_superuser, reject_loan, remove_customer,
)


def _pending_requests_page(request):
    """Render the pending-requests page (shown after approve and reject)."""
    pending = loanRequest.objects.filter(status=Status.PENDING)
    return render(request, Templates.REQUEST_USER,
                  context={'loanrequest': pending})


def superuser_login_view(request):
    form = AdminLoginForm()
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse(Endpoints.HOME))

    if request.method == 'POST':
        form = AdminLoginForm(data=request.POST)

        if form.is_valid():
            user, error = authenticate_superuser(
                request,
                form.cleaned_data['username'],
                form.cleaned_data['password'])

            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse(Endpoints.DASHBOARD))
            if error:
                return render(request, Templates.ADMIN_LOGIN,
                              context={'form': form, 'error': error})
        else:
            return render(request, Templates.ADMIN_LOGIN,
                          context={'form': form,
                                   'error': Messages.INVALID_LOGIN})
    return render(request, Templates.ADMIN_LOGIN,
                  context={'form': form, 'user': "Admin Login"})


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
    remove_customer(pk)
    return HttpResponseRedirect(Endpoints.USERS_REDIRECT)


@staff_member_required(login_url=Endpoints.LOGIN_URL)
def loan_request(request):
    loanrequest = loanRequest.objects.filter(status=Status.PENDING)
    return render(request, Templates.REQUEST_USER, context={'loanrequest': loanrequest})


@staff_member_required(login_url=Endpoints.LOGIN_URL)
def approved_request(request, id):
    approve_loan(id)
    return _pending_requests_page(request)


@staff_member_required(login_url=Endpoints.LOGIN_URL)
def rejected_request(request, id):
    reject_loan(id)
    return _pending_requests_page(request)


@staff_member_required(login_url=Endpoints.LOGIN_URL)
def approved_loan(request):
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
