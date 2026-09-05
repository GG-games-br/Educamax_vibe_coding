from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        ALUNO = 'ALUNO', 'Aluno'
        PROFESSOR = 'PROFESSOR', 'Professor'
        FUNCIONARIO = 'FUNCIONARIO', 'Funcionário'
        EMPRESA = 'EMPRESA', 'Empresa'


    email = models.EmailField(unique=True)

    cargo = models.CharField(
        max_length=20, 
        choices=Roles.choices, 
        default=Roles.ALUNO
    )


    # Define o e-mail como o campo de login principal
    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['username'] # O username ainda é exigido pelo Django, mas não para o login

    def __str__(self):
        return self.email

class PerfilAluno(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='perfil_aluno')
    matricula = models.CharField(max_length=20, blank=True, null=True)
    # Adicione outros campos do aluno aqui

class PerfilProfessor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='perfil_professor')
    especialidade = models.CharField(max_length=100, blank=True, null=True)

class PerfilFuncionario(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='perfil_funcionario')
    departamento = models.CharField(max_length=50, blank=True, null=True)

class PerfilEmpresa(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='perfil_empresa')
    cnpj = models.CharField(max_length=18, blank=True, null=True)
    nome_fantasia = models.CharField(max_length=100, blank=True, null=True)