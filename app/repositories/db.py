import pymysql
import pymysql.cursors
from flask import current_app
from config import Config
from app.utils.logging import get_module_logger

logger = get_module_logger("database")

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
            connect_timeout=5,
            read_timeout=15,
            write_timeout=15
        )
        return conn
    except Exception as e:
        logger.error(f"Falha de conexão com MySQL ({host}:{port}/{db_name}): {str(e)}")
        raise e
