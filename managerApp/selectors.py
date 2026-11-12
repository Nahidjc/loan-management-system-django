"""
Read-only data access for managerApp (the "selectors" layer).

Views used to call ``Model.objects.filter(...)`` and ``aggregate(...)``
directly, so the high-level screens depended on low-level ORM details
(Dependency Inversion Principle). Now views and services ask a selector for
data by NAME ("pending loans", "dashboard stats") and do not know how it is
fetched. If the query changes, only this file changes.

Writes (create / update / delete) stay in services.py.
"""
from django.contrib.auth.models import User
from django.db.models import Sum

from loanApp.models import CustomerLoan, loanRequest, loanTransaction
from loginApp.models import CustomerSignUp

from .constants import Status


def get_loan_request(loan_id):
    """One loan request; raises DoesNotExist for an unknown id (as before)."""
    return loanRequest.objects.get(id=loan_id)


def get_loan_requests_by_status(status):
    return loanRequest.objects.filter(status=status)


def get_pending_requests():
    return get_loan_requests_by_status(Status.PENDING)


def get_approved_requests():
    return get_loan_requests_by_status(Status.APPROVED)


def get_rejected_requests():
    return get_loan_requests_by_status(Status.REJECTED)


def get_all_customers():
    return CustomerSignUp.objects.all()


def get_customer(pk):
    return CustomerSignUp.objects.get(id=pk)


def get_user(pk):
    return User.objects.get(id=pk)


def get_all_transactions():
    return loanTransaction.objects.all()


def get_customer_balance(customer):
    """The customer's CustomerLoan row, or None when they have no balance."""
    try:
        return CustomerLoan.objects.get(customer=customer)
    except CustomerLoan.DoesNotExist:
        return None


def _total(model, field):
    """Sum of one column; None when the table is empty."""
    return model.objects.aggregate(total=Sum(field))['total']


def get_dashboard_stats():
    """All numbers shown on the manager dashboard, keyed as the template expects."""
    return {
        'totalCustomer': CustomerSignUp.objects.count(),
        'request': loanRequest.objects.filter(status=Status.PENDING).count(),
        'approved': loanRequest.objects.filter(status=Status.APPROVED).count(),
        'rejected': loanRequest.objects.filter(status=Status.REJECTED).count(),
        'totalLoan': _total(CustomerLoan, 'total_loan'),
        'totalPayable': _total(CustomerLoan, 'payable_loan'),
        'totalPaid': _total(loanTransaction, 'payment'),
    }
