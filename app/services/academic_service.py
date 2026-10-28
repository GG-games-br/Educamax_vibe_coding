import re
from app.repositories.academic_repository import AcademicRepository

class AcademicService:
    """
    Camada de serviço para operações acadêmicas e validações de regras de negócio.
    """

    @classmethod
    def list_turmas(cls):
        return AcademicRepository.list_turmas()

    @classmethod
    def get_turmas_disponiveis(cls):
        """Retorna turmas do enum que ainda não foram criadas."""
        existentes = {t["id_turma"] for t in cls.list_turmas()}
        return [t for t in AcademicRepository.OPCOES_TURMAS if t not in existentes]

    @classmethod
    def add_turma(cls, id_turma):
        if id_turma not in AcademicRepository.OPCOES_TURMAS:
            return False, f"Identificador de turma inválido. Opções válidas: {', '.join(AcademicRepository.OPCOES_TURMAS)}."
        try:
            AcademicRepository.create_turma(id_turma)
            return True, f"Turma {id_turma.upper()} criada com sucesso!"
        except Exception as e:
            return False, f"Erro ao criar turma: {str(e)}"

    @classmethod
    def remove_turma(cls, id_turma):
        try:
            AcademicRepository.delete_turma(id_turma)
            return True, f"Turma {id_turma.upper()} removida com sucesso."
        except Exception as e:
            return False, f"Erro ao remover turma: {str(e)}"

    # --- MATÉRIAS ---
    @classmethod
    def list_materias(cls):
        return AcademicRepository.list_materias()

    @classmethod
    def add_materia(cls, nome):
        if not nome or len(nome.strip()) < 2:
            return False, "O nome da matéria deve ter no mínimo 2 caracteres."
        try:
            AcademicRepository.create_materia(nome)
            return True, f"Matéria '{nome.strip()}' cadastrada com sucesso!"
        except Exception as e:
            return False, f"Erro ao cadastrar matéria: {str(e)}"

    @classmethod
    def remove_materia(cls, id_materia):
        try:
            AcademicRepository.delete_materia(id_materia)
            return True, "Matéria removida com sucesso."
        except Exception as e:
            return False, f"Erro ao remover matéria: {str(e)}"

    # --- PRESTADORES ---
    @classmethod
    def list_prestadores(cls):
        return AcademicRepository.list_prestadores()

    @classmethod
    def add_prestador(cls, cnpj, servico, numero, email):
        clean_cnpj = re.sub(r"\D", "", cnpj or "")
        if len(clean_cnpj) != 14:
            return False, "O CNPJ deve conter exatamente 14 dígitos numéricos."
        if not servico or len(servico.strip()) < 3:
            return False, "A descrição do serviço prestado deve ter no mínimo 3 caracteres."
        try:
            AcademicRepository.create_prestador(clean_cnpj, servico, numero, email)
            return True, f"Prestador de serviço '{servico.strip()}' cadastrado com sucesso!"
        except Exception as e:
            return False, f"Erro ao cadastrar prestador: {str(e)}"

    @classmethod
    def remove_prestador(cls, id_servico):
        try:
            AcademicRepository.delete_prestador(id_servico)
            return True, "Prestador de serviço removido com sucesso."
        except Exception as e:
            return False, f"Erro ao remover prestador: {str(e)}"

    # --- VÍNCULOS ---
    @classmethod
    def list_alunos(cls):
        return AcademicRepository.list_alunos()

    @classmethod
    def list_professores(cls):
        return AcademicRepository.list_professores()

    @classmethod
    def list_responsaveis(cls):
        return AcademicRepository.list_responsaveis()

    @classmethod
    def vincular_aluno_turma(cls, matricula, id_turma, ano=2026):
        try:
            id_ano = AcademicRepository.get_or_create_current_ano(ano)
            AcademicRepository.vincular_aluno_turma(matricula, id_turma, id_ano)
            return True, f"Aluno matriculado na turma {id_turma.upper()} com sucesso!"
        except Exception as e:
            return False, f"Erro ao vincular aluno: {str(e)}"

    @classmethod
    def vincular_professor_turma(cls, id_professor, id_turma, ano=2026):
        try:
            id_ano = AcademicRepository.get_or_create_current_ano(ano)
            AcademicRepository.vincular_professor_turma(id_professor, id_turma, id_ano)
            return True, f"Professor alocado na turma {id_turma.upper()} com sucesso!"
        except Exception as e:
            return False, f"Erro ao alocar professor: {str(e)}"

    @classmethod
    def desvincular_professor_turma(cls, id_professor, id_turma, ano=2026):
        try:
            id_ano = AcademicRepository.get_or_create_current_ano(ano)
            AcademicRepository.desvincular_professor_turma(id_professor, id_turma, id_ano)
            return True, f"Professor desvinculado da turma {id_turma.upper()}."
        except Exception as e:
            return False, f"Erro ao desvincular professor: {str(e)}"

    @classmethod
    def vincular_responsavel_aluno(cls, id_responsavel, matricula, parentesco):
        try:
            AcademicRepository.vincular_responsavel_aluno(id_responsavel, matricula, parentesco or "Responsável")
            return True, "Dependente vinculado ao responsável com sucesso!"
        except Exception as e:
            return False, f"Erro ao vincular dependente: {str(e)}"

    @classmethod
    def desvincular_responsavel_aluno(cls, id_responsavel, matricula):
        try:
            AcademicRepository.desvincular_responsavel_aluno(id_responsavel, matricula)
            return True, "Vínculo de dependente removido com sucesso."
        except Exception as e:
            return False, f"Erro ao desvincular dependente: {str(e)}"

    # --- PERMISSÕES DE ACESSO DO PROFESSOR (03-perfis-permissoes.md) ---
    @classmethod
    def get_turmas_professor(cls, id_professor):
        return AcademicRepository.get_turmas_do_professor(id_professor)

    @classmethod
    def check_professor_has_turma(cls, id_professor, id_turma):
        """Retorna True se o professor leciona na turma informada."""
        return AcademicRepository.is_professor_of_turma(id_professor, id_turma)

    @classmethod
    def get_alunos_turma(cls, id_turma):
        return AcademicRepository.get_alunos_da_turma(id_turma)

    # --- PERMISSÕES DE ACESSO DO RESPONSÁVEL (03-perfis-permissoes.md) ---
    @classmethod
    def get_alunos_responsavel(cls, id_responsavel):
        return AcademicRepository.get_alunos_do_responsavel(id_responsavel)

    @classmethod
    def check_responsavel_has_aluno(cls, id_responsavel, matricula):
        """Retorna True se o aluno informado pertence ao responsável logado."""
        return AcademicRepository.is_responsavel_of_aluno(id_responsavel, matricula)

    # --- PERMISSÕES DE ACESSO DO ALUNO (03-perfis-permissoes.md) ---
    @classmethod
    def get_aluno_info(cls, matricula):
        return AcademicRepository.get_aluno_detalhes(matricula)
