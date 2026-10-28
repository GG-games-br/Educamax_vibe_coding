from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = "auth.login"
login_manager.login_message = "Por favor, efetue login para acessar esta página."
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    """Callback do Flask-Login para carregar o usuário a partir do id_conta."""
    from app.repositories.user_repository import UserRepository
    try:
        return UserRepository.find_user_by_id(int(user_id))
    except Exception:
        return None
