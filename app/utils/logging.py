import logging
import os
import sys

def setup_logging(app=None):
    """Configura o sistema de logs centralizado e formatado."""
    log_level = logging.DEBUG if os.environ.get("FLASK_ENV") == "development" else logging.INFO
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)

    root_logger = logging.getLogger("educamax")
    if not root_logger.handlers:
        root_logger.addHandler(handler)
        root_logger.setLevel(log_level)

    if app:
        app.logger.handlers = root_logger.handlers
        app.logger.setLevel(log_level)

def get_module_logger(module_name):
    """Retorna um logger com namespace específico para o módulo."""
    return logging.getLogger(f"educamax.{module_name}")
