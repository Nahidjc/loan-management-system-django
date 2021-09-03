from django.urls import path
from loginApp import views


app_name = 'login_App'
urlpatterns = [
    path('login-customer/', views.login_view, name='login_customer'),
    path('signup-customer/', views.sign_up_view, name='signup_customer'),
    path('logout-customer/', views.logout_view, name='logout'),
    path('edit-customer/', views.edit_customer, name='edit-customer'),

]
