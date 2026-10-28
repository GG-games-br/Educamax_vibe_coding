import unittest
from unittest.mock import patch, MagicMock
from werkzeug.security import generate_password_hash
from app import create_app
from app.models.user import User
from app.services.auth_service import AuthService
from config import Config

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-key"

class TestAuthModule(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

    def test_user_model_properties(self):
        """Testa propriedades da entidade User e controle de permissões."""
        # Aluno ativo
        u_aluno = User(
            id_conta=1,
            email="aluno@escola.com",
            perfil="aluno",
            id_perfil=10,
            nome="Aluno Teste",
            ativo=True,
            status_conta="ativo"
        )
        self.assertEqual(u_aluno.id, "1")
        self.assertTrue(u_aluno.is_active)
        self.assertFalse(u_aluno.is_admin)

        # Professor pendente
        u_prof_pendente = User(
            id_conta=2,
            email="prof@escola.com",
            perfil="professor",
            id_perfil=5,
            nome="Prof Teste",
            ativo=False,
            status_conta="pendente"
        )
        self.assertFalse(u_prof_pendente.is_active)
        self.assertFalse(u_prof_pendente.is_admin)

        # Funcionário administrativo
        u_admin = User(
            id_conta=3,
            email="admin@escola.com",
            perfil="funcionario",
            id_perfil=2,
            nome="Admin Teste",
            ativo=True,
            status_conta="ativo",
            cargo_nome="Administrador Geral",
            acesso_dados_sensiveis=True
        )
        self.assertTrue(u_admin.is_active)
        self.assertTrue(u_admin.is_admin)

    def test_validation_common_fields(self):
        """Testa validação de entrada de dados no AuthService."""
        # Dados inválidos
        errors, cpf = AuthService._validate_common_fields("Jo", "email_invalido", "123", "123", "456")
        self.assertIn("O nome deve ter no mínimo 3 caracteres.", errors)
        self.assertIn("Informe um endereço de e-mail válido.", errors)
        self.assertIn("O CPF deve conter exatamente 11 dígitos numéricos.", errors)
        self.assertIn("A senha deve ter no mínimo 6 caracteres.", errors)
        self.assertIn("A confirmação de senha não confere com a senha informada.", errors)

        # Dados válidos
        errors, cpf = AuthService._validate_common_fields(
            "Maria Oliveira", "maria@teste.com", "123.456.789-01", "senha123", "senha123"
        )
        self.assertEqual(len(errors), 0)
        self.assertEqual(cpf, "12345678901")

    @patch("app.repositories.user_repository.UserRepository.find_conta_for_auth")
    def test_authenticate_invalid_credentials(self, mock_find):
        """Testa autenticação com credenciais inexistentes ou incorretas."""
        mock_find.return_value = None
        user, err = AuthService.authenticate("usuario@teste.com", "senha123")
        self.assertIsNone(user)
        self.assertIn("Credenciais inválidas", err)

    @patch("app.repositories.user_repository.UserRepository.find_user_by_id")
    @patch("app.repositories.user_repository.UserRepository.find_conta_for_auth")
    def test_authenticate_pending_account_blocks_login(self, mock_find, mock_user):
        """Testa se conta pendente de aprovação bloqueia o login com aviso explicativo."""
        mock_find.return_value = {
            "id_conta": 10,
            "email": "prof.novo@escola.com",
            "senha_hash": generate_password_hash("senha123"),
            "ativo": False,
            "status_conta": "pendente",
            "id_aluno": None,
            "id_professor": 7,
            "id_funcionario": None,
            "id_responsavel": None
        }

        user, err = AuthService.authenticate("prof.novo@escola.com", "senha123")
        self.assertIsNone(user)
        self.assertIn("aguarda aprovação", err)

    @patch("app.repositories.user_repository.UserRepository.find_user_by_id")
    @patch("app.repositories.user_repository.UserRepository.find_conta_for_auth")
    def test_authenticate_active_success(self, mock_find, mock_user):
        """Testa autenticação bem-sucedida de conta ativa."""
        mock_find.return_value = {
            "id_conta": 15,
            "email": "aluno.ativo@escola.com",
            "senha_hash": generate_password_hash("minhasenha123"),
            "ativo": True,
            "status_conta": "ativo",
            "id_aluno": 3,
            "id_professor": None,
            "id_funcionario": None,
            "id_responsavel": None
        }
        mock_user.return_value = User(
            id_conta=15,
            email="aluno.ativo@escola.com",
            perfil="aluno",
            id_perfil=3,
            nome="Aluno Ativo"
        )

        user, err = AuthService.authenticate("aluno.ativo@escola.com", "minhasenha123")
        self.assertIsNotNone(user)
        self.assertIsNone(err)
        self.assertEqual(user.nome, "Aluno Ativo")

    def test_routes_status_and_health(self):
        """Verifica se as rotas da Fase 2 e o endpoint /health estão respondendo."""
        res_health = self.client.get("/health")
        self.assertEqual(res_health.status_code, 200)

        res_login = self.client.get("/auth/login")
        self.assertEqual(res_login.status_code, 200)
        self.assertIn("Acesso ao Sistema".encode("utf-8"), res_login.data)

        res_hub = self.client.get("/auth/cadastro")
        self.assertEqual(res_hub.status_code, 200)
        self.assertIn("Selecione seu Perfil".encode("utf-8"), res_hub.data)

        res_cad_aluno = self.client.get("/auth/cadastro/aluno")
        self.assertEqual(res_cad_aluno.status_code, 200)

        res_cad_prof = self.client.get("/auth/cadastro/professor")
        self.assertEqual(res_cad_prof.status_code, 200)

        res_cad_resp = self.client.get("/auth/cadastro/responsavel")
        self.assertEqual(res_cad_resp.status_code, 200)

if __name__ == "__main__":
    unittest.main()
