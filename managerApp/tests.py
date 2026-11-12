"""
Baseline tests for managerApp views.

These tests describe the CURRENT behaviour of the original views.py. They are
written BEFORE the refactor, and every one of them must pass before and after
each refactoring step. Where today's behaviour is questionable (for example,
approving the same loan twice adds the amount twice), the test records what
the code does now, so any change in behaviour is a conscious decision.
"""
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from loanApp.models import CustomerLoan, loanCategory, loanRequest, loanTransaction
from loginApp.models import CustomerSignUp

LOGIN_URL = '/manager/admin-login'


def make_customer(username, is_staff=False, is_superuser=False):
    """Create a User plus the CustomerSignUp profile the views expect."""
    user = User.objects.create_user(
        username=username, password='pass12345',
        is_staff=is_staff, is_superuser=is_superuser)
    return CustomerSignUp.objects.create(
        user=user, first_name='F', last_name='L',
        email=f'{username}@example.com', designation='Engineer',
        profile_picture='profile_pic/x.jpg')


# The project uses WhiteNoise's manifest storage, which needs `collectstatic`
# before templates can render. Use plain static storage for the tests only.
@override_settings(
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class ManagerTestBase(TestCase):
    def setUp(self):
        self.admin = make_customer('admin', is_staff=True, is_superuser=True)
        self.client.force_login(self.admin.user)
        self.customer = make_customer('alice')
        self.category = loanCategory.objects.create(loan_name='Personal')

    def new_request(self, amount=1000, year=2, status='pending', customer=None):
        return loanRequest.objects.create(
            customer=customer or self.customer, category=self.category,
            reason='need money', amount=amount, year=year, status=status)


class SuperuserLoginTests(ManagerTestBase):
    def test_get_renders_login_for_anonymous(self):
        self.client.logout()
        response = self.client.get(reverse('managerApp:admin-login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/adminLogin.html')

    def test_authenticated_user_is_redirected_to_home(self):
        response = self.client.get(reverse('managerApp:admin-login'))
        self.assertRedirects(response, reverse('home'),
                             fetch_redirect_response=False)

    def test_superuser_login_redirects_to_dashboard(self):
        self.client.logout()
        response = self.client.post(reverse('managerApp:admin-login'), {
            'username': 'admin', 'password': 'pass12345'})
        self.assertRedirects(response, reverse('managerApp:dashboard'),
                             fetch_redirect_response=False)

    def test_non_superuser_gets_not_super_user_error(self):
        self.client.logout()
        make_customer('staffer', is_staff=True, is_superuser=False)
        response = self.client.post(reverse('managerApp:admin-login'), {
            'username': 'staffer', 'password': 'pass12345'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error'], 'You are not Super User')

    def test_wrong_password_gets_invalid_error(self):
        self.client.logout()
        response = self.client.post(reverse('managerApp:admin-login'), {
            'username': 'admin', 'password': 'wrong'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error'],
                         'Invalid Username or Password ')


class AccessControlTests(ManagerTestBase):
    """Every manager page must send anonymous users to the admin login."""
    names = ['managerApp:dashboard', 'managerApp:add_category',
             'managerApp:total_users', 'managerApp:loan_request',
             'managerApp:approved_loan', 'managerApp:rejected_loan',
             'managerApp:transaction_loan']

    def test_anonymous_users_are_redirected(self):
        self.client.logout()
        for name in self.names:
            with self.subTest(view=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response['Location'].startswith(LOGIN_URL))

    def test_anonymous_cannot_approve_or_reject(self):
        loan = self.new_request()
        self.client.logout()
        for name in ('managerApp:approved_request',
                     'managerApp:rejected_request'):
            with self.subTest(view=name):
                response = self.client.get(reverse(name, args=[loan.id]))
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response['Location'].startswith(LOGIN_URL))
        loan.refresh_from_db()
        self.assertEqual(loan.status, 'pending')


class DashboardTests(ManagerTestBase):
    def test_dashboard_counts_and_totals(self):
        self.new_request(status='pending')
        self.new_request(status='approved')
        self.new_request(status='rejected')
        CustomerLoan.objects.create(customer=self.customer,
                                    total_loan=1500, payable_loan=1800)
        loanTransaction.objects.create(customer=self.customer, payment=200)

        response = self.client.get(reverse('managerApp:dashboard'))
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertEqual(ctx['totalCustomer'], 2)  # admin + alice
        self.assertEqual(ctx['request'], 1)
        self.assertEqual(ctx['approved'], 1)
        self.assertEqual(ctx['rejected'], 1)
        self.assertEqual(ctx['totalLoan'], 1500)
        self.assertEqual(ctx['totalPayable'], 1800)
        self.assertEqual(ctx['totalPaid'], 200)

    def test_dashboard_totals_are_none_when_no_data(self):
        response = self.client.get(reverse('managerApp:dashboard'))
        self.assertIsNone(response.context['totalLoan'])
        self.assertIsNone(response.context['totalPayable'])
        self.assertIsNone(response.context['totalPaid'])
        self.assertEqual(response.context['approved'], 0)


class ApproveLoanTests(ManagerTestBase):
    def test_first_approval_creates_balance_with_12_percent_interest(self):
        loan = self.new_request(amount=1000, year=2)
        self.client.get(reverse('managerApp:approved_request', args=[loan.id]))

        balance = CustomerLoan.objects.get(customer=self.customer)
        self.assertEqual(balance.total_loan, 1000)
        # 1000 + 1000 * 0.12 * 2 = 1240
        self.assertEqual(balance.payable_loan, 1240)

        loan.refresh_from_db()
        self.assertEqual(loan.status, 'approved')
        self.assertEqual(loan.status_date, date.today().strftime("%B %d, %Y"))

    def test_second_approval_adds_to_existing_balance(self):
        first = self.new_request(amount=1000, year=2)
        second = self.new_request(amount=500, year=1)
        self.client.get(reverse('managerApp:approved_request', args=[first.id]))
        self.client.get(reverse('managerApp:approved_request', args=[second.id]))

        balance = CustomerLoan.objects.get(customer=self.customer)
        self.assertEqual(balance.total_loan, 1500)
        # first payable 1240, then + 500 + 500 * 0.12 * 1 = 560 -> 1800
        self.assertEqual(balance.payable_loan, 1800)

    def test_fractional_interest_is_truncated(self):
        """1001 * 0.12 * 1 = 120.12; the integer field keeps 1121."""
        loan = self.new_request(amount=1001, year=1)
        self.client.get(reverse('managerApp:approved_request', args=[loan.id]))
        balance = CustomerLoan.objects.get(customer=self.customer)
        self.assertEqual(balance.payable_loan, 1121)

    def test_approving_same_request_twice_changes_balance_twice(self):
        """Documents today's behaviour: nothing stops a double approval."""
        loan = self.new_request(amount=1000, year=2)
        url = reverse('managerApp:approved_request', args=[loan.id])
        self.client.get(url)
        self.client.get(url)

        balance = CustomerLoan.objects.get(customer=self.customer)
        self.assertEqual(balance.total_loan, 2000)

    def test_approval_renders_pending_list(self):
        loan = self.new_request()
        response = self.client.get(
            reverse('managerApp:approved_request', args=[loan.id]))
        self.assertTemplateUsed(response, 'admin/request_user.html')
        self.assertNotIn(loan, response.context['loanrequest'])


class RejectLoanTests(ManagerTestBase):
    def test_rejection_sets_status_and_creates_no_balance(self):
        loan = self.new_request(amount=1000, year=2)
        response = self.client.get(
            reverse('managerApp:rejected_request', args=[loan.id]))

        loan.refresh_from_db()
        self.assertEqual(loan.status, 'rejected')
        self.assertEqual(loan.status_date, date.today().strftime("%B %d, %Y"))
        self.assertFalse(CustomerLoan.objects.filter(
            customer=self.customer).exists())
        self.assertTemplateUsed(response, 'admin/request_user.html')


class LoanListTests(ManagerTestBase):
    def test_pending_list_contains_only_pending(self):
        pending = self.new_request(status='pending')
        self.new_request(status='approved')
        response = self.client.get(reverse('managerApp:loan_request'))
        self.assertEqual(list(response.context['loanrequest']), [pending])

    def test_approved_loan_page_lists_approved(self):
        approved = self.new_request(status='approved')
        self.new_request(status='pending')
        response = self.client.get(reverse('managerApp:approved_loan'))
        self.assertEqual(list(response.context['approvedLoan']), [approved])
        self.assertTemplateUsed(response, 'admin/approved_loan.html')

    def test_rejected_loan_page_lists_rejected(self):
        rejected = self.new_request(status='rejected')
        response = self.client.get(reverse('managerApp:rejected_loan'))
        self.assertEqual(list(response.context['rejectedLoan']), [rejected])
        self.assertTemplateUsed(response, 'admin/rejected_loan.html')

    def test_transaction_page_lists_transactions(self):
        tx = loanTransaction.objects.create(customer=self.customer, payment=50)
        response = self.client.get(reverse('managerApp:transaction_loan'))
        self.assertEqual(list(response.context['transactions']), [tx])
        self.assertTemplateUsed(response, 'admin/transaction.html')

    def test_users_page_lists_customers(self):
        response = self.client.get(reverse('managerApp:total_users'))
        self.assertIn(self.customer, response.context['users'])
        self.assertTemplateUsed(response, 'admin/customer.html')


class UserManagementTests(ManagerTestBase):
    def test_user_remove_deletes_customer_and_user(self):
        victim = make_customer('bob')
        pk = victim.user.id
        response = self.client.get(
            reverse('managerApp:user_remove', args=[pk]))

        self.assertRedirects(response, '/manager/users',
                             fetch_redirect_response=False)
        self.assertFalse(User.objects.filter(id=pk).exists())
        self.assertFalse(CustomerSignUp.objects.filter(id=pk).exists())


class AddCategoryTests(ManagerTestBase):
    def test_get_renders_form(self):
        response = self.client.get(reverse('managerApp:add_category'))
        self.assertTemplateUsed(response, 'admin/admin_add_category.html')

    def test_valid_post_creates_category_and_redirects(self):
        response = self.client.post(reverse('managerApp:add_category'),
                                    {'loan_name': 'Business'})
        self.assertRedirects(response, reverse('managerApp:dashboard'),
                             fetch_redirect_response=False)
        self.assertTrue(loanCategory.objects.filter(
            loan_name='Business').exists())

    def test_invalid_post_rerenders_form(self):
        response = self.client.post(reverse('managerApp:add_category'),
                                    {'loan_name': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
