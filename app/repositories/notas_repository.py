from datetime import datetime
from app.repositories.db import get_db_connection
from app.repositories.mock_data import mock_db

class NotasRepository:
    """
    Camada de acesso a dados para avaliações e notas:
    - Tarefas e notas de tarefas (tarefa, tarefa_aluno)
    - Provas e notas de provas (prova, prova_aluno)
    - Histórico escolar consolidado (historico_escolar)
    - Suporte automático a Modo Demonstração Offline (Fallback em Memória)
    """

    # --- PROVAS ---
    @staticmethod
    def create_prova(id_professor, id_materia, descricao, data_prova):
        try:
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
        except Exception:
            novo_id = max([p["id_prova"] for p in mock_db.provas] + [0]) + 1
            materia = next((m for m in mock_db.materias if m["id_materia"] == id_materia), None)
            mock_db.provas.insert(0, {
                "id_prova": novo_id,
                "id_professor": id_professor,
                "id_materia": id_materia,
                "descricao": descricao,
                "data_prova": str(data_prova),
                "nome_materia": materia["nome"] if materia else "Matéria"
            })
            return novo_id

    @staticmethod
    def list_provas_by_professor(id_professor):
        try:
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
        except Exception:
            return [p for p in mock_db.provas if p["id_professor"] == id_professor]

    @staticmethod
    def lancar_nota_prova(id_prova, matricula, nota):
        try:
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
        except Exception:
            prova = next((p for p in mock_db.provas if p["id_prova"] == id_prova), None)
            prof = next((p for p in mock_db.professores if p["id_professor"] == (prova["id_professor"] if prova else 1)), None)
            mock_db.provas_aluno = [pa for pa in mock_db.provas_aluno if not (pa["id_prova"] == id_prova and pa["matricula"] == matricula)]
            mock_db.provas_aluno.append({
                "id_prova": id_prova,
                "matricula": matricula,
                "nota": float(nota),
                "descricao": prova["descricao"] if prova else "Prova",
                "data_prova": prova["data_prova"] if prova else datetime.now().strftime("%Y-%m-%d"),
                "nome_materia": prova["nome_materia"] if prova else "Geral",
                "nome_professor": prof["nome"] if prof else "Professor"
            })
            return True

    # --- TAREFAS ---
    @staticmethod
    def create_tarefa(id_professor, id_materia, descricao):
        try:
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
        except Exception:
            novo_id = max([t["id_tarefa"] for t in mock_db.tarefas] + [0]) + 1
            materia = next((m for m in mock_db.materias if m["id_materia"] == id_materia), None)
            mock_db.tarefas.insert(0, {
                "id_tarefa": novo_id,
                "id_professor": id_professor,
                "id_materia": id_materia,
                "descricao": descricao,
                "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "nome_materia": materia["nome"] if materia else "Matéria"
            })
            return novo_id

    @staticmethod
    def list_tarefas_by_professor(id_professor):
        try:
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
        except Exception:
            return [t for t in mock_db.tarefas if t["id_professor"] == id_professor]

    @staticmethod
    def lancar_nota_tarefa(id_tarefa, matricula, nota):
        try:
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
        except Exception:
            tarefa = next((t for t in mock_db.tarefas if t["id_tarefa"] == id_tarefa), None)
            prof = next((p for p in mock_db.professores if p["id_professor"] == (tarefa["id_professor"] if tarefa else 1)), None)
            mock_db.tarefas_aluno = [ta for ta in mock_db.tarefas_aluno if not (ta["id_tarefa"] == id_tarefa and ta["matricula"] == matricula)]
            mock_db.tarefas_aluno.append({
                "id_tarefa": id_tarefa,
                "matricula": matricula,
                "nota": float(nota),
                "descricao": tarefa["descricao"] if tarefa else "Tarefa",
                "data_criacao": tarefa["data_criacao"] if tarefa else datetime.now().strftime("%Y-%m-%d"),
                "nome_materia": tarefa["nome_materia"] if tarefa else "Geral",
                "nome_professor": prof["nome"] if prof else "Professor"
            })
            return True

    # --- HISTÓRICO ESCOLAR / BOLETIM ---
    @staticmethod
    def lancar_historico_nota(matricula, id_materia, id_ano, nota):
        try:
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
        except Exception:
            materia = next((m for m in mock_db.materias if m["id_materia"] == id_materia), None)
            novo_id = max([h["id_historico"] for h in mock_db.historicos] + [0]) + 1
            mock_db.historicos = [h for h in mock_db.historicos if not (h["matricula"] == matricula and h["id_materia"] == id_materia and h["id_ano"] == id_ano)]
            mock_db.historicos.append({
                "id_historico": novo_id,
                "matricula": matricula,
                "id_materia": id_materia,
                "id_ano": id_ano,
                "ano": 2026,
                "nota": float(nota),
                "nome_materia": materia["nome"] if materia else "Matéria"
            })
            return True

    @staticmethod
    def get_boletim_aluno(matricula):
        """Retorna as notas consolidadas de um aluno em todas as matérias."""
        try:
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
        except Exception:
            return [h for h in mock_db.historicos if h["matricula"] == int(matricula)]

    @staticmethod
    def get_provas_aluno(matricula):
        try:
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
        except Exception:
            return [pa for pa in mock_db.provas_aluno if pa["matricula"] == int(matricula)]

    @staticmethod
    def get_tarefas_aluno(matricula):
        try:
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
        except Exception:
            return [ta for ta in mock_db.tarefas_aluno if ta["matricula"] == int(matricula)]
