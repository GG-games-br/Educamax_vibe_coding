import unittest
from unittest.mock import patch
from app import create_app
from app.models.user import User
from app.services.financeiro_service import FinanceiroService
from config import Config

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-financeiro-key"

class TestFinanceiroSimulado(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

    def test_linha_digitavel_ficticia_generator(self):
        """Verifica se a linha digitável simulada é gerada com o formato estético adequado."""
        linha = FinanceiroService.gerar_linha_digitavel_ficticia(15, 350.50)
        self.assertIn("00190.", linha)
        self.assertIn("0000035050", linha)

    @patch("app.repositories.financeiro_repository.FinanceiroRepository.get_boleto_by_id")
    @patch("app.repositories.financeiro_repository.FinanceiroRepository.update_boleto_pagamento_simulado")
    @patch("app.repositories.academic_repository.AcademicRepository.is_responsavel_of_aluno")
    def test_responsavel_pagamento_simulado_sucesso(self, mock_is_resp, mock_update, mock_get):
        """Responsável vinculado ao aluno consegue efetuar o pagamento simulado com sucesso."""
        mock_get.return_value = {
            "id_boleto": 10,
            "matricula": 1001,
            "valor": 450.00,
            "status": "pendente"
        }
        mock_is_resp.return_value = True
        mock_update.return_value = True

        user_resp = User(
            id_conta=1,
            email="pai@escola.com",
            perfil="responsavel",
            id_perfil=5,
            nome="Pai do Aluno"
        )

        ok, msg = FinanceiroService.pagar_boleto_simulado(10, user_resp)
        self.assertTrue(ok)
        self.assertIn("Pagamento simulado registrado com sucesso", msg)
        mock_update.assert_called_once_with(10)

    @patch("app.repositories.financeiro_repository.FinanceiroRepository.get_boleto_by_id")
    @patch("app.repositories.academic_repository.AcademicRepository.is_responsavel_of_aluno")
    def test_responsavel_nao_pode_pagar_boleto_de_outro_aluno(self, mock_is_resp, mock_get):
        """Responsável é impedido de pagar boleto de aluno não vinculado a ele."""
        mock_get.return_value = {
            "id_boleto": 11,
            "matricula": 9999,
            "valor": 500.00,
            "status": "pendente"
        }
        mock_is_resp.return_value = False  # Não é responsável por esse aluno!

        user_resp = User(
            id_conta=1,
            email="outro.pai@escola.com",
            perfil="responsavel",
            id_perfil=5,
            nome="Outro Pai"
        )

        ok, msg = FinanceiroService.pagar_boleto_simulado(11, user_resp)
        self.assertFalse(ok)
        self.assertIn("não tem permissão", msg)

    @patch("app.repositories.financeiro_repository.FinanceiroRepository.get_boleto_by_id")
    def test_boleto_ja_pago_nao_pode_ser_pago_novamente(self, mock_get):
        """Boleto já com status 'pago' rejeita novo pagamento."""
        mock_get.return_value = {
            "id_boleto": 12,
            "matricula": 1001,
            "valor": 300.00,
            "status": "pago"
        }
        user_resp = User(
            id_conta=1,
            email="pai@escola.com",
            perfil="responsavel",
            id_perfil=5,
            nome="Pai"
        )
        ok, msg = FinanceiroService.pagar_boleto_simulado(12, user_resp)
        self.assertFalse(ok)
        self.assertIn("já consta como pago", msg)

    @patch("app.repositories.financeiro_repository.FinanceiroRepository.list_folha_by_professor")
    def test_professor_visualiza_apenas_proprio_salario(self, mock_list):
        """Professor só recupera seus próprios registros salariais."""
        mock_list.return_value = [
            {"id_pagamento": 1, "mes_referencia": 9, "ano_referencia": 2026, "valor": 4000.00, "status": "pago"}
        ]
        user_prof = User(
            id_conta=2,
            email="prof@escola.com",
            perfil="professor",
            id_perfil=14,
            nome="Prof Roberto"
        )
        salarios = FinanceiroService.get_salarios_usuario(user_prof)
        self.assertEqual(len(salarios), 1)
        mock_list.assert_called_once_with(14)

    def test_rotas_financeiro_restricao_perfil(self):
        """Testa restrições de rotas por perfil no painel financeiro."""
        # Aluno é proibido de acessar painel financeiro admin
        aluno = User(
            id_conta=3,
            email="aluno@escola.com",
            perfil="aluno",
            id_perfil=1,
            nome="Aluno",
            matricula=1001
        )
        with self.client.session_transaction() as sess:
            sess["_user_id"] = "3"

        with patch("app.repositories.user_repository.UserRepository.find_user_by_id", return_value=aluno):
            res_admin = self.client.get("/financeiro/painel")
            self.assertEqual(res_admin.status_code, 403)

            res_boletos = self.client.get("/financeiro/meus-boletos")
            self.assertEqual(res_boletos.status_code, 403)

if __name__ == "__main__":
    unittest.main()
