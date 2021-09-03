from django.contrib import admin
from .models import loanRequest, loanCategory
# Register your models here.loanCategory,
admin.site.register(loanRequest)
admin.site.register(loanCategory)
