from datetime import datetime, date
from decimal import Decimal
from app.repositories.financeiro_repository import FinanceiroRepository
from app.repositories.academic_repository import AcademicRepository

class FinanceiroService:
    """
    Camada de serviço para o módulo financeiro 100% simulado.
    Implementa as regras de negócio de 04-financeiro-simulado.md.
    """

    @staticmethod
    def gerar_linha_digitavel_ficticia(id_boleto, valor):
        """Gera uma representação estética de linha digitável de mentirinha."""
        val_str = f"{int(float(valor) * 100):010d}"
        bloco1 = f"00190.{id_boleto:04d}1"
        bloco2 = f"99887.{id_boleto * 3:05d}2"
        bloco3 = f"55443.{id_boleto * 7:05d}3"
        bloco4 = "1"
        bloco5 = val_str
        return f"{bloco1} {bloco2} {bloco3} {bloco4} {bloco5}"

    # --- BOLETOS ---
    @classmethod
    def emitir_boleto_individual(cls, matricula, tipo, valor, data_vencimento, id_requisicao=None):
        try:
            val = Decimal(str(valor))
            if val <= 0:
                return False, "O valor do boleto deve ser maior que zero."
        except Exception:
            return False, "Valor numérico inválido."

        if not data_vencimento:
            return False, "Informe uma data de vencimento válida."

        try:
            id_b = FinanceiroRepository.create_boleto(
                matricula=matricula,
                tipo=tipo,
                valor=val,
                data_vencimento=data_vencimento,
                id_requisicao=id_requisicao
            )
            return True, f"Boleto fictício #{id_b} gerado com sucesso!"
        except Exception as e:
            return False, f"Erro ao gerar boleto: {str(e)}"

    @classmethod
    def emitir_mensalidades_em_lote(cls, id_turma, valor, data_vencimento):
        """Gera um boleto de mensalidade simulada para cada aluno da turma informada."""
        alunos = AcademicRepository.get_alunos_da_turma(id_turma)
        if not alunos:
            return False, f"Nenhum aluno matriculado na turma {id_turma.upper()}."

        gerados = 0
        for aluno in alunos:
            ok, _ = cls.emitir_boleto_individual(
                matricula=aluno["matricula"],
                tipo="mensalidade",
                valor=valor,
                data_vencimento=data_vencimento
            )
            if ok:
                gerados += 1

        return True, f"{gerados} boletos fictícios de mensalidade emitidos para a Turma {id_turma.upper()}."

    @classmethod
    def get_boleto_detalhes(cls, id_boleto):
        boleto = FinanceiroRepository.get_boleto_by_id(id_boleto)
        if boleto:
            boleto["linha_digitavel"] = cls.gerar_linha_digitavel_ficticia(boleto["id_boleto"], boleto["valor"])
        return boleto

    @classmethod
    def pagar_boleto_simulado(cls, id_boleto, user):
        """
        Simula a quitação do boleto.
        Verifica se o usuário é o responsável pelo aluno ou administrador.
        """
        boleto = FinanceiroRepository.get_boleto_by_id(id_boleto)
        if not boleto:
            return False, "Boleto não encontrado."

        if boleto["status"] == "pago":
            return False, "Este boleto já consta como pago."

        # Checagem de permissão: admin pode simular qualquer; responsável só dos seus alunos
        if not user.is_admin:
            if user.perfil != "responsavel":
                return False, "Apenas o responsável ou a administração podem pagar este boleto."
            if not AcademicRepository.is_responsavel_of_aluno(user.id_perfil, boleto["matricula"]):
                return False, "Você não tem permissão para pagar o boleto deste aluno."

        try:
            FinanceiroRepository.update_boleto_pagamento_simulado(id_boleto)
            return True, "Pagamento simulado registrado com sucesso! O status foi alterado para 'Pago'."
        except Exception as e:
            return False, f"Erro ao registrar pagamento simulado: {str(e)}"

    # --- FOLHA DE PAGAMENTO ---
    @classmethod
    def lancar_salario(cls, tipo_beneficiario, id_beneficiario, mes, ano, valor):
        try:
            val = Decimal(str(valor))
            if val <= 0:
                return False, "O valor do salário deve ser superior a zero."
        except Exception:
            return False, "Valor numérico inválido."

        if not (1 <= int(mes) <= 12):
            return False, "Mês de referência inválido (deve ser entre 1 e 12)."

        id_prof = id_beneficiario if tipo_beneficiario == "professor" else None
        id_func = id_beneficiario if tipo_beneficiario == "funcionario" else None

        try:
            id_folha = FinanceiroRepository.create_folha_pagamento(
                id_professor=id_prof,
                id_funcionario=id_func,
                mes_referencia=int(mes),
                ano_referencia=int(ano),
                valor=val
            )
            return True, f"Lançamento salarial #{id_folha} registrado na folha de pagamento!"
        except Exception as e:
            return False, f"Erro ao registrar salário na folha: {str(e)}"

    @classmethod
    def quitar_salario_simulado(cls, id_pagamento):
        """Marca o salário como 'pago' pelo administrativo."""
        try:
            FinanceiroRepository.update_salario_pagamento_simulado(id_pagamento)
            return True, "Salário marcado como pago com sucesso (simulação administrativa)."
        except Exception as e:
            return False, f"Erro ao atualizar status do salário: {str(e)}"

    @classmethod
    def get_salarios_usuario(cls, user):
        """Retorna exclusivamente os salários do usuário logado (Professor ou Funcionário)."""
        if user.perfil == "professor":
            return FinanceiroRepository.list_folha_by_professor(user.id_perfil)
        elif user.perfil == "funcionario":
            return FinanceiroRepository.list_folha_by_funcionario(user.id_perfil)
        return []

    # --- CONTRATOS PRESTADORES ---
    @classmethod
    def criar_contrato_prestador(cls, id_servico, descricao, valor, data_inicio, data_fim=None):
        try:
            val = Decimal(str(valor)) if valor else None
        except Exception:
            return False, "Valor de contrato inválido."

        if not data_inicio:
            return False, "A data de início de vigência é obrigatória."

        try:
            FinanceiroRepository.create_contrato_prestador(
                id_servico=id_servico,
                descricao=descricao,
                valor=val,
                data_inicio=data_inicio,
                data_fim=data_fim or None
            )
            return True, "Contrato com prestador cadastrado com sucesso!"
        except Exception as e:
            return False, f"Erro ao cadastrar contrato: {str(e)}"

    @classmethod
    def encerrar_contrato(cls, id_contrato):
        try:
            FinanceiroRepository.update_contrato_status(id_contrato, "encerrado")
            return True, "Contrato marcado como encerrado."
        except Exception as e:
            return False, f"Erro ao encerrar contrato: {str(e)}"
