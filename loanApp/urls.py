from django.urls import path
from loanApp import views


app_name = 'loanApp'
urlpatterns = [
    path('loan-request/', views.LoanRequest, name='loan_request'),

]
