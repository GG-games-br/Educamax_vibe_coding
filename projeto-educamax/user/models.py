from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    # Define o e-mail como o campo de login principal
    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['username'] # O username ainda é exigido pelo Django, mas não para o login

    def __str__(self):
        return self.email