"""
Business rules for managerApp (the "services" layer).

Views used to do everything: parse the request, apply the interest rule,
update balances, change statuses and render. Here each business action is a
plain function that can be tested without an HTTP request, so a view only has
to call it and render the result (Single Responsibility Principle).

Reads go through selectors.py. Writes (create / update / delete) are still
done here with the ORM, so this layer is only partly decoupled from it.
"""
from datetime import date

from django.contrib.auth import authenticate
from django.db import transaction

from loanApp.models import CustomerLoan, loanRequest

from .constants import Loan, Messages, STATUS_DATE_FORMAT, Status
from .selectors import (
    get_customer, get_customer_balance, get_loan_request, get_user,
)


# --- authentication ---------------------------------------------------------

def authenticate_superuser(request, username, password):
    """Check credentials and the superuser rule.

    Returns a pair ``(user, error)``:
      * ``(user, None)``  - credentials are valid and the user is a superuser
      * ``(None, msg)``   - valid credentials but not a superuser
      * ``(None, None)``  - authentication failed
    """
    user = authenticate(request, username=username, password=password)
    if user is None:
        return None, None
    if not user.is_superuser:
        return None, Messages.NOT_SUPERUSER
    return user, None


# --- loan rules -------------------------------------------------------------

def calculate_interest(amount, years):
    """Simple annual interest: amount * rate * years (a float, as before)."""
    return int(amount) * Loan.ANNUAL_INTEREST_RATE * int(years)


def _stamp_status_date(loan):
    loan.status_date = date.today().strftime(STATUS_DATE_FORMAT)
    loan.save()


def _set_status(loan_id, status):
    loanRequest.objects.filter(id=loan_id).update(status=status)


@transaction.atomic
def approve_loan(loan_id):
    """Approve a loan request and add it to the customer's balance.

    Same behaviour as the original view: a customer with no balance gets one
    created; a customer with a balance has the amount (and amount plus
    interest) added to it. Fractions of a unit are truncated, because the
    balance columns are integer fields.

    Runs in ONE database transaction: the date stamp, the balance change and
    the status change all succeed together or none of them is saved.
    """
    loan = get_loan_request(loan_id)
    _stamp_status_date(loan)

    customer = loan.customer
    amount = int(loan.amount)
    interest = calculate_interest(amount, loan.year)

    existing = get_customer_balance(customer)
    if existing is not None:
        CustomerLoan.objects.filter(customer=customer).update(
            total_loan=int(existing.total_loan) + amount)
        CustomerLoan.objects.filter(customer=customer).update(
            payable_loan=int(int(existing.payable_loan) + amount + interest))
    else:
        CustomerLoan.objects.create(
            customer=customer,
            total_loan=amount,
            payable_loan=int(amount + interest))

    _set_status(loan_id, Status.APPROVED)


@transaction.atomic
def reject_loan(loan_id):
    """Reject a loan request. No balance is created or changed."""
    loan = get_loan_request(loan_id)
    _stamp_status_date(loan)
    _set_status(loan_id, Status.REJECTED)


# --- user management --------------------------------------------------------

def remove_customer(pk):
    """Delete a customer profile and its login account.

    NOTE: as in the original code, the same ``pk`` is used for both the
    CustomerSignUp row and the User row.
    """
    get_customer(pk).delete()
    get_user(pk).delete()
