import pymysql
import pymysql.cursors
import socket
from flask import current_app
from config import Config
from app.utils.logging import get_module_logger

logger = get_module_logger("database")

def is_db_connected():
    """
    Verifica de forma ultrarrápida (timeout de 0.3s) se o serviço
    do MySQL está escutando no host e porta configurados.
    """
    host = current_app.config.get("DB_HOST", Config.DB_HOST) if current_app else Config.DB_HOST
    port = current_app.config.get("DB_PORT", Config.DB_PORT) if current_app else Config.DB_PORT
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def get_db_connection():
    """
    Retorna uma conexão aberta e resiliente com o banco de dados MySQL
    utilizando PyMySQL, cursor de dicionário e limites de timeout.
    """
    host = current_app.config.get("DB_HOST", Config.DB_HOST) if current_app else Config.DB_HOST
    port = current_app.config.get("DB_PORT", Config.DB_PORT) if current_app else Config.DB_PORT
    user = current_app.config.get("DB_USER", Config.DB_USER) if current_app else Config.DB_USER
    password = current_app.config.get("DB_PASSWORD", Config.DB_PASSWORD) if current_app else Config.DB_PASSWORD
    db_name = current_app.config.get("DB_NAME", Config.DB_NAME) if current_app else Config.DB_NAME

    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
            connect_timeout=3,
            read_timeout=10,
            write_timeout=10
        )
        return conn
    except Exception as e:
        logger.warning(f"MySQL indisponível ({host}:{port}/{db_name}): {str(e)} — Ativando Modo Demonstração Offline.")
        raise e
