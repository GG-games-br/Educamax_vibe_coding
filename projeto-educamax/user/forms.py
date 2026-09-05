from django import forms
from django.contrib.auth.forms import AuthenticationForm

class EmailAuthenticationForm(AuthenticationForm):
    # Alteramos o label de "Usuário" para "E-mail"
    username = forms.EmailField(label="E-mail", widget=forms.EmailInput(attrs={'autofocus': True}))