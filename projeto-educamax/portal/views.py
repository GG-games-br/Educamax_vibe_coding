from django.shortcuts import render
from user.decorators import role_required

# Create your views here.

@role_required('ALUNO')
def dashboard_aluno(request):
    aluno = request.user.perfil_aluno
    # later: grades, assignments filtered by this student
    context = {'aluno': aluno}
    return render(request, 'portal/dashboard_aluno.html', context)

@role_required('ALUNO')
def dashboard_aluno(request):
    return render(request, 'portal/dashboard_aluno.html')

@role_required('PROFESSOR')
def dashboard_professor(request):
    return render(request, 'portal/dashboard_professor.html')

@role_required('EMPRESA')
def dashboard_empresa(request):
    return render(request, 'portal/dashboard_empresa.html')