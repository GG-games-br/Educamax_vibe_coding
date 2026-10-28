from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.blueprints.auth.decorators import perfil_required, professor_turma_required
from app.services.academic_service import AcademicService

professor_bp = Blueprint("professor", __name__, url_prefix="/professor")

@professor_bp.route("/turmas")
@login_required
@perfil_required("professor", "admin")
def minhas_turmas():
    """Lista exclusivamente as turmas alocadas ao professor logado."""
    turmas = AcademicService.get_turmas_professor(current_user.id_perfil)
    return render_template("professor/minhas_turmas.html", turmas=turmas)

@professor_bp.route("/turma/<id_turma>")
@login_required
@professor_turma_required
def ver_turma(id_turma):
    """
    Exibe os detalhes e alunos de uma turma específica.
    Protegido no backend: o professor só acessa se estiver alocado nesta turma.
    """
    alunos = AcademicService.get_alunos_turma(id_turma)
    return render_template("professor/detalhes_turma.html", id_turma=id_turma, alunos=alunos)
