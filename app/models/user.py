from flask_login import UserMixin

class User(UserMixin):
    """
    Representação do usuário logado na sessão do Flask-Login.
    Mapeia os dados da tabela 'conta' e o perfil associado.
    """
    def __init__(
        self,
        id_conta,
        email,
        perfil,
        id_perfil,
        nome,
        ativo=True,
        status_conta="ativo",
        matricula=None,
        cargo_nome=None,
        acesso_dados_sensiveis=False
    ):
        self.id_conta = id_conta
        self.email = email
        self.perfil = perfil  # 'aluno', 'professor', 'funcionario', 'responsavel'
        self.id_perfil = id_perfil
        self.nome = nome
        self.ativo = bool(ativo)
        self.status_conta = status_conta
        self.matricula = matricula
        self.cargo_nome = cargo_nome
        self.acesso_dados_sensiveis = bool(acesso_dados_sensiveis)

    @property
    def id(self):
        """Identificador único exigido pelo Flask-Login."""
        return str(self.id_conta)

    @property
    def is_active(self):
        """Conta ativa somente se 'ativo' for True e status_conta for 'ativo'."""
        return self.ativo and self.status_conta == "ativo"

    @property
    def is_admin(self):
        """
        Perfil Administrativo: funcionário com acesso a dados sensíveis
        ou cargo administrativo.
        """
        if self.perfil != "funcionario":
            return False
        if self.acesso_dados_sensiveis:
            return True
        if self.cargo_nome and any(term in self.cargo_nome.lower() for term in ["admin", "diretor", "coordenad", "secretár"]):
            return True
        return False

    def __repr__(self):
        return f"<User id_conta={self.id_conta} email={self.email} perfil={self.perfil} status={self.status_conta}>"
