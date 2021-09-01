from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class CustomerSignUp(models.Model):
    user = models.OneToOneField(
        User, unique=True, on_delete=models.CASCADE, related_name='customer')
    first_name = models.CharField(max_length=250, blank=False)
    last_name = models.CharField(max_length=250, blank=False)
    email = models.EmailField(max_length=100, blank=False)
    profile_picture = models.ImageField(
        upload_to='profile_pic', blank=False)
    designation = models.CharField(max_length=100, blank=False)
    # password1 = models.PasswordField(max_length=100)
    # password2 = models.PasswordField(max_length=100)

    def __str__(self):
        return self.user.username


# class CustomerLogin(models.Model):
#     username = models.CharField(max_length=250, blank=False, null=False)
#     password = models.PasswordField(max_length=100, blank=False)
