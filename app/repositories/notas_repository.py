from app.repositories.db import get_db_connection

class NotasRepository:
    """
    Camada de acesso a dados para avaliações e notas:
    - Tarefas e notas de tarefas (tarefa, tarefa_aluno)
    - Provas e notas de provas (prova, prova_aluno)
    - Histórico escolar consolidado (historico_escolar)
    """

    # --- PROVAS ---
    @staticmethod
    def create_prova(id_professor, id_materia, descricao, data_prova):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO prova (id_professor, id_materia, descricao, data_prova)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (id_professor, id_materia, descricao, data_prova))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def list_provas_by_professor(id_professor):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        p.id_prova, p.id_materia, p.descricao, p.data_prova,
                        m.nome AS nome_materia
                    FROM prova p
                    JOIN materia m ON p.id_materia = m.id_materia
                    WHERE p.id_professor = %s
                    ORDER BY p.data_prova DESC, p.id_prova DESC
                """
                cursor.execute(query, (id_professor,))
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def lancar_nota_prova(id_prova, matricula, nota):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO prova_aluno (id_prova, matricula, nota)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE nota = VALUES(nota)
                """
                cursor.execute(query, (id_prova, matricula, nota))
            conn.commit()
            return True
        finally:
            conn.close()

    # --- TAREFAS ---
    @staticmethod
    def create_tarefa(id_professor, id_materia, descricao):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO tarefa (id_professor, id_materia, descricao)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(query, (id_professor, id_materia, descricao))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def list_tarefas_by_professor(id_professor):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        t.id_tarefa, t.id_materia, t.descricao, t.data_criacao,
                        m.nome AS nome_materia
                    FROM tarefa t
                    JOIN materia m ON t.id_materia = m.id_materia
                    WHERE t.id_professor = %s
                    ORDER BY t.data_criacao DESC, t.id_tarefa DESC
                """
                cursor.execute(query, (id_professor,))
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def lancar_nota_tarefa(id_tarefa, matricula, nota):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO tarefa_aluno (id_tarefa, matricula, nota)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE nota = VALUES(nota)
                """
                cursor.execute(query, (id_tarefa, matricula, nota))
            conn.commit()
            return True
        finally:
            conn.close()

    # --- HISTÓRICO ESCOLAR / BOLETIM ---
    @staticmethod
    def lancar_historico_nota(matricula, id_materia, id_ano, nota):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO historico_escolar (matricula, id_materia, id_ano, nota)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (matricula, id_materia, id_ano, nota))
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def get_boletim_aluno(matricula):
        """Retorna as notas consolidadas de um aluno em todas as matérias."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        h.id_historico, h.matricula, h.nota,
                        m.id_materia, m.nome AS nome_materia,
                        al.ano
                    FROM historico_escolar h
                    JOIN materia m ON h.id_materia = m.id_materia
                    JOIN ano_letivo al ON h.id_ano = al.id_ano
                    WHERE h.matricula = %s
                    ORDER BY m.nome ASC
                """
                cursor.execute(query, (matricula,))
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_provas_aluno(matricula):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        pa.nota, p.descricao, p.data_prova,
                        m.nome AS nome_materia, pr.nome AS nome_professor
                    FROM prova_aluno pa
                    JOIN prova p ON pa.id_prova = p.id_prova
                    JOIN materia m ON p.id_materia = m.id_materia
                    JOIN professor pr ON p.id_professor = pr.id_professor
                    WHERE pa.matricula = %s
                    ORDER BY p.data_prova DESC
                """
                cursor.execute(query, (matricula,))
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_tarefas_aluno(matricula):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        ta.nota, t.descricao, t.data_criacao,
                        m.nome AS nome_materia, pr.nome AS nome_professor
                    FROM tarefa_aluno ta
                    JOIN tarefa t ON ta.id_tarefa = t.id_tarefa
                    JOIN materia m ON t.id_materia = m.id_materia
                    JOIN professor pr ON t.id_professor = pr.id_professor
                    WHERE ta.matricula = %s
                    ORDER BY t.data_criacao DESC
                """
                cursor.execute(query, (matricula,))
                return cursor.fetchall()
        finally:
            conn.close()
