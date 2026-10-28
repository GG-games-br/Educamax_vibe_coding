from datetime import datetime
from app.repositories.db import get_db_connection
from app.repositories.mock_data import mock_db

class FinanceiroRepository:
    """
    Camada de acesso a dados para o Módulo Financeiro Simulado:
    - Boletos fictícios (mensalidades e requisições)
    - Folha de pagamento simulada (salários de professores e funcionários)
    - Contratos de prestadores de serviço
    - Suporte automático a Modo Demonstração Offline (Fallback em Memória)
    
    REGRA INEGOCIÁVEL (04-financeiro-simulado.md):
    Todos os valores são 100% fictícios. Nenhuma movimentação bancária real.
    """

    # --- BOLETOS FICTÍCIOS ---
    @staticmethod
    def create_boleto(matricula, tipo, valor, data_vencimento, id_requisicao=None):
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = """
                        INSERT INTO boleto (matricula, tipo, id_requisicao, valor, status, data_vencimento)
                        VALUES (%s, %s, %s, %s, 'pendente', %s)
                    """
                    cursor.execute(query, (matricula, tipo, id_requisicao, valor, data_vencimento))
                conn.commit()
                return cursor.lastrowid
            finally:
                conn.close()
        except Exception:
            novo_id = max([b["id_boleto"] for b in mock_db.boletos] + [0]) + 1
            aluno = next((a for a in mock_db.alunos if a["matricula"] == matricula), None)
            mock_db.boletos.insert(0, {
                "id_boleto": novo_id,
                "matricula": matricula,
                "tipo": tipo,
                "valor": float(valor),
                "status": "pendente",
                "data_vencimento": str(data_vencimento),
                "data_pagamento": None,
                "id_requisicao": id_requisicao,
                "nome_aluno": aluno["nome"] if aluno else f"Aluno {matricula}",
                "cpf_aluno": aluno.get("cpf", "00000000000") if aluno else "00000000000",
                "email_aluno": aluno.get("email", "") if aluno else ""
            })
            return novo_id

    @staticmethod
    def list_all_boletos():
        """Lista todos os boletos cadastrados na escola (visão administrativa)."""
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = """
                        SELECT 
                            b.id_boleto, b.matricula, b.tipo, b.valor, b.status,
                            b.data_vencimento, b.data_pagamento, b.id_requisicao,
                            a.nome AS nome_aluno, a.cpf AS cpf_aluno
                        FROM boleto b
                        JOIN aluno a ON b.matricula = a.matricula
                        ORDER BY b.data_vencimento DESC, b.id_boleto DESC
                    """
                    cursor.execute(query)
                    return cursor.fetchall()
            finally:
                conn.close()
        except Exception:
            return mock_db.boletos

    @staticmethod
    def get_boleto_by_id(id_boleto):
        """Busca um boleto por ID com dados do aluno associado."""
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = """
                        SELECT 
                            b.id_boleto, b.matricula, b.tipo, b.valor, b.status,
                            b.data_vencimento, b.data_pagamento, b.id_requisicao,
                            a.nome AS nome_aluno, a.cpf AS cpf_aluno, a.email AS email_aluno
                        FROM boleto b
                        JOIN aluno a ON b.matricula = a.matricula
                        WHERE b.id_boleto = %s
                    """
                    cursor.execute(query, (id_boleto,))
                    return cursor.fetchone()
            finally:
                conn.close()
        except Exception:
            for b in mock_db.boletos:
                if b["id_boleto"] == id_boleto:
                    return b
            return None

    @staticmethod
    def list_boletos_by_responsavel(id_responsavel):
        """Retorna apenas os boletos vinculados aos alunos deste responsável."""
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = """
                        SELECT 
                            b.id_boleto, b.matricula, b.tipo, b.valor, b.status,
                            b.data_vencimento, b.data_pagamento,
                            a.nome AS nome_aluno
                        FROM boleto b
                        JOIN aluno a ON b.matricula = a.matricula
                        JOIN responsavel_aluno ra ON a.matricula = ra.matricula
                        WHERE ra.id_responsavel = %s
                        ORDER BY b.status ASC, b.data_vencimento ASC
                    """
                    cursor.execute(query, (id_responsavel,))
                    return cursor.fetchall()
            finally:
                conn.close()
        except Exception:
            matriculas_resp = {ra["matricula"] for ra in mock_db.responsavel_aluno if ra["id_responsavel"] == id_responsavel}
            return [b for b in mock_db.boletos if b["matricula"] in matriculas_resp]

    @staticmethod
    def update_boleto_pagamento_simulado(id_boleto):
        """
        Simula a quitação do boleto: apenas altera o status para 'pago'
        e grava a data_pagamento com o momento atual.
        """
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = """
                        UPDATE boleto
                        SET status = 'pago', data_pagamento = NOW()
                        WHERE id_boleto = %s
                    """
                    cursor.execute(query, (id_boleto,))
                conn.commit()
                return True
            finally:
                conn.close()
        except Exception:
            for b in mock_db.boletos:
                if b["id_boleto"] == id_boleto:
                    b["status"] = "pago"
                    b["data_pagamento"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    return True
            return False

    # --- FOLHA DE PAGAMENTO (SALÁRIOS SIMULADOS) ---
    @staticmethod
    def create_folha_pagamento(id_professor, id_funcionario, mes_referencia, ano_referencia, valor):
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = """
                        INSERT INTO folha_pagamento 
                            (id_professor, id_funcionario, mes_referencia, ano_referencia, valor, status)
                        VALUES (%s, %s, %s, %s, %s, 'pendente')
                    """
                    cursor.execute(query, (id_professor, id_funcionario, mes_referencia, ano_referencia, valor))
                conn.commit()
                return cursor.lastrowid
            finally:
                conn.close()
        except Exception:
            novo_id = max([f["id_pagamento"] for f in mock_db.folhas_pagamento] + [0]) + 1
            nome_b = "Colaborador EducaMax"
            cargo_n = "Professor" if id_professor else "Funcionário"
            if id_professor:
                prof = next((p for p in mock_db.professores if p["id_professor"] == id_professor), None)
                if prof:
                    nome_b = prof["nome"]
            mock_db.folhas_pagamento.insert(0, {
                "id_pagamento": novo_id,
                "id_professor": id_professor,
                "id_funcionario": id_funcionario,
                "mes_referencia": mes_referencia,
                "ano_referencia": ano_referencia,
                "valor": float(valor),
                "status": "pendente",
                "data_pagamento": None,
                "nome_beneficiario": nome_b,
                "cpf_beneficiario": "00000000000",
                "tipo_cargo": "Professor" if id_professor else "Funcionário",
                "cargo_nome": cargo_n
            })
            return novo_id

    @staticmethod
    def list_all_folha_pagamento():
        """Lista geral de lançamentos de salários (visão administrativa)."""
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = """
                        SELECT 
                            fp.id_pagamento, fp.id_professor, fp.id_funcionario,
                            fp.mes_referencia, fp.ano_referencia, fp.valor, fp.status, fp.data_pagamento,
                            COALESCE(p.nome, f.nome) AS nome_beneficiario,
                            COALESCE(p.cpf, f.cpf) AS cpf_beneficiario,
                            CASE 
                                WHEN fp.id_professor IS NOT NULL THEN 'Professor'
                                ELSE 'Funcionário'
                            END AS tipo_cargo,
                            cg.nome AS cargo_nome
                        FROM folha_pagamento fp
                        LEFT JOIN professor p ON fp.id_professor = p.id_professor
                        LEFT JOIN funcionario f ON fp.id_funcionario = f.id_funcionario
                        LEFT JOIN cargo cg ON f.id_cargo = cg.id_cargo
                        ORDER BY fp.ano_referencia DESC, fp.mes_referencia DESC, fp.id_pagamento DESC
                    """
                    cursor.execute(query)
                    return cursor.fetchall()
            finally:
                conn.close()
        except Exception:
            return mock_db.folhas_pagamento

    @staticmethod
    def list_folha_by_professor(id_professor):
        """Retorna os lançamentos salariais exclusivos do professor logado."""
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = """
                        SELECT 
                            fp.id_pagamento, fp.mes_referencia, fp.ano_referencia,
                            fp.valor, fp.status, fp.data_pagamento,
                            p.nome AS nome_beneficiario, p.matricula
                        FROM folha_pagamento fp
                        JOIN professor p ON fp.id_professor = p.id_professor
                        WHERE fp.id_professor = %s
                        ORDER BY fp.ano_referencia DESC, fp.mes_referencia DESC
                    """
                    cursor.execute(query, (id_professor,))
                    return cursor.fetchall()
            finally:
                conn.close()
        except Exception:
            return [f for f in mock_db.folhas_pagamento if f.get("id_professor") == id_professor]

    @staticmethod
    def list_folha_by_funcionario(id_funcionario):
        """Retorna os lançamentos salariais exclusivos do funcionário logado."""
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = """
                        SELECT 
                            fp.id_pagamento, fp.mes_referencia, fp.ano_referencia,
                            fp.valor, fp.status, fp.data_pagamento,
                            f.nome AS nome_beneficiario, cg.nome AS cargo_nome
                        FROM folha_pagamento fp
                        JOIN funcionario f ON fp.id_funcionario = f.id_funcionario
                        LEFT JOIN cargo cg ON f.id_cargo = cg.id_cargo
                        WHERE fp.id_funcionario = %s
                        ORDER BY fp.ano_referencia DESC, fp.mes_referencia DESC
                    """
                    cursor.execute(query, (id_funcionario,))
                    return cursor.fetchall()
            finally:
                conn.close()
        except Exception:
            return [f for f in mock_db.folhas_pagamento if f.get("id_funcionario") == id_funcionario]

    @staticmethod
    def update_salario_pagamento_simulado(id_pagamento):
        """
        Simula a quitação do salário de um professor ou funcionário:
        apenas altera status para 'pago' e data_pagamento para NOW().
        """
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = """
                        UPDATE folha_pagamento
                        SET status = 'pago', data_pagamento = NOW()
                        WHERE id_pagamento = %s
                    """
                    cursor.execute(query, (id_pagamento,))
                conn.commit()
                return True
            finally:
                conn.close()
        except Exception:
            for f in mock_db.folhas_pagamento:
                if f["id_pagamento"] == id_pagamento:
                    f["status"] = "pago"
                    f["data_pagamento"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    return True
            return False

    # --- CONTRATOS COM PRESTADORES DE SERVIÇO ---
    @staticmethod
    def create_contrato_prestador(id_servico, descricao, valor, data_inicio, data_fim=None):
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = """
                        INSERT INTO contrato_prestador 
                            (id_servico, descricao, valor, data_inicio, data_fim, status)
                        VALUES (%s, %s, %s, %s, %s, 'ativo')
                    """
                    cursor.execute(query, (id_servico, descricao, valor, data_inicio, data_fim))
                conn.commit()
                return cursor.lastrowid
            finally:
                conn.close()
        except Exception:
            novo_id = max([c["id_contrato"] for c in mock_db.contratos] + [0]) + 1
            prestador = next((p for p in mock_db.prestadores if p["id_servico"] == id_servico), None)
            mock_db.contratos.insert(0, {
                "id_contrato": novo_id,
                "id_servico": id_servico,
                "descricao": descricao,
                "valor": float(valor) if valor else 0.0,
                "data_inicio": str(data_inicio),
                "data_fim": str(data_fim) if data_fim else None,
                "status": "ativo",
                "nome_prestador": prestador["servico"] if prestador else "Prestador",
                "cnpj": prestador["cnpj"] if prestador else ""
            })
            return novo_id

    @staticmethod
    def list_all_contratos():
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = """
                        SELECT 
                            c.id_contrato, c.id_servico, c.descricao, c.valor,
                            c.data_inicio, c.data_fim, c.status,
                            p.servico AS nome_prestador, p.cnpj
                        FROM contrato_prestador c
                        JOIN prestador_de_servico p ON c.id_servico = p.id_servico
                        ORDER BY c.status ASC, c.id_contrato DESC
                    """
                    cursor.execute(query)
                    return cursor.fetchall()
            finally:
                conn.close()
        except Exception:
            return mock_db.contratos

    @staticmethod
    def update_contrato_status(id_contrato, novo_status):
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = "UPDATE contrato_prestador SET status = %s WHERE id_contrato = %s"
                    cursor.execute(query, (novo_status, id_contrato))
                conn.commit()
                return True
            finally:
                conn.close()
        except Exception:
            for c in mock_db.contratos:
                if c["id_contrato"] == id_contrato:
                    c["status"] = novo_status
                    return True
            return False

    # --- TOTAIS E MÉTRICAS SIMULADAS PARA O DASHBOARD ---
    @staticmethod
    def get_dashboard_financeiro_metricas():
        """Calcula totais simulados para apresentação visual."""
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            COALESCE(SUM(CASE WHEN status = 'pago' THEN valor ELSE 0 END), 0) AS total_recebido_simulado,
                            COALESCE(SUM(CASE WHEN status = 'pendente' THEN valor ELSE 0 END), 0) AS total_a_receber_simulado,
                            COUNT(CASE WHEN status = 'pago' THEN 1 END) AS qtd_boletos_pagos,
                            COUNT(CASE WHEN status = 'pendente' THEN 1 END) AS qtd_boletos_pendentes
                        FROM boleto
                    """)
                    boletos_stats = cursor.fetchone()

                    cursor.execute("""
                        SELECT 
                            COALESCE(SUM(CASE WHEN status = 'pago' THEN valor ELSE 0 END), 0) AS total_salarios_pagos,
                            COALESCE(SUM(CASE WHEN status = 'pendente' THEN valor ELSE 0 END), 0) AS total_salarios_pendentes
                        FROM folha_pagamento
                    """)
                    salarios_stats = cursor.fetchone()

                    cursor.execute("""
                        SELECT 
                            COUNT(id_contrato) as total_contratos_ativos,
                            COALESCE(SUM(valor), 0) as total_valor_contratos
                        FROM contrato_prestador
                        WHERE status = 'ativo'
                    """)
                    contratos_stats = cursor.fetchone()

                    return {
                        **boletos_stats,
                        **salarios_stats,
                        **contratos_stats
                    }
            finally:
                conn.close()
        except Exception:
            total_rec = sum(b["valor"] for b in mock_db.boletos if b["status"] == "pago")
            total_pend = sum(b["valor"] for b in mock_db.boletos if b["status"] == "pendente")
            qtd_pagos = sum(1 for b in mock_db.boletos if b["status"] == "pago")
            qtd_pendentes = sum(1 for b in mock_db.boletos if b["status"] == "pendente")

            sal_pagos = sum(f["valor"] for f in mock_db.folhas_pagamento if f["status"] == "pago")
            sal_pendentes = sum(f["valor"] for f in mock_db.folhas_pagamento if f["status"] == "pendente")

            contratos_ativos = sum(1 for c in mock_db.contratos if c["status"] == "ativo")
            total_contratos_v = sum(c["valor"] for c in mock_db.contratos if c["status"] == "ativo")

            return {
                "total_recebido_simulado": total_rec,
                "total_a_receber_simulado": total_pend,
                "qtd_boletos_pagos": qtd_pagos,
                "qtd_boletos_pendentes": qtd_pendentes,
                "total_salarios_pagos": sal_pagos,
                "total_salarios_pendentes": sal_pendentes,
                "total_contratos_ativos": contratos_ativos,
                "total_valor_contratos": total_contratos_v
            }
