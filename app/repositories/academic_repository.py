from app.repositories.db import get_db_connection

class AcademicRepository:
    """
    Repositório para operações de entidades acadêmicas e vínculos:
    - Turmas, Anos Letivos, Matérias, Prestadores de Serviço
    - Vínculos: Aluno-Turma, Professor-Turma, Responsável-Aluno
    - Consultas de escopo e checagem de permissões
    """

    # --- ANOS LETIVOS ---
    @staticmethod
    def get_or_create_current_ano(ano=2026):
        """Garante que o ano letivo de referência existe e retorna o id_ano."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id_ano, ano FROM ano_letivo WHERE ano = %s", (ano,))
                row = cursor.fetchone()
                if row:
                    return row["id_ano"]
                cursor.execute("INSERT INTO ano_letivo (ano) VALUES (%s)", (ano,))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def list_anos_letivos():
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id_ano, ano FROM ano_letivo ORDER BY ano DESC")
                return cursor.fetchall()
        finally:
            conn.close()

    # --- TURMAS ---
    OPCOES_TURMAS = ['1a', '1b', '2a', '2b', '3a', '3b', '4a', '4b', '5a', '5b', '6a', '6b']

    @staticmethod
    def list_turmas():
        """Lista todas as turmas cadastradas com contagem de alunos."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT t.id_turma, COUNT(at.matricula) as total_alunos
                    FROM turma t
                    LEFT JOIN aluno_turma at ON t.id_turma = at.id_turma
                    GROUP BY t.id_turma
                    ORDER BY t.id_turma ASC
                """
                cursor.execute(query)
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def create_turma(id_turma):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO turma (id_turma) VALUES (%s)", (id_turma,))
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def delete_turma(id_turma):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM aluno_turma WHERE id_turma = %s", (id_turma,))
                cursor.execute("DELETE FROM professor_turma WHERE id_turma = %s", (id_turma,))
                cursor.execute("DELETE FROM turma WHERE id_turma = %s", (id_turma,))
            conn.commit()
            return True
        finally:
            conn.close()

    # --- MATÉRIAS ---
    @staticmethod
    def list_materias():
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id_materia, nome FROM materia ORDER BY nome ASC")
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def create_materia(nome):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO materia (nome) VALUES (%s)", (nome.strip(),))
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def delete_materia(id_materia):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM materia WHERE id_materia = %s", (id_materia,))
            conn.commit()
            return True
        finally:
            conn.close()

    # --- PRESTADORES DE SERVIÇO ---
    @staticmethod
    def list_prestadores():
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id_servico, cnpj, servico, numero, email FROM prestador_de_servico ORDER BY servico ASC")
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def create_prestador(cnpj, servico, numero, email):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO prestador_de_servico (cnpj, servico, numero, email)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (cnpj, servico.strip(), numero.strip() if numero else None, email.strip() if email else None)
                )
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def delete_prestador(id_servico):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM contrato_prestador WHERE id_servico = %s", (id_servico,))
                cursor.execute("DELETE FROM prestador_de_servico WHERE id_servico = %s", (id_servico,))
            conn.commit()
            return True
        finally:
            conn.close()

    # --- LISTAGENS DE USUÁRIOS E PERFIS ---
    @staticmethod
    def list_alunos():
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        a.id_aluno, a.matricula, a.cpf, a.nome, a.email, a.numero,
                        at.id_turma, al.ano
                    FROM aluno a
                    LEFT JOIN aluno_turma at ON a.matricula = at.matricula
                    LEFT JOIN ano_letivo al ON at.id_ano = al.id_ano
                    ORDER BY a.nome ASC
                """
                cursor.execute(query)
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def list_professores():
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        p.id_professor, p.matricula, p.cpf, p.nome, p.email, p.numero,
                        COUNT(pt.id_turma) as total_turmas
                    FROM professor p
                    LEFT JOIN professor_turma pt ON p.id_professor = pt.id_professor
                    GROUP BY p.id_professor, p.matricula, p.cpf, p.nome, p.email, p.numero
                    ORDER BY p.nome ASC
                """
                cursor.execute(query)
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def list_responsaveis():
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        r.id_responsavel, r.cpf, r.nome, r.email, r.numero,
                        COUNT(ra.matricula) as total_dependentes
                    FROM responsavel r
                    LEFT JOIN responsavel_aluno ra ON r.id_responsavel = ra.id_responsavel
                    GROUP BY r.id_responsavel, r.cpf, r.nome, r.email, r.numero
                    ORDER BY r.nome ASC
                """
                cursor.execute(query)
                return cursor.fetchall()
        finally:
            conn.close()

    # --- VÍNCULOS ACADÊMICOS ---
    @staticmethod
    def vincular_aluno_turma(matricula, id_turma, id_ano):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO aluno_turma (matricula, id_turma, id_ano)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE id_turma = VALUES(id_turma)
                    """,
                    (matricula, id_turma, id_ano)
                )
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def desvincular_aluno_turma(matricula, id_turma, id_ano):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM aluno_turma WHERE matricula = %s AND id_turma = %s AND id_ano = %s",
                    (matricula, id_turma, id_ano)
                )
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def vincular_professor_turma(id_professor, id_turma, id_ano):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO professor_turma (id_professor, id_turma, id_ano)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE id_turma = id_turma
                    """,
                    (id_professor, id_turma, id_ano)
                )
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def desvincular_professor_turma(id_professor, id_turma, id_ano):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM professor_turma WHERE id_professor = %s AND id_turma = %s AND id_ano = %s",
                    (id_professor, id_turma, id_ano)
                )
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def vincular_responsavel_aluno(id_responsavel, matricula, parentesco="Responsável Legal"):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO responsavel_aluno (id_responsavel, matricula, parentesco)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE parentesco = VALUES(parentesco)
                    """,
                    (id_responsavel, matricula, parentesco)
                )
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def desvincular_responsavel_aluno(id_responsavel, matricula):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM responsavel_aluno WHERE id_responsavel = %s AND matricula = %s",
                    (id_responsavel, matricula)
                )
            conn.commit()
            return True
        finally:
            conn.close()

    # --- MÉTODOS DE CHECAGEM DE PERMISSÕES ESPECÍFICAS (03-perfis-permissoes.md) ---

    @staticmethod
    def get_turmas_do_professor(id_professor):
        """Retorna apenas as turmas associadas ao professor logado."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT pt.id_turma, al.ano, COUNT(at.matricula) as total_alunos
                    FROM professor_turma pt
                    JOIN ano_letivo al ON pt.id_ano = al.id_ano
                    LEFT JOIN aluno_turma at ON pt.id_turma = at.id_turma AND pt.id_ano = at.id_ano
                    WHERE pt.id_professor = %s
                    GROUP BY pt.id_turma, al.ano
                    ORDER BY pt.id_turma ASC
                """
                cursor.execute(query, (id_professor,))
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def is_professor_of_turma(id_professor, id_turma):
        """Valida no backend se o professor leciona na turma informada."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = "SELECT 1 FROM professor_turma WHERE id_professor = %s AND id_turma = %s LIMIT 1"
                cursor.execute(query, (id_professor, id_turma))
                return cursor.fetchone() is not None
        finally:
            conn.close()

    @staticmethod
    def get_alunos_da_turma(id_turma):
        """Retorna os alunos matriculados em uma turma."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT a.matricula, a.nome, a.email, a.numero
                    FROM aluno a
                    JOIN aluno_turma at ON a.matricula = at.matricula
                    WHERE at.id_turma = %s
                    ORDER BY a.nome ASC
                """
                cursor.execute(query, (id_turma,))
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_alunos_do_responsavel(id_responsavel):
        """Retorna apenas os alunos vinculados ao responsável logado."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        a.matricula, a.nome, a.email, a.numero, 
                        ra.parentesco, at.id_turma
                    FROM aluno a
                    JOIN responsavel_aluno ra ON a.matricula = ra.matricula
                    LEFT JOIN aluno_turma at ON a.matricula = at.matricula
                    WHERE ra.id_responsavel = %s
                    ORDER BY a.nome ASC
                """
                cursor.execute(query, (id_responsavel,))
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def is_responsavel_of_aluno(id_responsavel, matricula):
        """Valida no backend se o responsável possui vínculo com a matrícula indicada."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = "SELECT 1 FROM responsavel_aluno WHERE id_responsavel = %s AND matricula = %s LIMIT 1"
                cursor.execute(query, (id_responsavel, matricula))
                return cursor.fetchone() is not None
        finally:
            conn.close()

    @staticmethod
    def get_aluno_detalhes(matricula):
        """Retorna os dados cadastrais e turma de um aluno específico."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        a.matricula, a.nome, a.cpf, a.email, a.numero,
                        at.id_turma, al.ano
                    FROM aluno a
                    LEFT JOIN aluno_turma at ON a.matricula = at.matricula
                    LEFT JOIN ano_letivo al ON at.id_ano = al.id_ano
                    WHERE a.matricula = %s
                """
                cursor.execute(query, (matricula,))
                return cursor.fetchone()
        finally:
            conn.close()
