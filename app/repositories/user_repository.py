import pymysql
from app.repositories.db import get_db_connection
from app.repositories.mock_data import mock_db
from app.models.user import User

class UserRepository:
    """
    Camada de acesso a dados para contas, perfis e autenticação.
    Utiliza consultas parametrizadas e transações explícitas.
    Suporte automático ao Modo Demonstração Offline.
    """

    @staticmethod
    def get_cargos():
        """Retorna todos os cargos cadastrados para o formulário de funcionários."""
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id_cargo, nome, acesso_dados_sensiveis FROM cargo ORDER BY nome ASC")
                    cargos = cursor.fetchall()
                    if not cargos:
                        default_cargos = [
                            ("Administrador", 1),
                            ("Secretário Acadêmico", 1),
                            ("Coordenador Pedagógico", 1),
                            ("Auxiliar Administrativo", 0)
                        ]
                        for nome_c, acesso_c in default_cargos:
                            cursor.execute(
                                "INSERT INTO cargo (nome, acesso_dados_sensiveis) VALUES (%s, %s)",
                                (nome_c, acesso_c)
                            )
                        conn.commit()
                        cursor.execute("SELECT id_cargo, nome, acesso_dados_sensiveis FROM cargo ORDER BY nome ASC")
                        cargos = cursor.fetchall()
                    return cargos
            finally:
                conn.close()
        except Exception:
            return mock_db.cargos

    @staticmethod
    def find_user_by_id(id_conta):
        """Busca os detalhes completos da conta e monta a instância de User."""
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = """
                        SELECT 
                            c.id_conta, c.email, c.ativo, 
                            COALESCE(c.status_conta, IF(c.ativo=1, 'ativo', 'pendente')) AS status_conta,
                            c.id_aluno, c.id_professor, c.id_funcionario, c.id_responsavel,
                            a.nome AS nome_aluno, a.matricula AS matricula_aluno,
                            p.nome AS nome_professor, p.matricula AS matricula_prof,
                            f.nome AS nome_funcionario, cg.nome AS cargo_nome, cg.acesso_dados_sensiveis,
                            r.nome AS nome_responsavel
                        FROM conta c
                        LEFT JOIN aluno a ON c.id_aluno = a.id_aluno
                        LEFT JOIN professor p ON c.id_professor = p.id_professor
                        LEFT JOIN funcionario f ON c.id_funcionario = f.id_funcionario
                        LEFT JOIN cargo cg ON f.id_cargo = cg.id_cargo
                        LEFT JOIN responsavel r ON c.id_responsavel = r.id_responsavel
                        WHERE c.id_conta = %s
                    """
                    cursor.execute(query, (id_conta,))
                    row = cursor.fetchone()
                    if row:
                        if row["id_aluno"]:
                            perfil = "aluno"
                            id_perfil = row["id_aluno"]
                            nome = row["nome_aluno"]
                            matricula = row["matricula_aluno"]
                            cargo_nome = None
                            acesso_dados = False
                        elif row["id_professor"]:
                            perfil = "professor"
                            id_perfil = row["id_professor"]
                            nome = row["nome_professor"]
                            matricula = row["matricula_prof"]
                            cargo_nome = None
                            acesso_dados = False
                        elif row["id_funcionario"]:
                            perfil = "funcionario"
                            id_perfil = row["id_funcionario"]
                            nome = row["nome_funcionario"]
                            matricula = None
                            cargo_nome = row["cargo_nome"]
                            acesso_dados = row["acesso_dados_sensiveis"]
                        elif row["id_responsavel"]:
                            perfil = "responsavel"
                            id_perfil = row["id_responsavel"]
                            nome = row["nome_responsavel"]
                            matricula = None
                            cargo_nome = None
                            acesso_dados = False
                        else:
                            perfil = "desconhecido"
                            id_perfil = None
                            nome = "Usuário do Sistema"
                            matricula = None
                            cargo_nome = None
                            acesso_dados = False

                        return User(
                            id_conta=row["id_conta"],
                            email=row["email"],
                            perfil=perfil,
                            id_perfil=id_perfil,
                            nome=nome,
                            ativo=row["ativo"],
                            status_conta=row["status_conta"],
                            matricula=matricula,
                            cargo_nome=cargo_nome,
                            acesso_dados_sensiveis=acesso_dados
                        )
            finally:
                conn.close()
        except Exception:
            pass

        # Fallback para execução sem banco de dados (offline / mock)
        if id_conta == 1:
            return User(
                id_conta=1,
                email="administrador@gmail.com",
                perfil="funcionario",
                id_perfil=1,
                nome="Administrador Geral",
                ativo=True,
                status_conta="ativo",
                cargo_nome="Administrador Geral",
                acesso_dados_sensiveis=True
            )
        if id_conta == 2:
            return User(
                id_conta=2,
                email="professor@gmail.com",
                perfil="professor",
                id_perfil=1,
                nome="Prof. Carlos Eduardo (Matemática)",
                ativo=True,
                status_conta="ativo",
                matricula=2001
            )
        if id_conta == 3:
            return User(
                id_conta=3,
                email="responsavel@gmail.com",
                perfil="responsavel",
                id_perfil=1,
                nome="Responsável EducaMax (Pai do Lucas)",
                ativo=True,
                status_conta="ativo"
            )
        if id_conta == 4:
            return User(
                id_conta=4,
                email="aluno@gmail.com",
                perfil="aluno",
                id_perfil=1,
                nome="Lucas Silva de Oliveira",
                ativo=True,
                status_conta="ativo",
                matricula=1001
            )

        return None

    @staticmethod
    def find_conta_for_auth(identificador):
        """
        Busca uma conta e seu hash de senha através de EMAIL ou NOME,
        conforme especificado em 02-autenticacao-contas.md.
        """
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query_email = """
                        SELECT 
                            c.id_conta, c.email, c.senha_hash, c.ativo,
                            COALESCE(c.status_conta, IF(c.ativo=1, 'ativo', 'pendente')) AS status_conta,
                            c.id_aluno, c.id_professor, c.id_funcionario, c.id_responsavel
                        FROM conta c
                        WHERE c.email = %s
                    """
                    cursor.execute(query_email, (identificador.strip(),))
                    row = cursor.fetchone()

                    if not row:
                        query_nome = """
                            SELECT 
                                c.id_conta, c.email, c.senha_hash, c.ativo,
                                COALESCE(c.status_conta, IF(c.ativo=1, 'ativo', 'pendente')) AS status_conta,
                                c.id_aluno, c.id_professor, c.id_funcionario, c.id_responsavel
                            FROM conta c
                            LEFT JOIN aluno a ON c.id_aluno = a.id_aluno
                            LEFT JOIN professor p ON c.id_professor = p.id_professor
                            LEFT JOIN funcionario f ON c.id_funcionario = f.id_funcionario
                            LEFT JOIN responsavel r ON c.id_responsavel = r.id_responsavel
                            WHERE LOWER(a.nome) = LOWER(%s)
                               OR LOWER(p.nome) = LOWER(%s)
                               OR LOWER(f.nome) = LOWER(%s)
                               OR LOWER(r.nome) = LOWER(%s)
                            LIMIT 1
                        """
                        cursor.execute(query_nome, (
                            identificador.strip(),
                            identificador.strip(),
                            identificador.strip(),
                            identificador.strip()
                        ))
                        row = cursor.fetchone()

                    return row
            finally:
                conn.close()
        except Exception:
            return None

    @staticmethod
    def check_duplicate_email(email):
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM conta WHERE email = %s", (email,))
                    if cursor.fetchone():
                        return True
                    cursor.execute("SELECT 1 FROM aluno WHERE email = %s", (email,))
                    if cursor.fetchone():
                        return True
                    cursor.execute("SELECT 1 FROM professor WHERE email = %s", (email,))
                    if cursor.fetchone():
                        return True
                    cursor.execute("SELECT 1 FROM funcionario WHERE email = %s", (email,))
                    if cursor.fetchone():
                        return True
                    cursor.execute("SELECT 1 FROM responsavel WHERE email = %s", (email,))
                    if cursor.fetchone():
                        return True
                    return False
            finally:
                conn.close()
        except Exception:
            return False

    @staticmethod
    def check_duplicate_cpf(cpf, tabela):
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = f"SELECT 1 FROM {tabela} WHERE cpf = %s"
                    cursor.execute(query, (cpf,))
                    return cursor.fetchone() is not None
            finally:
                conn.close()
        except Exception:
            return False

    @staticmethod
    def check_duplicate_matricula(matricula, tabela):
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = f"SELECT 1 FROM {tabela} WHERE matricula = %s"
                    cursor.execute(query, (matricula,))
                    return cursor.fetchone() is not None
            finally:
                conn.close()
        except Exception:
            return False

    @staticmethod
    def create_aluno_with_conta(aluno_data, senha_hash):
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    sql_aluno = """
                        INSERT INTO aluno (matricula, cpf, numero, nome, email)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_aluno, (
                        aluno_data["matricula"],
                        aluno_data["cpf"],
                        aluno_data.get("numero"),
                        aluno_data["nome"],
                        aluno_data["email"]
                    ))
                    id_aluno = cursor.lastrowid

                    sql_conta = """
                        INSERT INTO conta (email, senha_hash, ativo, status_conta, id_aluno)
                        VALUES (%s, %s, TRUE, 'ativo', %s)
                    """
                    cursor.execute(sql_conta, (
                        aluno_data["email"],
                        senha_hash,
                        id_aluno
                    ))
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        except Exception:
            novo_id = max([a["id_aluno"] for a in mock_db.alunos] + [0]) + 1
            mock_db.alunos.append({
                "id_aluno": novo_id,
                "matricula": aluno_data["matricula"],
                "cpf": aluno_data["cpf"],
                "nome": aluno_data["nome"],
                "email": aluno_data["email"],
                "numero": aluno_data.get("numero", ""),
                "id_turma": None,
                "ano": 2026
            })
            return True

    @staticmethod
    def create_responsavel_with_conta(resp_data, senha_hash):
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    sql_resp = """
                        INSERT INTO responsavel (cpf, numero, nome, email)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql_resp, (
                        resp_data["cpf"],
                        resp_data.get("numero"),
                        resp_data["nome"],
                        resp_data["email"]
                    ))
                    id_responsavel = cursor.lastrowid

                    sql_conta = """
                        INSERT INTO conta (email, senha_hash, ativo, status_conta, id_responsavel)
                        VALUES (%s, %s, TRUE, 'ativo', %s)
                    """
                    cursor.execute(sql_conta, (
                        resp_data["email"],
                        senha_hash,
                        id_responsavel
                    ))
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        except Exception:
            novo_id = max([r["id_responsavel"] for r in mock_db.responsaveis] + [0]) + 1
            mock_db.responsaveis.append({
                "id_responsavel": novo_id,
                "cpf": resp_data["cpf"],
                "nome": resp_data["nome"],
                "email": resp_data["email"],
                "numero": resp_data.get("numero", ""),
                "total_dependentes": 0
            })
            return True

    @staticmethod
    def create_professor_with_conta(prof_data, senha_hash):
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    sql_prof = """
                        INSERT INTO professor (matricula, cpf, numero, nome, email)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_prof, (
                        prof_data["matricula"],
                        prof_data["cpf"],
                        prof_data.get("numero"),
                        prof_data["nome"],
                        prof_data["email"]
                    ))
                    id_professor = cursor.lastrowid

                    sql_conta = """
                        INSERT INTO conta (email, senha_hash, ativo, status_conta, id_professor)
                        VALUES (%s, %s, FALSE, 'pendente', %s)
                    """
                    cursor.execute(sql_conta, (
                        prof_data["email"],
                        senha_hash,
                        id_professor
                    ))
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        except Exception:
            novo_id = len(mock_db.contas_pendentes) + 200
            mock_db.contas_pendentes.append({
                "id_conta": novo_id,
                "email": prof_data["email"],
                "ativo": 0,
                "status_conta": "pendente",
                "tipo_perfil": "Professor",
                "nome": prof_data["nome"],
                "cpf": prof_data["cpf"],
                "numero": prof_data.get("numero", ""),
                "cargo_nome": None
            })
            return True

    @staticmethod
    def create_funcionario_with_conta(func_data, senha_hash):
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    sql_func = """
                        INSERT INTO funcionario (cpf, numero, nome, email, id_cargo)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_func, (
                        func_data["cpf"],
                        func_data.get("numero"),
                        func_data["nome"],
                        func_data["email"],
                        func_data["id_cargo"]
                    ))
                    id_funcionario = cursor.lastrowid

                    sql_conta = """
                        INSERT INTO conta (email, senha_hash, ativo, status_conta, id_funcionario)
                        VALUES (%s, %s, FALSE, 'pendente', %s)
                    """
                    cursor.execute(sql_conta, (
                        func_data["email"],
                        senha_hash,
                        id_funcionario
                    ))
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        except Exception:
            novo_id = len(mock_db.contas_pendentes) + 200
            cargo = next((c for c in mock_db.cargos if c["id_cargo"] == func_data["id_cargo"]), None)
            mock_db.contas_pendentes.append({
                "id_conta": novo_id,
                "email": func_data["email"],
                "ativo": 0,
                "status_conta": "pendente",
                "tipo_perfil": "Funcionário / Administrativo",
                "nome": func_data["nome"],
                "cpf": func_data["cpf"],
                "numero": func_data.get("numero", ""),
                "cargo_nome": cargo["nome"] if cargo else "Funcionário"
            })
            return True

    @staticmethod
    def get_pending_contas():
        """Retorna todas as contas com status 'pendente' aguardando aprovação administrativa."""
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = """
                        SELECT 
                            c.id_conta, c.email, c.ativo,
                            COALESCE(c.status_conta, 'pendente') as status_conta,
                            CASE 
                                WHEN c.id_professor IS NOT NULL THEN 'Professor'
                                WHEN c.id_funcionario IS NOT NULL THEN 'Funcionário / Administrativo'
                                ELSE 'Outro'
                            END AS tipo_perfil,
                            COALESCE(p.nome, f.nome) AS nome,
                            COALESCE(p.cpf, f.cpf) AS cpf,
                            COALESCE(p.numero, f.numero) AS numero,
                            cg.nome AS cargo_nome
                        FROM conta c
                        LEFT JOIN professor p ON c.id_professor = p.id_professor
                        LEFT JOIN funcionario f ON c.id_funcionario = f.id_funcionario
                        LEFT JOIN cargo cg ON f.id_cargo = cg.id_cargo
                        WHERE (c.status_conta = 'pendente' OR (c.status_conta IS NULL AND c.ativo = FALSE))
                          AND (c.id_professor IS NOT NULL OR c.id_funcionario IS NOT NULL)
                        ORDER BY c.id_conta ASC
                    """
                    cursor.execute(query)
                    return cursor.fetchall()
            finally:
                conn.close()
        except Exception:
            return mock_db.contas_pendentes

    @staticmethod
    def update_status_conta(id_conta, status):
        """
        Atualiza o status de aprovação de uma conta:
        - 'ativo': ativo=TRUE, status_conta='ativo'
        - 'recusado': ativo=FALSE, status_conta='recusado'
        """
        if status not in ("ativo", "recusado"):
            raise ValueError("Status inválido")

        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    is_active = (status == "ativo")
                    query = """
                        UPDATE conta
                        SET ativo = %s, status_conta = %s
                        WHERE id_conta = %s
                    """
                    cursor.execute(query, (is_active, status, id_conta))
                conn.commit()
                return True
            finally:
                conn.close()
        except Exception:
            mock_db.contas_pendentes = [c for c in mock_db.contas_pendentes if c["id_conta"] != id_conta]
            return True
