from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.blueprints.auth.decorators import perfil_required
from app.services.academic_service import AcademicService

aluno_bp = Blueprint("aluno", __name__, url_prefix="/aluno")

@aluno_bp.route("/perfil")
@login_required
@perfil_required("aluno", "admin")
def meu_perfil():
    """Exibe os dados de matrícula e turma do aluno logado."""
    matricula = current_user.matricula
    aluno = AcademicService.get_aluno_info(matricula) if matricula else None
    return render_template("aluno/meu_perfil.html", aluno=aluno)
