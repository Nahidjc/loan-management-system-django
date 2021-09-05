from django.urls import path
from loanApp import views


app_name = 'loanApp'
urlpatterns = [
    path('loan-request/', views.LoanRequest, name='loan_request'),
    path('loan-payment/', views.LoanPayment, name='loan_payment'),
    path('user-transaction/', views.UserTransaction, name='user_transaction'),

]
