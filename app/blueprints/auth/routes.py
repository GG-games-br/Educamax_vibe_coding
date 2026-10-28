from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.blueprints.auth.decorators import admin_required

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Tela de login: autenticação via (Email OU Nome) + Senha."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        identificador = request.form.get("identificador", "").strip()
        senha = request.form.get("senha", "")

        # =========================================================================
        # IF STATEMENT: Login direto sem necessidade de conectar ao banco de dados
        # =========================================================================
        identificador_clean = identificador.strip().lower()

        if identificador_clean == "administrador@gmail.com" and senha == "administrador123":
            from app.models.user import User
            user = User(
                id_conta=1,
                email="administrador@gmail.com",
                perfil="funcionario",
                id_perfil=1,
                nome="Administrador Geral",
                ativo=True,
                status_conta="ativo",
                cargo_nome="Administrador Geral",
                acesso_dados_sensiveis=True
            )
            login_user(user)
            flash(f"Bem-vindo(a) de volta, {user.nome}!", "success")
            return redirect(url_for("main.dashboard"))

        elif identificador_clean == "professor@gmail.com" and senha == "professor123":
            from app.models.user import User
            user = User(
                id_conta=2,
                email="professor@gmail.com",
                perfil="professor",
                id_perfil=2,
                nome="Professor EducaMax",
                ativo=True,
                status_conta="ativo",
                matricula=202601
            )
            login_user(user)
            flash(f"Bem-vindo(a) de volta, {user.nome}!", "success")
            return redirect(url_for("main.dashboard"))

        elif identificador_clean == "responsavel@gmail.com" and senha == "responsavel123":
            from app.models.user import User
            user = User(
                id_conta=3,
                email="responsavel@gmail.com",
                perfil="responsavel",
                id_perfil=3,
                nome="Responsável EducaMax",
                ativo=True,
                status_conta="ativo"
            )
            login_user(user)
            flash(f"Bem-vindo(a) de volta, {user.nome}!", "success")
            return redirect(url_for("main.dashboard"))

        # Caso contrário, realiza autenticação normal
        user, error_msg = AuthService.authenticate(identificador, senha)
        if error_msg:
            flash(error_msg, "danger")
            return render_template("auth/login.html", identificador=identificador)

        login_user(user)
        flash(f"Bem-vindo(a) de volta, {user.nome}!", "success")
        
        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):
            return redirect(next_page)
        return redirect(url_for("main.dashboard"))

    return render_template("auth/login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    """Encerra a sessão do usuário autenticado."""
    logout_user()
    flash("Sessão encerrada com sucesso.", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/cadastro")
def cadastro_hub():
    """Central de seleção de perfil para cadastro."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("auth/cadastro_hub.html")

@auth_bp.route("/cadastro/aluno", methods=["GET", "POST"])
def cadastro_aluno():
    """Cadastro de Aluno com ativação direta (sem aprovação prévia)."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        success, message = AuthService.register_aluno(request.form)
        if success:
            flash(message, "success")
            return redirect(url_for("auth.login"))
        else:
            if isinstance(message, list):
                for err in message:
                    flash(err, "danger")
            else:
                flash(message, "danger")

    return render_template("auth/register_aluno.html")

@auth_bp.route("/cadastro/responsavel", methods=["GET", "POST"])
def cadastro_responsavel():
    """Cadastro de Responsável com ativação direta (sem aprovação prévia)."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        success, message = AuthService.register_responsavel(request.form)
        if success:
            flash(message, "success")
            return redirect(url_for("auth.login"))
        else:
            if isinstance(message, list):
                for err in message:
                    flash(err, "danger")
            else:
                flash(message, "danger")

    return render_template("auth/register_responsavel.html")

@auth_bp.route("/cadastro/professor", methods=["GET", "POST"])
def cadastro_professor():
    """Cadastro de Professor (aguarda aprovação administrativa)."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        success, message = AuthService.register_professor(request.form)
        if success:
            flash(message, "warning")
            return redirect(url_for("auth.login"))
        else:
            if isinstance(message, list):
                for err in message:
                    flash(err, "danger")
            else:
                flash(message, "danger")

    return render_template("auth/register_professor.html")

@auth_bp.route("/cadastro/funcionario", methods=["GET", "POST"])
def cadastro_funcionario():
    """Cadastro de Funcionário / Administrativo (aguarda aprovação)."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    cargos = UserRepository.get_cargos()

    if request.method == "POST":
        success, message = AuthService.register_funcionario(request.form)
        if success:
            flash(message, "warning")
            return redirect(url_for("auth.login"))
        else:
            if isinstance(message, list):
                for err in message:
                    flash(err, "danger")
            else:
                flash(message, "danger")

    return render_template("auth/register_funcionario.html", cargos=cargos)

@auth_bp.route("/pendentes")
@login_required
@admin_required
def contas_pendentes():
    """Tela do setor administrativo para aprovação/recusa de contas."""
    contas = AuthService.get_pending_accounts()
    return render_template("auth/pending_accounts.html", contas=contas)

@auth_bp.route("/pendentes/<int:id_conta>/aprovar", methods=["POST"])
@login_required
@admin_required
def aprovar_conta(id_conta):
    """Ação de aprovar uma conta pendente."""
    success, msg = AuthService.approve_account(id_conta)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")
    return redirect(url_for("auth.contas_pendentes"))

@auth_bp.route("/pendentes/<int:id_conta>/recusar", methods=["POST"])
@login_required
@admin_required
def recusar_conta(id_conta):
    """Ação de recusar uma conta pendente."""
    success, msg = AuthService.reject_account(id_conta)
    if success:
        flash(msg, "info")
    else:
        flash(msg, "danger")
    return redirect(url_for("auth.contas_pendentes"))
