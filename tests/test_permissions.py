import unittest
from unittest.mock import patch
from flask_login import login_user
from app import create_app
from app.models.user import User
from config import Config

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-permissions-key"

class TestPermissionsRBAC(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

    def test_admin_routes_block_unauthenticated(self):
        """Usuário não logado é redirecionado ao tentar acessar rotas admin."""
        res = self.client.get("/admin/academico")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/auth/login", res.headers["Location"])

    def test_admin_routes_block_aluno(self):
        """Aluno tentando acessar rota administrativa recebe 403."""
        aluno = User(
            id_conta=1,
            email="aluno@teste.com",
            perfil="aluno",
            id_perfil=1,
            nome="Aluno",
            matricula=1001
        )
        with self.client.session_transaction() as sess:
            sess["_user_id"] = "1"

        with patch("app.repositories.user_repository.UserRepository.find_user_by_id", return_value=aluno):
            res = self.client.get("/admin/academico")
            self.assertEqual(res.status_code, 403)

    def test_admin_routes_block_professor(self):
        """Professor tentando acessar rota administrativa recebe 403."""
        professor = User(
            id_conta=2,
            email="prof@teste.com",
            perfil="professor",
            id_perfil=2,
            nome="Professor",
            matricula=2001
        )
        with self.client.session_transaction() as sess:
            sess["_user_id"] = "2"

        with patch("app.repositories.user_repository.UserRepository.find_user_by_id", return_value=professor):
            res = self.client.get("/admin/turmas")
            self.assertEqual(res.status_code, 403)

    def test_admin_routes_allowed_for_admin(self):
        """Administrador tem acesso liberado às rotas acadêmicas."""
        admin = User(
            id_conta=3,
            email="admin@teste.com",
            perfil="funcionario",
            id_perfil=3,
            nome="Administrador",
            cargo_nome="Administrador Geral",
            acesso_dados_sensiveis=True
        )
        with self.client.session_transaction() as sess:
            sess["_user_id"] = "3"

        with patch("app.repositories.user_repository.UserRepository.find_user_by_id", return_value=admin), \
             patch("app.repositories.academic_repository.AcademicRepository.list_turmas", return_value=[]), \
             patch("app.repositories.academic_repository.AcademicRepository.list_materias", return_value=[]), \
             patch("app.repositories.academic_repository.AcademicRepository.list_prestadores", return_value=[]), \
             patch("app.repositories.academic_repository.AcademicRepository.list_alunos", return_value=[]), \
             patch("app.repositories.academic_repository.AcademicRepository.list_professores", return_value=[]), \
             patch("app.repositories.academic_repository.AcademicRepository.list_responsaveis", return_value=[]):
            res = self.client.get("/admin/academico")
            self.assertEqual(res.status_code, 200)
            self.assertIn("Gestão Acadêmica".encode("utf-8"), res.data)

    def test_professor_isolated_turma_access(self):
        """Professor só pode ver turmas que leciona. Acesso a outra turma resulta em 403."""
        professor = User(
            id_conta=5,
            email="prof.mat@teste.com",
            perfil="professor",
            id_perfil=10,
            nome="Prof Matemática",
            matricula=5001
        )
        with self.client.session_transaction() as sess:
            sess["_user_id"] = "5"

        with patch("app.repositories.user_repository.UserRepository.find_user_by_id", return_value=professor):
            # 1. Turma que ele leciona -> 200 OK
            with patch("app.services.academic_service.AcademicService.check_professor_has_turma", return_value=True), \
                 patch("app.services.academic_service.AcademicService.get_alunos_turma", return_value=[]):
                res_ok = self.client.get("/professor/turma/1a")
                self.assertEqual(res_ok.status_code, 200)

            # 2. Turma que ele NÃO leciona -> 403 Proibido
            with patch("app.services.academic_service.AcademicService.check_professor_has_turma", return_value=False):
                res_forbidden = self.client.get("/professor/turma/2b")
                self.assertEqual(res_forbidden.status_code, 403)

    def test_responsavel_isolated_aluno_access(self):
        """Responsável só visualiza alunos vinculados a ele. Acesso a aluno não vinculado resulta em 403."""
        responsavel = User(
            id_conta=7,
            email="pai@teste.com",
            perfil="responsavel",
            id_perfil=20,
            nome="Pai Responsavel"
        )
        with self.client.session_transaction() as sess:
            sess["_user_id"] = "7"

        with patch("app.repositories.user_repository.UserRepository.find_user_by_id", return_value=responsavel):
            # 1. Aluno vinculado a ele -> 200 OK
            with patch("app.services.academic_service.AcademicService.check_responsavel_has_aluno", return_value=True), \
                 patch("app.services.academic_service.AcademicService.get_aluno_info", return_value={"nome": "Filho", "matricula": 101}):
                res_ok = self.client.get("/responsavel/aluno/101")
                self.assertEqual(res_ok.status_code, 200)

            # 2. Aluno não vinculado a ele -> 403 Proibido
            with patch("app.services.academic_service.AcademicService.check_responsavel_has_aluno", return_value=False):
                res_forbidden = self.client.get("/responsavel/aluno/999")
                self.assertEqual(res_forbidden.status_code, 403)

if __name__ == "__main__":
    unittest.main()
