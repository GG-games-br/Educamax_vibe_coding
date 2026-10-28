import unittest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from app import create_app
from app.models.user import User
from app.utils.pagination import Pagination
from app.utils.logging import get_module_logger
from app.services.notas_service import NotasService
from app.services.requisicao_service import RequisicaoService
from config import Config

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-escalabilidade-key"

class TestEscalabilidadeEModulos(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

    def test_pagination_utility(self):
        """Verifica a lógica de paginação reutilizável."""
        items = list(range(1, 101))  # 100 itens
        # Página 1 (10 por página)
        p1 = Pagination(page=1, per_page=10, total_count=100, items=items[:10])
        self.assertEqual(p1.total_pages, 10)
        self.assertFalse(p1.has_prev)
        self.assertTrue(p1.has_next)
        self.assertEqual(p1.next_num, 2)

        # Página 5
        p5 = Pagination(page=5, per_page=10, total_count=100, items=items[40:50])
        self.assertTrue(p5.has_prev)
        self.assertTrue(p5.has_next)
        self.assertEqual(p5.prev_num, 4)
        self.assertEqual(p5.next_num, 6)

    def test_module_logger_namespace(self):
        """Verifica se o logger retorna o namespace correto por módulo."""
        log = get_module_logger("financeiro")
        self.assertEqual(log.name, "educamax.financeiro")

    def test_nota_validation_rules(self):
        """Verifica a validação de nota entre 0 e 10."""
        # Inválidas
        val, nota, err = NotasService.validar_nota(-1)
        self.assertFalse(val)
        self.assertIn("entre 0,00 e 10,00", err)

        val, nota, err = NotasService.validar_nota(10.5)
        self.assertFalse(val)

        val, nota, err = NotasService.validar_nota("nota_invalida")
        self.assertFalse(val)

        # Válida
        val, nota, err = NotasService.validar_nota(8.75)
        self.assertTrue(val)
        self.assertEqual(nota, Decimal("8.75"))

    @patch("app.repositories.requisicao_repository.RequisicaoRepository.create_requisicao")
    @patch("app.repositories.academic_repository.AcademicRepository.is_responsavel_of_aluno")
    def test_criar_requisicao_responsavel(self, mock_is_resp, mock_create):
        """Responsável cria requisição para seu aluno dependente."""
        mock_is_resp.return_value = True
        mock_create.return_value = 101

        resp_user = User(id_conta=1, email="resp@teste.com", perfil="responsavel", id_perfil=3, nome="Pai")
        ok, msg = RequisicaoService.criar_requisicao(resp_user, 1001, "farda", "Solicito 2 uniformes novos.")
        self.assertTrue(ok)
        self.assertIn("sucesso", msg)
        mock_create.assert_called_once()

    @patch("app.repositories.requisicao_repository.RequisicaoRepository.get_requisicao_by_id")
    @patch("app.repositories.requisicao_repository.RequisicaoRepository.responder_requisicao")
    @patch("app.services.financeiro_service.FinanceiroService.emitir_boleto_individual")
    def test_responder_requisicao_com_geracao_de_boleto(self, mock_boleto, mock_resp, mock_get):
        """Ao aprovar requisição com taxa, gera automaticamente o boleto fictício correspondente."""
        mock_get.return_value = {
            "id_requisicao": 55,
            "matricula": 1001,
            "tipo": "segunda_chamada",
            "descricao": "2a chamada de Matematica"
        }
        mock_resp.return_value = True
        mock_boleto.return_value = (True, "Boleto gerado")

        admin_user = User(id_conta=2, email="admin@teste.com", perfil="funcionario", id_perfil=1, nome="Admin", acesso_dados_sensiveis=True)

        ok, msg = RequisicaoService.responder_requisicao(
            id_requisicao=55,
            status="aprovada",
            resposta="Autorizada 2a chamada.",
            user=admin_user,
            valor_boleto=30.00,
            vencimento_boleto="2026-10-15"
        )
        self.assertTrue(ok)
        mock_resp.assert_called_once()
        mock_boleto.assert_called_once_with(
            matricula=1001,
            tipo="segunda_chamada",
            valor=30.00,
            data_vencimento="2026-10-15",
            id_requisicao=55
        )

    def test_health_check_endpoint(self):
        """Verifica o endpoint de monitoramento /health."""
        with patch("app.blueprints.main.routes.get_db_connection") as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor
            res = self.client.get("/health")
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertEqual(data["status"], "online")
            self.assertEqual(data["app"], "EducaMax")
            self.assertEqual(data["database"], "ok")

if __name__ == "__main__":
    unittest.main()
