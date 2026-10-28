from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.blueprints.auth.decorators import admin_required, perfil_required
from app.repositories.financeiro_repository import FinanceiroRepository
from app.repositories.academic_repository import AcademicRepository
from app.services.financeiro_service import FinanceiroService

financeiro_bp = Blueprint("financeiro", __name__, url_prefix="/financeiro")

# --- PAINEL GERAL (ADMINISTRATIVO) ---
@financeiro_bp.route("/painel")
@login_required
@admin_required
def painel():
    """Painel financeiro administrativo com métricas e resumos simulados."""
    metricas = FinanceiroRepository.get_dashboard_financeiro_metricas()
    ultimos_boletos = FinanceiroRepository.list_all_boletos()[:5]
    ultimos_salarios = FinanceiroRepository.list_all_folha_pagamento()[:5]
    return render_template(
        "financeiro/painel_admin.html",
        metricas=metricas,
        boletos=ultimos_boletos,
        salarios=ultimos_salarios
    )

# --- BOLETOS (ADMINISTRATIVO) ---
@financeiro_bp.route("/boletos", methods=["GET", "POST"])
@login_required
@admin_required
def boletos_admin():
    """Gerenciamento e emissão de boletos simulados pela administração."""
    if request.method == "POST":
        acao = request.form.get("acao")
        if acao == "individual":
            matricula = int(request.form.get("matricula"))
            tipo = request.form.get("tipo", "mensalidade")
            valor = request.form.get("valor")
            data_vencimento = request.form.get("data_vencimento")
            success, msg = FinanceiroService.emitir_boleto_individual(matricula, tipo, valor, data_vencimento)
            if success:
                flash(msg, "success")
            else:
                flash(msg, "danger")

        elif acao == "lote":
            id_turma = request.form.get("id_turma")
            valor = request.form.get("valor")
            data_vencimento = request.form.get("data_vencimento")
            success, msg = FinanceiroService.emitir_mensalidades_em_lote(id_turma, valor, data_vencimento)
            if success:
                flash(msg, "success")
            else:
                flash(msg, "danger")

        return redirect(url_for("financeiro.boletos_admin"))

    boletos = FinanceiroRepository.list_all_boletos()
    alunos = AcademicRepository.list_alunos()
    turmas = AcademicRepository.list_turmas()
    return render_template("financeiro/boletos_admin.html", boletos=boletos, alunos=alunos, turmas=turmas)

# --- FOLHA DE PAGAMENTO (ADMINISTRATIVO) ---
@financeiro_bp.route("/folha", methods=["GET", "POST"])
@login_required
@admin_required
def folha_admin():
    """Gestão da folha salarial de professores e colaboradores."""
    if request.method == "POST":
        tipo = request.form.get("tipo_beneficiario")  # 'professor' ou 'funcionario'
        id_beneficiario = int(request.form.get("id_beneficiario"))
        mes = request.form.get("mes")
        ano = request.form.get("ano")
        valor = request.form.get("valor")

        success, msg = FinanceiroService.lancar_salario(tipo, id_beneficiario, mes, ano, valor)
        if success:
            flash(msg, "success")
        else:
            flash(msg, "danger")
        return redirect(url_for("financeiro.folha_admin"))

    folhas = FinanceiroRepository.list_all_folha_pagamento()
    professores = AcademicRepository.list_professores()
    funcionarios = AcademicRepository.list_professores()  # ou get list of employees
    return render_template("financeiro/folha_admin.html", folhas=folhas, professores=professores)

@financeiro_bp.route("/folha/<int:id_pagamento>/quitar", methods=["POST"])
@login_required
@admin_required
def quitar_salario(id_pagamento):
    """Marca o pagamento do salário como concluído (simulação)."""
    success, msg = FinanceiroService.quitar_salario_simulado(id_pagamento)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")
    return redirect(url_for("financeiro.folha_admin"))

# --- CONTRATOS PRESTADORES (ADMINISTRATIVO) ---
@financeiro_bp.route("/contratos", methods=["GET", "POST"])
@login_required
@admin_required
def contratos_admin():
    """Contratos com empresas terceirizadas prestadoras de serviço."""
    if request.method == "POST":
        id_servico = int(request.form.get("id_servico"))
        descricao = request.form.get("descricao")
        valor = request.form.get("valor")
        data_inicio = request.form.get("data_inicio")
        data_fim = request.form.get("data_fim")

        success, msg = FinanceiroService.criar_contrato_prestador(id_servico, descricao, valor, data_inicio, data_fim)
        if success:
            flash(msg, "success")
        else:
            flash(msg, "danger")
        return redirect(url_for("financeiro.contratos_admin"))

    contratos = FinanceiroRepository.list_all_contratos()
    prestadores = AcademicRepository.list_prestadores()
    return render_template("financeiro/contratos_admin.html", contratos=contratos, prestadores=prestadores)

@financeiro_bp.route("/contratos/<int:id_contrato>/encerrar", methods=["POST"])
@login_required
@admin_required
def encerrar_contrato(id_contrato):
    success, msg = FinanceiroService.encerrar_contrato(id_contrato)
    if success:
        flash(msg, "info")
    else:
        flash(msg, "danger")
    return redirect(url_for("financeiro.contratos_admin"))

# --- VISÃO DO RESPONSÁVEL: BOLETOS DOS DEPENDENTES ---
@financeiro_bp.route("/meus-boletos")
@login_required
@perfil_required("responsavel", "admin")
def meus_boletos():
    """Lista todos os boletos fictícios vinculados aos alunos deste responsável."""
    boletos = FinanceiroRepository.list_boletos_by_responsavel(current_user.id_perfil)
    return render_template("financeiro/meus_boletos.html", boletos=boletos)

@financeiro_bp.route("/boleto/<int:id_boleto>")
@login_required
def visualizar_boleto(id_boleto):
    """Exibição visual estética do boleto simulado."""
    boleto = FinanceiroService.get_boleto_detalhes(id_boleto)
    if not boleto:
        abort(404)

    # Checagem de permissão: apenas o responsável pelo aluno ou administrativo pode ver
    if not current_user.is_admin:
        if current_user.perfil != "responsavel":
            abort(403)
        if not AcademicRepository.is_responsavel_of_aluno(current_user.id_perfil, boleto["matricula"]):
            abort(403)

    return render_template("financeiro/visualizar_boleto.html", boleto=boleto)

@financeiro_bp.route("/boleto/<int:id_boleto>/pagar", methods=["POST"])
@login_required
def pagar_boleto(id_boleto):
    """Ação fictícia de pagamento de boleto."""
    success, msg = FinanceiroService.pagar_boleto_simulado(id_boleto, current_user)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")

    if current_user.perfil == "responsavel":
        return redirect(url_for("financeiro.meus_boletos"))
    return redirect(url_for("financeiro.boletos_admin"))

# --- VISÃO DO PROFESSOR OU FUNCIONÁRIO: MEU SALÁRIO SIMULADO ---
@financeiro_bp.route("/meu-salario")
@login_required
@perfil_required("professor", "funcionario", "admin")
def meu_salario():
    """Consulta de lançamentos de salário exclusivos do colaborador logado."""
    salarios = FinanceiroService.get_salarios_usuario(current_user)
    return render_template("financeiro/meu_salario.html", salarios=salarios)
