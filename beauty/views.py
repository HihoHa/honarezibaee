from django import forms
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse

def logout_view(request):#logout the current user and redirect to previous location
    logout(request)
    return redirect('%s' % request.GET['next'])

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            #getting the next page
            next = form.cleaned_data['next']
            if next is None:
                next = '/'
            user_name = form.cleaned_data['user_name']
            password = form.cleaned_data['password']
            #user will be None if the provided attributes dont match
            user = authenticate(username=user_name, password=password)
            if user is not None and user.is_active:
                login(request, user)
                return redirect(next)
            else:
                return render(request, 'login.html', {'form':form,
                 'error_message':'your user name and password dont match'})
        else:
            return render(request, 'login.html', {'form':form})
    else:
        form = LoginForm()
        #This is actually a part of logic, so it is OK to be here.
        #Posting the 'next' attribute to view for future redirect
        try:
            form.initial['next'] = request.GET['next']
        except:
            form.initial['next'] = '/'
        return render(request, 'login.html', {'form':form})

class LoginForm(forms.Form):
    user_name = forms.CharField(label="User Name", max_length=30)
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class':'form-control'}))
    next = forms.CharField(widget = forms.HiddenInput())