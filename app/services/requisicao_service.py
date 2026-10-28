from app.repositories.requisicao_repository import RequisicaoRepository
from app.repositories.academic_repository import AcademicRepository
from app.services.financeiro_service import FinanceiroService
from app.utils.logging import get_module_logger

logger = get_module_logger("requisicoes")

class RequisicaoService:
    """
    Camada de serviço para o módulo de requisições de responsáveis.
    """
    TIPOS_PERMITIDOS = ['farda', 'material', 'prova_substitutiva', 'segunda_chamada']

    @classmethod
    def criar_requisicao(cls, user, matricula, tipo, descricao):
        if tipo not in cls.TIPOS_PERMITIDOS:
            return False, f"Tipo de requisição inválido. Permitidos: {', '.join(cls.TIPOS_PERMITIDOS)}."

        if not descricao or len(descricao.strip()) < 5:
            return False, "A descrição da solicitação deve conter no mínimo 5 caracteres."

        # Validação de escopo: o aluno precisa pertencer ao responsável
        if not user.is_admin:
            if not AcademicRepository.is_responsavel_of_aluno(user.id_perfil, matricula):
                return False, "Você só pode realizar requisições para seus alunos dependentes vinculados."

        try:
            id_req = RequisicaoRepository.create_requisicao(
                id_responsavel=user.id_perfil,
                matricula=matricula,
                tipo=tipo,
                descricao=descricao.strip()
            )
            logger.info(f"Requisição #{id_req} criada com sucesso pelo responsável #{user.id_perfil}.")
            return True, f"Requisição #{id_req} enviada com sucesso para a secretaria escolar!"
        except Exception as e:
            logger.error(f"Erro ao criar requisição: {str(e)}")
            return False, f"Erro ao registrar requisição: {str(e)}"

    @classmethod
    def responder_requisicao(cls, id_requisicao, status, resposta, user, valor_boleto=None, vencimento_boleto=None):
        if status not in ('aprovada', 'negada'):
            return False, "Status de resposta inválido (deve ser 'aprovada' ou 'negada')."

        req = RequisicaoRepository.get_requisicao_by_id(id_requisicao)
        if not req:
            return False, "Requisição não localizada."

        try:
            RequisicaoRepository.responder_requisicao(
                id_requisicao=id_requisicao,
                status=status,
                resposta=resposta.strip() if resposta else "Solicitação analisada pela administração escolar.",
                id_funcionario=user.id_perfil
            )

            # Se aprovada e fornecido valor para taxa/material/2ª chamada, gera o boleto fictício vinculado
            if status == "aprovada" and valor_boleto and float(valor_boleto) > 0:
                try:
                    FinanceiroService.emitir_boleto_individual(
                        matricula=req["matricula"],
                        tipo=req["tipo"],
                        valor=valor_boleto,
                        data_vencimento=vencimento_boleto,
                        id_requisicao=id_requisicao
                    )
                    logger.info(f"Boleto fictício gerado automaticamente para requisição #{id_requisicao}.")
                except Exception as ex_b:
                    logger.warning(f"Boleto não gerado para requisição #{id_requisicao}: {str(ex_b)}")

            logger.info(f"Requisição #{id_requisicao} respondida como '{status}' por admin #{user.id_conta}.")
            return True, f"Requisição #{id_requisicao} atualizada para '{status}' com sucesso!"
        except Exception as e:
            logger.error(f"Erro ao responder requisição #{id_requisicao}: {str(e)}")
            return False, f"Erro ao registrar resposta: {str(e)}"
