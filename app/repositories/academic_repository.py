from app.repositories.db import get_db_connection
from app.repositories.mock_data import mock_db

class AcademicRepository:
    """
    Repositório para operações de entidades acadêmicas e vínculos:
    - Turmas, Anos Letivos, Matérias, Prestadores de Serviço
    - Vínculos: Aluno-Turma, Professor-Turma, Responsável-Aluno
    - Consultas de escopo e checagem de permissões
    - Suporte automático a Modo Demonstração Offline (Fallback em Memória)
    """

    # --- ANOS LETIVOS ---
    @staticmethod
    def get_or_create_current_ano(ano=2026):
        """Garante que o ano letivo de referência existe e retorna o id_ano."""
        try:
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
        except Exception:
            for al in mock_db.anos_letivos:
                if al["ano"] == ano:
                    return al["id_ano"]
            novo_id = len(mock_db.anos_letivos) + 1
            mock_db.anos_letivos.append({"id_ano": novo_id, "ano": ano})
            return novo_id

    @staticmethod
    def list_anos_letivos():
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id_ano, ano FROM ano_letivo ORDER BY ano DESC")
                    return cursor.fetchall()
            finally:
                conn.close()
        except Exception:
            return mock_db.anos_letivos

    # --- TURMAS ---
    OPCOES_TURMAS = ['1a', '1b', '2a', '2b', '3a', '3b', '4a', '4b', '5a', '5b', '6a', '6b']

    @staticmethod
    def list_turmas():
        """Lista todas as turmas cadastradas com contagem de alunos."""
        try:
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
        except Exception:
            return mock_db.turmas

    @staticmethod
    def create_turma(id_turma):
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO turma (id_turma) VALUES (%s)", (id_turma,))
                conn.commit()
                return True
            finally:
                conn.close()
        except Exception:
            if not any(t["id_turma"] == id_turma for t in mock_db.turmas):
                mock_db.turmas.append({"id_turma": id_turma, "total_alunos": 0})
            return True

    @staticmethod
    def delete_turma(id_turma):
        try:
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
        except Exception:
            mock_db.turmas = [t for t in mock_db.turmas if t["id_turma"] != id_turma]
            mock_db.aluno_turma = [at for at in mock_db.aluno_turma if at["id_turma"] != id_turma]
            mock_db.professor_turma = [pt for pt in mock_db.professor_turma if pt["id_turma"] != id_turma]
            return True

    # --- MATÉRIAS ---
    @staticmethod
    def list_materias():
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id_materia, nome FROM materia ORDER BY nome ASC")
                    return cursor.fetchall()
            finally:
                conn.close()
        except Exception:
            return mock_db.materias

    @staticmethod
    def create_materia(nome):
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO materia (nome) VALUES (%s)", (nome.strip(),))
                conn.commit()
                return True
            finally:
                conn.close()
        except Exception:
            novo_id = max([m["id_materia"] for m in mock_db.materias] + [0]) + 1
            mock_db.materias.append({"id_materia": novo_id, "nome": nome.strip()})
            return True

    @staticmethod
    def delete_materia(id_materia):
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM materia WHERE id_materia = %s", (id_materia,))
                conn.commit()
                return True
            finally:
                conn.close()
        except Exception:
            mock_db.materias = [m for m in mock_db.materias if m["id_materia"] != id_materia]
            return True

    # --- PRESTADORES DE SERVIÇO ---
    @staticmethod
    def list_prestadores():
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id_servico, cnpj, servico, numero, email FROM prestador_de_servico ORDER BY servico ASC")
                    return cursor.fetchall()
            finally:
                conn.close()
        except Exception:
            return mock_db.prestadores

    @staticmethod
    def create_prestador(cnpj, servico, numero, email):
        try:
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
        except Exception:
            novo_id = max([p["id_servico"] for p in mock_db.prestadores] + [0]) + 1
            mock_db.prestadores.append({
                "id_servico": novo_id,
                "cnpj": cnpj,
                "servico": servico.strip(),
                "numero": numero.strip() if numero else None,
                "email": email.strip() if email else None
            })
            return True

    @staticmethod
    def delete_prestador(id_servico):
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM contrato_prestador WHERE id_servico = %s", (id_servico,))
                    cursor.execute("DELETE FROM prestador_de_servico WHERE id_servico = %s", (id_servico,))
                conn.commit()
                return True
            finally:
                conn.close()
        except Exception:
            mock_db.prestadores = [p for p in mock_db.prestadores if p["id_servico"] != id_servico]
            mock_db.contratos = [c for c in mock_db.contratos if c["id_servico"] != id_servico]
            return True

    # --- LISTAGENS DE USUÁRIOS E PERFIS ---
    @staticmethod
    def list_alunos():
        try:
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
        except Exception:
            return mock_db.alunos

    @staticmethod
    def list_professores():
        try:
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
        except Exception:
            return mock_db.professores

    @staticmethod
    def list_responsaveis():
        try:
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
        except Exception:
            return mock_db.responsaveis

    # --- VÍNCULOS ACADÊMICOS ---
    @staticmethod
    def vincular_aluno_turma(matricula, id_turma, id_ano):
        try:
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
        except Exception:
            for al in mock_db.alunos:
                if al["matricula"] == matricula:
                    al["id_turma"] = id_turma
            # Atualiza vínculo e contagem
            mock_db.aluno_turma = [at for at in mock_db.aluno_turma if at["matricula"] != matricula]
            mock_db.aluno_turma.append({"matricula": matricula, "id_turma": id_turma, "id_ano": id_ano})
            for t in mock_db.turmas:
                t["total_alunos"] = sum(1 for at in mock_db.aluno_turma if at["id_turma"] == t["id_turma"])
            return True

    @staticmethod
    def desvincular_aluno_turma(matricula, id_turma, id_ano):
        try:
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
        except Exception:
            mock_db.aluno_turma = [at for at in mock_db.aluno_turma if not (at["matricula"] == matricula and at["id_turma"] == id_turma)]
            for al in mock_db.alunos:
                if al["matricula"] == matricula:
                    al["id_turma"] = None
            return True

    @staticmethod
    def vincular_professor_turma(id_professor, id_turma, id_ano):
        try:
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
        except Exception:
            if not any(pt["id_professor"] == id_professor and pt["id_turma"] == id_turma for pt in mock_db.professor_turma):
                mock_db.professor_turma.append({"id_professor": id_professor, "id_turma": id_turma, "id_ano": id_ano})
            for p in mock_db.professores:
                if p["id_professor"] == id_professor:
                    p["total_turmas"] = sum(1 for pt in mock_db.professor_turma if pt["id_professor"] == id_professor)
            return True

    @staticmethod
    def desvincular_professor_turma(id_professor, id_turma, id_ano):
        try:
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
        except Exception:
            mock_db.professor_turma = [pt for pt in mock_db.professor_turma if not (pt["id_professor"] == id_professor and pt["id_turma"] == id_turma)]
            return True

    @staticmethod
    def vincular_responsavel_aluno(id_responsavel, matricula, parentesco="Responsável Legal"):
        try:
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
        except Exception:
            mock_db.responsavel_aluno = [ra for ra in mock_db.responsavel_aluno if not (ra["id_responsavel"] == id_responsavel and ra["matricula"] == matricula)]
            mock_db.responsavel_aluno.append({"id_responsavel": id_responsavel, "matricula": matricula, "parentesco": parentesco})
            return True

    @staticmethod
    def desvincular_responsavel_aluno(id_responsavel, matricula):
        try:
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
        except Exception:
            mock_db.responsavel_aluno = [ra for ra in mock_db.responsavel_aluno if not (ra["id_responsavel"] == id_responsavel and ra["matricula"] == matricula)]
            return True

    # --- MÉTODOS DE CHECAGEM DE PERMISSÕES ESPECÍFICAS (03-perfis-permissoes.md) ---

    @staticmethod
    def get_turmas_do_professor(id_professor):
        """Retorna apenas as turmas associadas ao professor logado."""
        try:
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
        except Exception:
            turmas_prof = [pt["id_turma"] for pt in mock_db.professor_turma if pt["id_professor"] == id_professor]
            return [t for t in mock_db.turmas if t["id_turma"] in turmas_prof]

    @staticmethod
    def is_professor_of_turma(id_professor, id_turma):
        """Valida no backend se o professor leciona na turma informada."""
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = "SELECT 1 FROM professor_turma WHERE id_professor = %s AND id_turma = %s LIMIT 1"
                    cursor.execute(query, (id_professor, id_turma))
                    return cursor.fetchone() is not None
            finally:
                conn.close()
        except Exception:
            return any(pt["id_professor"] == id_professor and pt["id_turma"] == id_turma for pt in mock_db.professor_turma)

    @staticmethod
    def get_alunos_da_turma(id_turma):
        """Retorna os alunos matriculados em uma turma."""
        try:
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
        except Exception:
            return [a for a in mock_db.alunos if a.get("id_turma") == id_turma]

    @staticmethod
    def get_alunos_do_responsavel(id_responsavel):
        """Retorna apenas os alunos vinculados ao responsável logado."""
        try:
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
        except Exception:
            matriculas_resp = {ra["matricula"]: ra.get("parentesco", "Responsável") for ra in mock_db.responsavel_aluno if ra["id_responsavel"] == id_responsavel}
            res = []
            for a in mock_db.alunos:
                if a["matricula"] in matriculas_resp:
                    item = dict(a)
                    item["parentesco"] = matriculas_resp[a["matricula"]]
                    res.append(item)
            return res

    @staticmethod
    def is_responsavel_of_aluno(id_responsavel, matricula):
        """Valida no backend se o responsável possui vínculo com a matrícula indicada."""
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = "SELECT 1 FROM responsavel_aluno WHERE id_responsavel = %s AND matricula = %s LIMIT 1"
                    cursor.execute(query, (id_responsavel, matricula))
                    return cursor.fetchone() is not None
            finally:
                conn.close()
        except Exception:
            return any(ra["id_responsavel"] == id_responsavel and ra["matricula"] == matricula for ra in mock_db.responsavel_aluno)

    @staticmethod
    def get_aluno_detalhes(matricula):
        """Retorna os dados cadastrais e turma de um aluno específico."""
        try:
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
        except Exception:
            for a in mock_db.alunos:
                if a["matricula"] == int(matricula):
                    return a
            return None
