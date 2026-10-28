from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.repositories.db import get_db_connection

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    """Redireciona para o dashboard se logado, ou para login."""
    if current_user.is_authenticated:
        return render_template("dashboard.html")
    return render_template("index.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Painel principal do usuário logado, adaptado ao perfil."""
    return render_template("dashboard.html")

@main_bp.route("/health")
def health():
    """Health-check para monitoramento da aplicação e banco de dados."""
    db_status = "ok"
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
        conn.close()
    except Exception as e:
        db_status = f"error: {str(e)}"

    return jsonify({
        "status": "online" if db_status == "ok" else "degraded",
        "app": "EducaMax",
        "database": db_status
    })
