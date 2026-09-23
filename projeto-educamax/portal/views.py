from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from tarefas.models import Tarefa
from user.decorators import role_required


@role_required('ALUNO')
def dashboard_aluno(request):
    hoje = timezone.localdate()

    # Next 5 tasks: due today or later, plus tasks without a due date
    tarefas_proximas = (
        Tarefa.objects
        .filter(Q(data_entrega__gte=hoje) | Q(data_entrega__isnull=True))
        .select_related('criado_por')
        .order_by('data_entrega')[:5]
    )

    context = {
        # None if the student has no PerfilAluno yet (avoids a crash)
        'aluno': getattr(request.user, 'perfil_aluno', None),
        'tarefas_proximas': tarefas_proximas,
    }
    return render(request, 'portal/dashboard_aluno.html', context)


@role_required('PROFESSOR')
def dashboard_professor(request):
    return render(request, 'portal/dashboard_professor.html')


@role_required('EMPRESA')
def dashboard_empresa(request):
    return render(request, 'portal/dashboard_empresa.html')
