from django.db import models
from django.contrib.auth.models import User
from loginApp.models import CustomerSignUp
# Create your models here.


class loanCategory(models.Model):
    loan_name = models.CharField(max_length=250)
    creation_date = models.DateField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category_name


class loanRequest(models.Model):
    customer = models.ForeignKey(CustomerSignUp, on_delete=models.CASCADE)
    category = models.ForeignKey(loanCategory, on_delete=models.CASCADE)
