import os
from urllib.parse import urlparse
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env caso exista localmente
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=env_path)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "educamax_chave_padrao_dev_segredo_2026")
    FLASK_ENV = os.environ.get("FLASK_ENV", "production")
    
    # -------------------------------------------------------------
    # Detecção Inteligente de Banco de Dados (Local ou Nuvem)
    # Suporta:
    # 1. URL unificada: MYSQL_URL ou DATABASE_URL (Railway, Render, AWS)
    # 2. Variáveis individuais do Railway: MYSQLHOST, MYSQLPORT, etc.
    # 3. Variáveis padrão do projeto: DB_HOST, DB_PORT, etc.
    # -------------------------------------------------------------
    db_url = os.environ.get("MYSQL_URL") or os.environ.get("DATABASE_URL")
    
    if db_url and ("mysql" in db_url or "mariadb" in db_url):
        parsed = urlparse(db_url)
        DB_HOST = parsed.hostname or "localhost"
        DB_PORT = int(parsed.port or 3306)
        DB_USER = parsed.username or "root"
        DB_PASSWORD = parsed.password or ""
        DB_NAME = parsed.path.lstrip("/") or "escola_db"
    else:
        DB_HOST = (
            os.environ.get("DB_HOST")
            or os.environ.get("MYSQLHOST")
            or os.environ.get("MYSQL_HOST")
            or "localhost"
        )
        DB_PORT = int(
            os.environ.get("DB_PORT")
            or os.environ.get("MYSQLPORT")
            or os.environ.get("MYSQL_PORT")
            or 3306
        )
        DB_USER = (
            os.environ.get("DB_USER")
            or os.environ.get("MYSQLUSER")
            or os.environ.get("MYSQL_USER")
            or "root"
        )
        DB_PASSWORD = (
            os.environ.get("DB_PASSWORD")
            or os.environ.get("MYSQLPASSWORD")
            or os.environ.get("MYSQL_PASSWORD")
            or ""
        )
        DB_NAME = (
            os.environ.get("DB_NAME")
            or os.environ.get("MYSQLDATABASE")
            or os.environ.get("MYSQL_DATABASE")
            or "escola_db"
        )

    # Porta do servidor web (usada pelo Railway/Render via variável $PORT)
    PORT = int(os.environ.get("PORT", 5000))

    # Controle do Modo Demonstração Offline (Fallback em memória)
    # Por padrão, ativo para facilitar testes. Pode ser desativado com ALLOW_OFFLINE_FALLBACK=false
    ALLOW_OFFLINE_FALLBACK = os.environ.get("ALLOW_OFFLINE_FALLBACK", "true").lower() in ("true", "1", "yes")

    # Configurações de Sessão e Proteção CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get("WTF_CSRF_SECRET_KEY", SECRET_KEY)
