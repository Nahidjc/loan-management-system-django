from django.urls import path
from managerApp import views


app_name = 'managerApp'

urlpatterns = [
    path('admin-login/', views.superuser_login_view, name='admin-login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-category/', views.add_category, name='add_category'),
    path('users/', views.total_users, name='total_users'),
    path('user-remove/<int:pk>/', views.user_remove, name='user_remove'),
    path('loan-request-user/', views.loan_request, name='loan_request'),
    path('approved-request/<int:id>/',
         views.approved_request, name='approved_request'),
    path('rejected-request/<int:id>/',
         views.rejected_request, name='rejected_request'),
    path('approved-loan',  views.approved_loan, name='approved_loan'),
    path('rejected-loan', views.rejected_loan, name='rejected_loan'),
    path('transaction-loan', views.transaction_loan, name='transaction_loan'),


]
