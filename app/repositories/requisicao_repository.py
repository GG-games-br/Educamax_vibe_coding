from datetime import datetime
from app.repositories.db import get_db_connection
from app.repositories.mock_data import mock_db

class RequisicaoRepository:
    """
    Camada de acesso a dados para o Módulo de Requisições de Responsáveis:
    - Solicitação de farda, material didático, prova substitutiva ou 2ª chamada
    - Tramitação e resposta administrativa
    - Suporte automático a Modo Demonstração Offline (Fallback em Memória)
    """

    @staticmethod
    def create_requisicao(id_responsavel, matricula, tipo, descricao):
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = """
                        INSERT INTO requisicao (id_responsavel, matricula, tipo, descricao, status)
                        VALUES (%s, %s, %s, %s, 'pendente')
                    """
                    cursor.execute(query, (id_responsavel, matricula, tipo, descricao))
                conn.commit()
                return cursor.lastrowid
            finally:
                conn.close()
        except Exception:
            novo_id = max([r["id_requisicao"] for r in mock_db.requisicoes] + [0]) + 1
            aluno = next((a for a in mock_db.alunos if a["matricula"] == matricula), None)
            resp = next((r for r in mock_db.responsaveis if r["id_responsavel"] == id_responsavel), None)
            mock_db.requisicoes.insert(0, {
                "id_requisicao": novo_id,
                "id_responsavel": id_responsavel,
                "matricula": matricula,
                "tipo": tipo,
                "descricao": descricao,
                "status": "pendente",
                "resposta_administrativo": None,
                "id_funcionario_resposta": None,
                "data_solicitacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_resposta": None,
                "nome_aluno": aluno["nome"] if aluno else f"Aluno {matricula}",
                "nome_responsavel": resp["nome"] if resp else "Responsável",
                "cpf_responsavel": resp.get("cpf", "00000000000") if resp else "00000000000",
                "nome_funcionario_resposta": None
            })
            return novo_id

    @staticmethod
    def list_all_requisicoes(status=None):
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = """
                        SELECT 
                            rq.id_requisicao, rq.id_responsavel, rq.matricula, rq.tipo,
                            rq.descricao, rq.status, rq.resposta_administrativo,
                            rq.data_solicitacao, rq.data_resposta,
                            a.nome AS nome_aluno,
                            r.nome AS nome_responsavel, r.cpf AS cpf_responsavel,
                            f.nome AS nome_funcionario_resposta
                        FROM requisicao rq
                        JOIN aluno a ON rq.matricula = a.matricula
                        JOIN responsavel r ON rq.id_responsavel = r.id_responsavel
                        LEFT JOIN funcionario f ON rq.id_funcionario_resposta = f.id_funcionario
                    """
                    params = []
                    if status:
                        query += " WHERE rq.status = %s"
                        params.append(status)
                    query += " ORDER BY rq.data_solicitacao DESC"

                    cursor.execute(query, params)
                    return cursor.fetchall()
            finally:
                conn.close()
        except Exception:
            if status:
                return [r for r in mock_db.requisicoes if r["status"] == status]
            return mock_db.requisicoes

    @staticmethod
    def list_requisicoes_by_responsavel(id_responsavel):
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = """
                        SELECT 
                            rq.id_requisicao, rq.matricula, rq.tipo, rq.descricao,
                            rq.status, rq.resposta_administrativo,
                            rq.data_solicitacao, rq.data_resposta,
                            a.nome AS nome_aluno
                        FROM requisicao rq
                        JOIN aluno a ON rq.matricula = a.matricula
                        WHERE rq.id_responsavel = %s
                        ORDER BY rq.data_solicitacao DESC
                    """
                    cursor.execute(query, (id_responsavel,))
                    return cursor.fetchall()
            finally:
                conn.close()
        except Exception:
            return [r for r in mock_db.requisicoes if r["id_responsavel"] == id_responsavel]

    @staticmethod
    def get_requisicao_by_id(id_requisicao):
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = """
                        SELECT 
                            rq.id_requisicao, rq.id_responsavel, rq.matricula, rq.tipo,
                            rq.descricao, rq.status, rq.resposta_administrativo,
                            rq.data_solicitacao, rq.data_resposta,
                            a.nome AS nome_aluno,
                            r.nome AS nome_responsavel
                        FROM requisicao rq
                        JOIN aluno a ON rq.matricula = a.matricula
                        JOIN responsavel r ON rq.id_responsavel = r.id_responsavel
                        WHERE rq.id_requisicao = %s
                    """
                    cursor.execute(query, (id_requisicao,))
                    return cursor.fetchone()
            finally:
                conn.close()
        except Exception:
            for r in mock_db.requisicoes:
                if r["id_requisicao"] == id_requisicao:
                    return r
            return None

    @staticmethod
    def responder_requisicao(id_requisicao, status, resposta, id_funcionario):
        """Atualiza a requisição com parecer (aprovada ou negada) e funcionário responsável."""
        try:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    query = """
                        UPDATE requisicao
                        SET status = %s, resposta_administrativo = %s,
                            id_funcionario_resposta = %s, data_resposta = NOW()
                        WHERE id_requisicao = %s
                    """
                    cursor.execute(query, (status, resposta, id_funcionario, id_requisicao))
                conn.commit()
                return True
            finally:
                conn.close()
        except Exception:
            for r in mock_db.requisicoes:
                if r["id_requisicao"] == id_requisicao:
                    r["status"] = status
                    r["resposta_administrativo"] = resposta
                    r["id_funcionario_resposta"] = id_funcionario
                    r["data_resposta"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    r["nome_funcionario_resposta"] = "Administrador Geral"
                    return True
            return False
