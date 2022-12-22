from django.shortcuts import render
import subprocess
from .forms import MyForm
from . import callme

def myview(request):
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user_filter = form.cleaned_data['userFilter']
            start_date = form.cleaned_data['startDate']
            end_date = form.cleaned_data['endDate']


            # Now you can pass the form data to your Python script
            # by calling a function or using some other method
            subjectsAndDates, top10Words= callme.THE_function(email, password, user_filter, start_date, end_date)

            # render the output
            return render(request, 'output.html', {'subjectsAndDates': subjectsAndDates, 'top10Words': top10Words})
    else:
        form = MyForm()
    return render(request, 'form.html', {'form': form})
