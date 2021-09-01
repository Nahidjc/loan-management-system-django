from django.urls import path
from loanApp import views


app_name = 'loginApp'
urlpatterns = [
    path('loanpage/', views.LoanPage, name='loanpage'),

]
