from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.blueprints.auth.decorators import perfil_required, responsavel_aluno_required
from app.services.academic_service import AcademicService

responsavel_bp = Blueprint("responsavel", __name__, url_prefix="/responsavel")

@responsavel_bp.route("/dependentes")
@login_required
@perfil_required("responsavel", "admin")
def meus_dependentes():
    """Lista exclusivamente os alunos vinculados ao responsável logado."""
    alunos = AcademicService.get_alunos_responsavel(current_user.id_perfil)
    return render_template("responsavel/meus_dependentes.html", alunos=alunos)

@responsavel_bp.route("/aluno/<int:matricula>")
@login_required
@responsavel_aluno_required
def ver_dependente(matricula):
    """
    Exibe os detalhes acadêmicos de um aluno vinculado.
    Protegido no backend: apenas o responsável pelo aluno ou administrativo pode acessar.
    """
    aluno = AcademicService.get_aluno_info(matricula)
    return render_template("responsavel/detalhes_dependente.html", aluno=aluno)
