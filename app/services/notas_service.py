from decimal import Decimal
from app.repositories.notas_repository import NotasRepository
from app.repositories.academic_repository import AcademicRepository
from app.utils.logging import get_module_logger

logger = get_module_logger("notas")

class NotasService:
    """
    Camada de serviço para lançamento de notas, provas, tarefas e boletins.
    Valida constraints de nota entre 0 e 10.
    """

    @classmethod
    def validar_nota(cls, valor):
        try:
            nota = Decimal(str(valor))
            if not (0 <= nota <= 10):
                return False, None, "A nota deve estar estritamente entre 0,00 e 10,00."
            return True, nota, None
        except Exception:
            return False, None, "Valor de nota numérico inválido."

    @classmethod
    def criar_prova(cls, user, id_materia, descricao, data_prova):
        if not descricao or len(descricao.strip()) < 3:
            return False, "A descrição da avaliação deve ter no mínimo 3 caracteres."
        try:
            id_p = NotasRepository.create_prova(user.id_perfil, id_materia, descricao.strip(), data_prova)
            logger.info(f"Prova #{id_p} cadastrada pelo professor #{user.id_perfil}.")
            return True, f"Prova avaliativa cadastrada com sucesso!"
        except Exception as e:
            logger.error(f"Erro ao criar prova: {str(e)}")
            return False, f"Erro ao criar prova: {str(e)}"

    @classmethod
    def lancar_nota_prova(cls, id_prova, matricula, valor_nota):
        valida, nota, erro = cls.validar_nota(valor_nota)
        if not valida:
            return False, erro
        try:
            NotasRepository.lancar_nota_prova(id_prova, matricula, nota)
            return True, "Nota da prova lançada com sucesso!"
        except Exception as e:
            return False, f"Erro ao registrar nota da prova: {str(e)}"

    @classmethod
    def criar_tarefa(cls, user, id_materia, descricao):
        if not descricao or len(descricao.strip()) < 3:
            return False, "A descrição da tarefa deve ter no mínimo 3 caracteres."
        try:
            id_t = NotasRepository.create_tarefa(user.id_perfil, id_materia, descricao.strip())
            logger.info(f"Tarefa #{id_t} cadastrada pelo professor #{user.id_perfil}.")
            return True, f"Tarefa cadastrada com sucesso!"
        except Exception as e:
            return False, f"Erro ao cadastrar tarefa: {str(e)}"

    @classmethod
    def lancar_nota_tarefa(cls, id_tarefa, matricula, valor_nota):
        valida, nota, erro = cls.validar_nota(valor_nota)
        if not valida:
            return False, erro
        try:
            NotasRepository.lancar_nota_tarefa(id_tarefa, matricula, nota)
            return True, "Nota da tarefa registrada com sucesso!"
        except Exception as e:
            return False, f"Erro ao registrar nota da tarefa: {str(e)}"

    @classmethod
    def lancar_historico_disciplina(cls, matricula, id_materia, ano, valor_nota):
        valida, nota, erro = cls.validar_nota(valor_nota)
        if not valida:
            return False, erro
        try:
            id_ano = AcademicRepository.get_or_create_current_ano(ano)
            NotasRepository.lancar_historico_nota(matricula, id_materia, id_ano, nota)
            return True, "Média consolidada no histórico escolar com sucesso!"
        except Exception as e:
            return False, f"Erro ao lançar no histórico: {str(e)}"

    @classmethod
    def get_boletim_completo(cls, user, matricula):
        """
        Retorna o boletim do aluno, validando permissão de acesso no backend:
        - Admin: acesso livre.
        - Aluno: somente o seu próprio.
        - Responsável: somente de seus dependentes.
        - Professor: acesso autorizado.
        """
        if not user.is_admin:
            if user.perfil == "aluno" and int(matricula) != user.matricula:
                return None, "Acesso não autorizado ao boletim de outro estudante."
            if user.perfil == "responsavel" and not AcademicRepository.is_responsavel_of_aluno(user.id_perfil, matricula):
                return None, "Acesso não autorizado ao boletim deste aluno (não vinculado)."

        aluno = AcademicRepository.get_aluno_detalhes(matricula)
        if not aluno:
            return None, "Aluno não localizado."

        historico = NotasRepository.get_boletim_aluno(matricula)
        provas = NotasRepository.get_provas_aluno(matricula)
        tarefas = NotasRepository.get_tarefas_aluno(matricula)

        return {
            "aluno": aluno,
            "historico": historico,
            "provas": provas,
            "tarefas": tarefas
        }, None
