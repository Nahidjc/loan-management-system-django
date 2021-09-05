from django import forms
from .models import loanRequest, loanTransaction


class LoanRequestForm(forms.ModelForm):
    class Meta:
        model = loanRequest
        fields = ('category', 'reason', 'amount', 'year')


class LoanTransactionForm(forms.ModelForm):
    class Meta:
        model = loanTransaction
        fields = ('payment',)
