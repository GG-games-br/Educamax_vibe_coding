from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.blueprints.auth.decorators import perfil_required
from app.repositories.academic_repository import AcademicRepository
from app.repositories.notas_repository import NotasRepository
from app.services.notas_service import NotasService

notas_bp = Blueprint("notas", __name__, url_prefix="/notas")

@notas_bp.route("/boletim/<int:matricula>")
@login_required
def ver_boletim(matricula):
    """Visualização do boletim e histórico escolar do aluno."""
    dados_boletim, erro = NotasService.get_boletim_completo(current_user, matricula)
    if erro:
        flash(erro, "danger")
        abort(403)
    return render_template("notas/boletim.html", dados=dados_boletim)

@notas_bp.route("/lancar")
@login_required
@perfil_required("professor", "admin")
def painel_lancamento():
    """Painel do professor e administrativo para gerenciar avaliações e notas."""
    materias = AcademicService.list_materias() if current_user.is_admin else AcademicRepository.list_materias()
    alunos = AcademicRepository.list_alunos()
    
    if current_user.perfil == "professor":
        provas = NotasRepository.list_provas_by_professor(current_user.id_perfil)
        tarefas = NotasRepository.list_tarefas_by_professor(current_user.id_perfil)
    else:
        provas = []
        tarefas = []

    return render_template(
        "notas/painel_lancamento.html",
        materias=materias,
        alunos=alunos,
        provas=provas,
        tarefas=tarefas
    )

@notas_bp.route("/prova/nova", methods=["POST"])
@login_required
@perfil_required("professor", "admin")
def nova_prova():
    id_materia = int(request.form.get("id_materia"))
    descricao = request.form.get("descricao")
    data_prova = request.form.get("data_prova")

    success, msg = NotasService.criar_prova(current_user, id_materia, descricao, data_prova)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")
    return redirect(url_for("notas.painel_lancamento"))

@notas_bp.route("/prova/atribuir", methods=["POST"])
@login_required
@perfil_required("professor", "admin")
def atribuir_nota_prova():
    id_prova = int(request.form.get("id_prova"))
    matricula = int(request.form.get("matricula"))
    nota = request.form.get("nota")

    success, msg = NotasService.lancar_nota_prova(id_prova, matricula, nota)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")
    return redirect(url_for("notas.painel_lancamento"))

@notas_bp.route("/tarefa/nova", methods=["POST"])
@login_required
@perfil_required("professor", "admin")
def nova_tarefa():
    id_materia = int(request.form.get("id_materia"))
    descricao = request.form.get("descricao")

    success, msg = NotasService.criar_tarefa(current_user, id_materia, descricao)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")
    return redirect(url_for("notas.painel_lancamento"))

@notas_bp.route("/tarefa/atribuir", methods=["POST"])
@login_required
@perfil_required("professor", "admin")
def atribuir_nota_tarefa():
    id_tarefa = int(request.form.get("id_tarefa"))
    matricula = int(request.form.get("matricula"))
    nota = request.form.get("nota")

    success, msg = NotasService.lancar_nota_tarefa(id_tarefa, matricula, nota)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")
    return redirect(url_for("notas.painel_lancamento"))

@notas_bp.route("/historico/lancar", methods=["POST"])
@login_required
@perfil_required("professor", "admin")
def lancar_historico():
    matricula = int(request.form.get("matricula"))
    id_materia = int(request.form.get("id_materia"))
    ano = int(request.form.get("ano", 2026))
    nota = request.form.get("nota")

    success, msg = NotasService.lancar_historico_disciplina(matricula, id_materia, ano, nota)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")
    return redirect(url_for("notas.painel_lancamento"))
