"""
Named constants for managerApp.

Before this module existed, the same string literals (statuses, URLs, template
names) and the 12% interest rate were typed directly into many views. Keeping
them here means a change is made in ONE place (Open/Closed Principle) and a
typo becomes an AttributeError instead of a silent wrong value.
"""


class Status:
    """Allowed values of loanRequest.status."""
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'


class Endpoints:
    """URL names and paths used for redirects and login protection."""
    HOME = 'home'
    DASHBOARD = 'managerApp:dashboard'
    LOGIN_URL = '/manager/admin-login'
    USERS_REDIRECT = '/manager/users'


class Templates:
    """Template paths rendered by the manager views."""
    ADMIN_LOGIN = 'admin/adminLogin.html'
    DASHBOARD = 'admin/dashboard.html'
    ADD_CATEGORY = 'admin/admin_add_category.html'
    CUSTOMERS = 'admin/customer.html'
    REQUEST_USER = 'admin/request_user.html'
    APPROVED_LOAN = 'admin/approved_loan.html'
    REJECTED_LOAN = 'admin/rejected_loan.html'
    TRANSACTION = 'admin/transaction.html'


class Loan:
    """Business rules for loans."""
    # Simple annual interest: payable = amount + amount * rate * years
    ANNUAL_INTEREST_RATE = 0.12


class Messages:
    """User-facing error messages (text kept exactly as in the original)."""
    NOT_SUPERUSER = "You are not Super User"
    INVALID_LOGIN = "Invalid Username or Password "  # trailing space is original


STATUS_DATE_FORMAT = "%B %d, %Y"
