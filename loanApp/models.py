from django.db import models
from django.contrib.auth.models import User
from loginApp.models import CustomerSignUp
# Create your models here.


class loanCategory(models.Model):
    loan_name = models.CharField(max_length=250)
    creation_date = models.DateField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.loan_name


class loanRequest(models.Model):
    customer = models.ForeignKey(CustomerSignUp, on_delete=models.CASCADE)
    # category = models.ForeignKey(loanCategory, on_delete=models.CASCADE)
    request_date = models.DateField(auto_now_add=True)
    reason = models.CharField(max_length=250)
    status = models.CharField(max_length=100, default='Pending')
    amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.customer.user
