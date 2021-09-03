from django import forms
from .models import loanRequest


class LoanRequestForm(forms.ModelForm):
    class Meta:
        model = loanRequest
        fields = ('category', 'reason', 'amount', 'year')
