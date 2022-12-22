from django import forms
from django.forms.widgets import DateInput

class MyForm(forms.Form):
    email = forms.EmailField(label='Enter email to fetch emails from*')
    password = forms.CharField(label='Enter app password for said email*')
    userFilter = forms.CharField(required=False, label='Enter email address to look for emails sent to')
    startDate = forms.DateField(label='Earliest date to look for emails sent on', widget=DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False)
    endDate = forms.DateField(label='Latest date to look for emails sent on',  widget=DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False)
