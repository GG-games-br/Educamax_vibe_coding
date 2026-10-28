from app.repositories.db import get_db_connection

class RequisicaoRepository:
    """
    Camada de acesso a dados para o Módulo de Requisições de Responsáveis:
    - Solicitação de farda, material didático, prova substitutiva ou 2ª chamada
    - Tramitação e resposta administrativa
    """

    @staticmethod
    def create_requisicao(id_responsavel, matricula, tipo, descricao):
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

    @staticmethod
    def list_all_requisicoes(status=None):
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

    @staticmethod
    def list_requisicoes_by_responsavel(id_responsavel):
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

    @staticmethod
    def get_requisicao_by_id(id_requisicao):
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

    @staticmethod
    def responder_requisicao(id_requisicao, status, resposta, id_funcionario):
        """Atualiza a requisição com parecer (aprovada ou negada) e funcionário responsável."""
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
