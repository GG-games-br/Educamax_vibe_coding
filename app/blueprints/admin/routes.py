from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.blueprints.auth.decorators import admin_required
from app.services.academic_service import AcademicService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/academico")
@login_required
@admin_required
def academico_hub():
    """Painel de Gestão Acadêmica Geral."""
    turmas = AcademicService.list_turmas()
    materias = AcademicService.list_materias()
    prestadores = AcademicService.list_prestadores()
    alunos = AcademicService.list_alunos()
    professores = AcademicService.list_professores()
    responsaveis = AcademicService.list_responsaveis()

    return render_template(
        "admin/academico_hub.html",
        total_turmas=len(turmas),
        total_materias=len(materias),
        total_prestadores=len(prestadores),
        total_alunos=len(alunos),
        total_professores=len(professores),
        total_responsaveis=len(responsaveis)
    )

# --- TURMAS ---
@admin_bp.route("/turmas", methods=["GET", "POST"])
@login_required
@admin_required
def turmas():
    """Listagem e cadastro de turmas."""
    if request.method == "POST":
        id_turma = request.form.get("id_turma", "").strip().lower()
        success, msg = AcademicService.add_turma(id_turma)
        if success:
            flash(msg, "success")
        else:
            flash(msg, "danger")
        return redirect(url_for("admin.turmas"))

    turmas_list = AcademicService.list_turmas()
    turmas_disponiveis = AcademicService.get_turmas_disponiveis()
    return render_template("admin/turmas.html", turmas=turmas_list, disponiveis=turmas_disponiveis)

@admin_bp.route("/turmas/<id_turma>/remover", methods=["POST"])
@login_required
@admin_required
def remover_turma(id_turma):
    """Exclui uma turma do sistema."""
    success, msg = AcademicService.remove_turma(id_turma)
    if success:
        flash(msg, "info")
    else:
        flash(msg, "danger")
    return redirect(url_for("admin.turmas"))

# --- MATÉRIAS ---
@admin_bp.route("/materias", methods=["GET", "POST"])
@login_required
@admin_required
def materias():
    """Listagem e cadastro de matérias/disciplinas."""
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        success, msg = AcademicService.add_materia(nome)
        if success:
            flash(msg, "success")
        else:
            flash(msg, "danger")
        return redirect(url_for("admin.materias"))

    materias_list = AcademicService.list_materias()
    return render_template("admin/materias.html", materias=materias_list)

@admin_bp.route("/materias/<int:id_materia>/remover", methods=["POST"])
@login_required
@admin_required
def remover_materia(id_materia):
    """Exclui uma matéria do sistema."""
    success, msg = AcademicService.remove_materia(id_materia)
    if success:
        flash(msg, "info")
    else:
        flash(msg, "danger")
    return redirect(url_for("admin.materias"))

# --- PRESTADORES DE SERVIÇO ---
@admin_bp.route("/prestadores", methods=["GET", "POST"])
@login_required
@admin_required
def prestadores():
    """Listagem e cadastro de prestadores terceirizados."""
    if request.method == "POST":
        cnpj = request.form.get("cnpj", "")
        servico = request.form.get("servico", "")
        numero = request.form.get("numero", "")
        email = request.form.get("email", "")

        success, msg = AcademicService.add_prestador(cnpj, servico, numero, email)
        if success:
            flash(msg, "success")
        else:
            flash(msg, "danger")
        return redirect(url_for("admin.prestadores"))

    prestadores_list = AcademicService.list_prestadores()
    return render_template("admin/prestadores.html", prestadores=prestadores_list)

@admin_bp.route("/prestadores/<int:id_servico>/remover", methods=["POST"])
@login_required
@admin_required
def remover_prestador(id_servico):
    """Exclui um prestador de serviço."""
    success, msg = AcademicService.remove_prestador(id_servico)
    if success:
        flash(msg, "info")
    else:
        flash(msg, "danger")
    return redirect(url_for("admin.prestadores"))

# --- ALUNOS E VÍNCULOS ---
@admin_bp.route("/alunos")
@login_required
@admin_required
def alunos():
    """Listagem de alunos cadastrados e suas turmas atuais."""
    alunos_list = AcademicService.list_alunos()
    turmas_list = AcademicService.list_turmas()
    responsaveis_list = AcademicService.list_responsaveis()
    return render_template(
        "admin/alunos.html",
        alunos=alunos_list,
        turmas=turmas_list,
        responsaveis=responsaveis_list
    )

@admin_bp.route("/vinculos/aluno-turma", methods=["POST"])
@login_required
@admin_required
def vincular_aluno_turma():
    """Associa um aluno a uma turma."""
    matricula = int(request.form.get("matricula"))
    id_turma = request.form.get("id_turma")
    success, msg = AcademicService.vincular_aluno_turma(matricula, id_turma)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")
    return redirect(url_for("admin.alunos"))

@admin_bp.route("/vinculos/responsavel-aluno", methods=["POST"])
@login_required
@admin_required
def vincular_responsavel_aluno():
    """Associa um aluno ao seu responsável legal."""
    id_responsavel = int(request.form.get("id_responsavel"))
    matricula = int(request.form.get("matricula"))
    parentesco = request.form.get("parentesco", "Pai/Mãe")

    success, msg = AcademicService.vincular_responsavel_aluno(id_responsavel, matricula, parentesco)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")
    return redirect(url_for("admin.alunos"))

# --- PROFESSORES E VÍNCULOS COM TURMAS ---
@admin_bp.route("/professores")
@login_required
@admin_required
def professores():
    """Listagem de professores e suas turmas alocadas."""
    professores_list = AcademicService.list_professores()
    turmas_list = AcademicService.list_turmas()
    return render_template(
        "admin/professores.html",
        professores=professores_list,
        turmas=turmas_list
    )

@admin_bp.route("/vinculos/professor-turma", methods=["POST"])
@login_required
@admin_required
def vincular_professor_turma():
    """Aloca um professor para lecionar em uma turma."""
    id_professor = int(request.form.get("id_professor"))
    id_turma = request.form.get("id_turma")

    success, msg = AcademicService.vincular_professor_turma(id_professor, id_turma)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")
    return redirect(url_for("admin.professores"))
