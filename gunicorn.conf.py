import os

# Configuração do Gunicorn para Ambientes de Produção (Railway, Render, Fly.io, etc.)
port = os.environ.get("PORT", "5000")
bind = f"0.0.0.0:{port}"

# Número de workers e threads para bom desempenho com I/O
workers = int(os.environ.get("WEB_CONCURRENCY", 2))
threads = int(os.environ.get("GUNICORN_THREADS", 4))
timeout = int(os.environ.get("GUNICORN_TIMEOUT", 120))

# Logs enviados para stdout/stderr para captura pela nuvem
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info")

