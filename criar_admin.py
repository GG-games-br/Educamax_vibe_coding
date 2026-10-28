"""
Utilitário para criação do primeiro usuário Administrador no EducaMax.
Permite inicializar um usuário com acesso administrativo completo para
aprovação de contas pendentes e testes do sistema.
"""

import sys
import argparse
from werkzeug.security import generate_password_hash
from app.repositories.db import get_db_connection

def criar_administrador(nome, email, senha, cpf, matricula=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Garante a existência do cargo Administrador Geral
            cursor.execute("SELECT id_cargo FROM cargo WHERE nome = 'Administrador Geral' OR acesso_dados_sensiveis = TRUE LIMIT 1")
            cargo = cursor.fetchone()
            if not cargo:
                cursor.execute(
                    "INSERT INTO cargo (nome, acesso_dados_sensiveis) VALUES (%s, %s)",
                    ("Administrador Geral", True)
                )
                id_cargo = cursor.lastrowid
            else:
                id_cargo = cargo["id_cargo"]

            # 2. Verifica se o email já existe
            cursor.execute("SELECT id_conta FROM conta WHERE email = %s", (email,))
            if cursor.fetchone():
                print(f"[-] Erro: Já existe uma conta cadastrada com o e-mail '{email}'.")
                return False

            # 3. Insere o funcionário
            cursor.execute("SELECT id_funcionario FROM funcionario WHERE cpf = %s", (cpf,))
            func = cursor.fetchone()
            if not func:
                cursor.execute(
                    """
                    INSERT INTO funcionario (cpf, numero, nome, email, id_cargo)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (cpf, "98999999999", nome, email, id_cargo)
                )
                id_funcionario = cursor.lastrowid
            else:
                id_funcionario = func["id_funcionario"]

            # 4. Cria a conta ativa
            senha_hash = generate_password_hash(senha)
            cursor.execute(
                """
                INSERT INTO conta (email, senha_hash, ativo, status_conta, id_funcionario)
                VALUES (%s, %s, TRUE, 'ativo', %s)
                """,
                (email, senha_hash, id_funcionario)
            )
            id_conta = cursor.lastrowid

        conn.commit()
        print(f"[+] Administrador criado com sucesso!")
        print(f"    Nome: {nome}")
        print(f"    E-mail: {email}")
        print(f"    ID Conta: #{id_conta}")
        print(f"    Status: ATIVO (Acesso Completo)")
        return True
    except Exception as e:
        conn.rollback()
        print(f"[-] Erro ao criar administrador: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Criar conta de Administrador no EducaMax")
    parser.add_argument("--nome", default="Administrador EducaMax", help="Nome completo")
    parser.add_argument("--email", default="admin@educamax.com", help="E-mail de acesso")
    parser.add_argument("--senha", default="admin123", help="Senha de acesso")
    parser.add_argument("--cpf", default="00000000001", help="CPF com 11 dígitos")

    args = parser.parse_args()
    criar_administrador(args.nome, args.email, args.senha, args.cpf)
