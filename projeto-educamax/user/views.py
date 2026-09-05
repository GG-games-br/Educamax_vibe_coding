from django.shortcuts import render
from .forms import EmailAuthenticationForm

def login(request):
    contexto ={
        'form' : EmailAuthenticationForm
    }
    return render(request, 'user/login.html', contexto)
