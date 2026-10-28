import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env caso exista
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=env_path)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "educamax_chave_padrao_dev_segredo_2026")
    
    # Credenciais do Banco de Dados MySQL
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", 3306))
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "28052007Be*")
    DB_NAME = os.environ.get("DB_NAME", "escola_db")
    
    # Configurações de Sessão e CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get("WTF_CSRF_SECRET_KEY", SECRET_KEY)
