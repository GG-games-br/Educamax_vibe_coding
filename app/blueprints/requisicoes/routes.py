from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.blueprints.auth.decorators import admin_required, perfil_required
from app.repositories.requisicao_repository import RequisicaoRepository
from app.repositories.academic_repository import AcademicRepository
from app.services.requisicao_service import RequisicaoService

requisicoes_bp = Blueprint("requisicoes", __name__, url_prefix="/requisicoes")

@requisicoes_bp.route("/")
@login_required
def index():
    """Redireciona para a tela apropriada conforme o perfil."""
    if current_user.is_admin:
        return redirect(url_for("requisicoes.gerenciar"))
    elif current_user.perfil == "responsavel":
        return redirect(url_for("requisicoes.minhas_requisicoes"))
    flash("Seu perfil não possui acesso ao módulo de requisições.", "warning")
    return redirect(url_for("main.dashboard"))

@requisicoes_bp.route("/minhas")
@login_required
@perfil_required("responsavel", "admin")
def minhas_requisicoes():
    """Histórico de solicitações feitas pelo responsável logado."""
    reqs = RequisicaoRepository.list_requisicoes_by_responsavel(current_user.id_perfil)
    alunos = AcademicRepository.get_alunos_do_responsavel(current_user.id_perfil)
    return render_template("requisicoes/minhas_requisicoes.html", requisicoes=reqs, alunos=alunos)

@requisicoes_bp.route("/nova", methods=["POST"])
@login_required
@perfil_required("responsavel", "admin")
def nova_requisicao():
    """Cria uma nova requisição para um dependente."""
    matricula = int(request.form.get("matricula"))
    tipo = request.form.get("tipo")
    descricao = request.form.get("descricao")

    success, msg = RequisicaoService.criar_requisicao(current_user, matricula, tipo, descricao)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")

    return redirect(url_for("requisicoes.minhas_requisicoes"))

@requisicoes_bp.route("/gerenciar")
@login_required
@admin_required
def gerenciar():
    """Painel administrativo de atendimento a requisições escolares."""
    status_filtro = request.args.get("status")
    reqs = RequisicaoRepository.list_all_requisicoes(status=status_filtro)
    return render_template("requisicoes/gerenciar_admin.html", requisicoes=reqs, status_filtro=status_filtro)

@requisicoes_bp.route("/<int:id_requisicao>/responder", methods=["POST"])
@login_required
@admin_required
def responder(id_requisicao):
    """Aprovação ou recusa administrativa com parecer e boleto fictício opcional."""
    status = request.form.get("status")
    resposta = request.form.get("resposta_administrativo")
    valor_boleto = request.form.get("valor_boleto")
    vencimento_boleto = request.form.get("vencimento_boleto")

    success, msg = RequisicaoService.responder_requisicao(
        id_requisicao=id_requisicao,
        status=status,
        resposta=resposta,
        user=current_user,
        valor_boleto=valor_boleto,
        vencimento_boleto=vencimento_boleto
    )

    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")

    return redirect(url_for("requisicoes.gerenciar"))
