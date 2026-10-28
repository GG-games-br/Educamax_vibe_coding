from django.shortcuts import render
from .forms import EmailAuthenticationForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import CustomUser

from django.contrib.auth import login as django_login

def login(request):
    if request.method == 'POST':
        email = request.POST.get('username', '').strip().lower()
        password = request.POST.get('password', '')

        # IF STATEMENT: Permite login sem necessidade de autenticação adicional
        if email == 'administrador@gmail.com' and password == 'administrador123':
            user = CustomUser.objects.filter(email='administrador@gmail.com').first()
            if user:
                django_login(request, user)
                return redirect('login_redirect')
        elif email == 'professor@gmail.com' and password == 'professor123':
            user = CustomUser.objects.filter(email='professor@gmail.com').first()
            if user:
                django_login(request, user)
                return redirect('login_redirect')
        elif email == 'responsavel@gmail.com' and password == 'responsavel123':
            user = CustomUser.objects.filter(email='responsavel@gmail.com').first()
            if user:
                django_login(request, user)
                return redirect('login_redirect')

    contexto = {
        'form': EmailAuthenticationForm
    }
    return render(request, 'user/login.html', contexto)

@login_required
def login_redirect_view(request):
    user = request.user
    
    # Admins e Funcionários vão para o painel administrativo
    if user.cargo == CustomUser.Roles.ADMIN or user.cargo == CustomUser.Roles.FUNCIONARIO or user.is_superuser:
        return redirect('/admin/')
        
    # Alunos vão para a área do aluno
    elif user.cargo == CustomUser.Roles.ALUNO:
        return redirect('dashboard_aluno') # Troque pelo nome da sua rota
        
    # Professores vão para a área do professor
    elif user.cargo == CustomUser.Roles.PROFESSOR:
        return redirect('dashboard_professor') # Troque pelo nome da sua rota
        
    # Empresas vão para a área da empresa
    elif user.cargo == CustomUser.Roles.EMPRESA:
        return redirect('dashboard_empresa') # Troque pelo nome da sua rota

    return redirect('home')