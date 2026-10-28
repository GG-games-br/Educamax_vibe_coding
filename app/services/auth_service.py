import re
from werkzeug.security import generate_password_hash, check_password_hash
from app.repositories.user_repository import UserRepository
from app.models.user import User

class AuthService:
    """
    Camada de serviço para autenticação, validação e registro de contas.
    Implementa as regras de negócio de 02-autenticacao-contas.md.
    """

    @staticmethod
    def _clean_cpf(cpf):
        """Remove caracteres não numéricos do CPF."""
        return re.sub(r"\D", "", cpf or "")

    @staticmethod
    def _validate_common_fields(nome, email, cpf, senha, confirmacao_senha):
        """Validações comuns de dados de entrada."""
        errors = []
        if not nome or len(nome.strip()) < 3:
            errors.append("O nome deve ter no mínimo 3 caracteres.")
        
        if not email or "@" not in email or "." not in email:
            errors.append("Informe um endereço de e-mail válido.")
            
        clean_cpf = AuthService._clean_cpf(cpf)
        if len(clean_cpf) != 11:
            errors.append("O CPF deve conter exatamente 11 dígitos numéricos.")

        if not senha or len(senha) < 6:
            errors.append("A senha deve ter no mínimo 6 caracteres.")

        if senha != confirmacao_senha:
            errors.append("A confirmação de senha não confere com a senha informada.")

        return errors, clean_cpf

    @classmethod
    def register_aluno(cls, form_data):
        """
        Registra Aluno com ativação imediata.
        Valida duplicidade de CPF, Email e Matrícula.
        """
        errors, clean_cpf = cls._validate_common_fields(
            form_data.get("nome"),
            form_data.get("email"),
            form_data.get("cpf"),
            form_data.get("senha"),
            form_data.get("confirmacao_senha")
        )

        matricula_raw = form_data.get("matricula", "").strip()
        if not matricula_raw.isdigit():
            errors.append("A matrícula do aluno deve ser um número válido.")
        else:
            matricula = int(matricula_raw)

        if errors:
            return False, errors

        email = form_data.get("email").strip().lower()

        # Validação preventiva de duplicidades
        if UserRepository.check_duplicate_email(email):
            return False, ["Este endereço de e-mail já está cadastrado no sistema."]

        if UserRepository.check_duplicate_cpf(clean_cpf, "aluno"):
            return False, ["Este CPF já está cadastrado para outro aluno."]

        if UserRepository.check_duplicate_matricula(matricula, "aluno"):
            return False, ["Esta matrícula já está em uso por outro aluno."]

        senha_hash = generate_password_hash(form_data.get("senha"))
        aluno_data = {
            "nome": form_data.get("nome").strip(),
            "cpf": clean_cpf,
            "numero": form_data.get("numero", "").strip(),
            "matricula": matricula,
            "email": email
        }

        try:
            UserRepository.create_aluno_with_conta(aluno_data, senha_hash)
            return True, "Conta de Aluno criada com sucesso! Faça login para acessar."
        except Exception as e:
            return False, [f"Erro ao registrar aluno: {str(e)}"]

    @classmethod
    def register_responsavel(cls, form_data):
        """
        Registra Responsável com ativação imediata.
        Valida duplicidade de CPF e Email.
        """
        errors, clean_cpf = cls._validate_common_fields(
            form_data.get("nome"),
            form_data.get("email"),
            form_data.get("cpf"),
            form_data.get("senha"),
            form_data.get("confirmacao_senha")
        )

        if errors:
            return False, errors

        email = form_data.get("email").strip().lower()

        if UserRepository.check_duplicate_email(email):
            return False, ["Este endereço de e-mail já está cadastrado no sistema."]

        if UserRepository.check_duplicate_cpf(clean_cpf, "responsavel"):
            return False, ["Este CPF já está cadastrado para outro responsável."]

        senha_hash = generate_password_hash(form_data.get("senha"))
        resp_data = {
            "nome": form_data.get("nome").strip(),
            "cpf": clean_cpf,
            "numero": form_data.get("numero", "").strip(),
            "email": email
        }

        try:
            UserRepository.create_responsavel_with_conta(resp_data, senha_hash)
            return True, "Conta de Responsável criada com sucesso! Faça login para acessar."
        except Exception as e:
            return False, [f"Erro ao registrar responsável: {str(e)}"]

    @classmethod
    def register_professor(cls, form_data):
        """
        Registra Professor com status pendente de aprovação administrativa.
        """
        errors, clean_cpf = cls._validate_common_fields(
            form_data.get("nome"),
            form_data.get("email"),
            form_data.get("cpf"),
            form_data.get("senha"),
            form_data.get("confirmacao_senha")
        )

        matricula_raw = form_data.get("matricula", "").strip()
        if not matricula_raw.isdigit():
            errors.append("A matrícula funcional do professor deve ser numérica.")
        else:
            matricula = int(matricula_raw)

        if errors:
            return False, errors

        email = form_data.get("email").strip().lower()

        if UserRepository.check_duplicate_email(email):
            return False, ["Este endereço de e-mail já está cadastrado no sistema."]

        if UserRepository.check_duplicate_cpf(clean_cpf, "professor"):
            return False, ["Este CPF já está cadastrado para outro professor."]

        if UserRepository.check_duplicate_matricula(matricula, "professor"):
            return False, ["Esta matrícula já está em uso por outro professor."]

        senha_hash = generate_password_hash(form_data.get("senha"))
        prof_data = {
            "nome": form_data.get("nome").strip(),
            "cpf": clean_cpf,
            "numero": form_data.get("numero", "").strip(),
            "matricula": matricula,
            "email": email
        }

        try:
            UserRepository.create_professor_with_conta(prof_data, senha_hash)
            return True, "Solicitação de cadastro de Professor enviada com sucesso! Aguarde a aprovação do setor Administrativo para logar."
        except Exception as e:
            return False, [f"Erro ao registrar professor: {str(e)}"]

    @classmethod
    def register_funcionario(cls, form_data):
        """
        Registra Funcionário / Administrativo com status pendente de aprovação.
        """
        errors, clean_cpf = cls._validate_common_fields(
            form_data.get("nome"),
            form_data.get("email"),
            form_data.get("cpf"),
            form_data.get("senha"),
            form_data.get("confirmacao_senha")
        )

        id_cargo_raw = form_data.get("id_cargo", "").strip()
        if not id_cargo_raw.isdigit():
            errors.append("Selecione um cargo válido.")
        else:
            id_cargo = int(id_cargo_raw)

        if errors:
            return False, errors

        email = form_data.get("email").strip().lower()

        if UserRepository.check_duplicate_email(email):
            return False, ["Este endereço de e-mail já está cadastrado no sistema."]

        if UserRepository.check_duplicate_cpf(clean_cpf, "funcionario"):
            return False, ["Este CPF já está cadastrado para outro funcionário."]

        senha_hash = generate_password_hash(form_data.get("senha"))
        func_data = {
            "nome": form_data.get("nome").strip(),
            "cpf": clean_cpf,
            "numero": form_data.get("numero", "").strip(),
            "email": email,
            "id_cargo": id_cargo
        }

        try:
            UserRepository.create_funcionario_with_conta(func_data, senha_hash)
            return True, "Solicitação de cadastro enviada com sucesso! Aguarde a aprovação do setor Administrativo para logar."
        except Exception as e:
            return False, [f"Erro ao registrar funcionário: {str(e)}"]

    @classmethod
    def authenticate(cls, identificador, senha):
        """
        Autentica o usuário por (EMAIL OU NOME) + SENHA.
        Verifica integridade da senha e se a conta está ativa ou pendente.
        Retorna (user_object, None) em caso de sucesso ou (None, mensagem_erro).
        """
        if not identificador or not senha:
            return None, "Informe seu e-mail (ou nome completo) e sua senha."

        identificador_clean = identificador.strip().lower()

        # =========================================================================
        # IF STATEMENT: Permite login direto sem a necessidade de conectar ao banco
        # de dados para cada tipo de usuário (Administrador, Professor, Responsável)
        # =========================================================================
        if identificador_clean == "administrador@gmail.com" and senha == "administrador123":
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
            ), None

        if identificador_clean == "professor@gmail.com" and senha == "professor123":
            return User(
                id_conta=2,
                email="professor@gmail.com",
                perfil="professor",
                id_perfil=2,
                nome="Professor EducaMax",
                ativo=True,
                status_conta="ativo",
                matricula=202601
            ), None

        if identificador_clean == "responsavel@gmail.com" and senha == "responsavel123":
            return User(
                id_conta=3,
                email="responsavel@gmail.com",
                perfil="responsavel",
                id_perfil=3,
                nome="Responsável EducaMax",
                ativo=True,
                status_conta="ativo"
            ), None

        # Autenticação via Banco de Dados (quando a conexão estiver disponível)
        try:
            conta_row = UserRepository.find_conta_for_auth(identificador)
        except Exception:
            return None, "Falha de conexão com o banco de dados. Utilize as credenciais de teste configuradas."

        if not conta_row:
            return None, "Credenciais inválidas. Verifique seu e-mail/nome e senha."

        # Validação do hash de senha
        if not check_password_hash(conta_row["senha_hash"], senha):
            return None, "Credenciais inválidas. Verifique seu e-mail/nome e senha."

        status_conta = conta_row.get("status_conta", "ativo" if conta_row["ativo"] else "pendente")
        ativo = bool(conta_row["ativo"])

        # Verificação do status de aprovação
        if status_conta == "pendente":
            return None, "Sua conta foi registrada com sucesso, mas ainda aguarda aprovação do setor Administrativo para ser ativada."

        if status_conta == "recusado" or not ativo:
            return None, "Sua solicitação de conta foi recusada ou desativada pela administração escolar."

        # Carrega o objeto User completo para a sessão
        user = UserRepository.find_user_by_id(conta_row["id_conta"])
        if not user:
            return None, "Erro ao carregar dados do usuário autenticado."

        return user, None

    @classmethod
    def approve_account(cls, id_conta):
        """Aprova a conta pendente."""
        try:
            UserRepository.update_status_conta(id_conta, "ativo")
            return True, "Conta aprovada com sucesso! O usuário já pode realizar login."
        except Exception as e:
            return False, f"Erro ao aprovar conta: {str(e)}"

    @classmethod
    def reject_account(cls, id_conta):
        """Recusa a conta pendente."""
        try:
            UserRepository.update_status_conta(id_conta, "recusado")
            return True, "Solicitação de conta recusada."
        except Exception as e:
            return False, f"Erro ao recusar conta: {str(e)}"

    @classmethod
    def get_pending_accounts(cls):
        """Lista todas as contas pendentes."""
        return UserRepository.get_pending_contas()
