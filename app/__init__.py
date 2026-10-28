from flask import Flask, render_template
from config import Config
from app.extensions import login_manager, csrf
from app.utils.logging import setup_logging
from app.blueprints.main import main_bp
from app.blueprints.auth import auth_bp
from app.blueprints.admin import admin_bp
from app.blueprints.professor import professor_bp
from app.blueprints.responsavel import responsavel_bp
from app.blueprints.aluno import aluno_bp
from app.blueprints.financeiro import financeiro_bp
from app.blueprints.requisicoes import requisicoes_bp
from app.blueprints.notas import notas_bp

def create_app(config_class=Config):
    """Application Factory para o EducaMax."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configuração de Logging Centralizado por Módulo
    setup_logging(app)

    # Inicialização de extensões
    login_manager.init_app(app)
    csrf.init_app(app)

    # Registro de Blueprints Modulares
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(professor_bp)
    app.register_blueprint(responsavel_bp)
    app.register_blueprint(aluno_bp)
    app.register_blueprint(financeiro_bp)
    app.register_blueprint(requisicoes_bp)
    app.register_blueprint(notas_bp)

    # Tratamento customizado de erros
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"), 500

    @app.context_processor
    def inject_global_vars():
        return {
            "app_name": "EducaMax",
            "simulado_aviso": "Ambiente de Demonstração — Dados Financeiros Fictícios"
        }

    return app
