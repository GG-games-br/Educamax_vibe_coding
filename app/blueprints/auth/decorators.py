from functools import wraps
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user
from app.services.academic_service import AcademicService

def perfil_required(*perfis):
    """
    Decorator para proteger rotas por perfil no backend.
    Uso: @perfil_required('aluno', 'responsavel')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login", next=request.path))
            
            # Administrador sempre tem permissão se 'admin' estiver listado ou como fallback
            if "admin" in perfis and current_user.is_admin:
                return f(*args, **kwargs)

            if current_user.perfil not in perfis:
                flash("Acesso não autorizado para o seu perfil de usuário.", "danger")
                abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator exclusivo para rotas do setor Administrativo."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", next=request.path))
        if not current_user.is_admin:
            flash("Esta funcionalidade é restrita ao setor Administrativo.", "danger")
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def professor_turma_required(f):
    """
    Garante no backend que o professor logado só acesse turmas que ele leciona.
    O perfil Administrativo possui acesso global permitido.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", next=request.path))

        # Administrativo pode visualizar qualquer turma
        if current_user.is_admin:
            return f(*args, **kwargs)

        if current_user.perfil != "professor":
            flash("Apenas professores podem acessar este recurso.", "danger")
            abort(403)

        id_turma = kwargs.get("id_turma")
        if not id_turma or not AcademicService.check_professor_has_turma(current_user.id_perfil, id_turma):
            flash(f"Você não possui autorização para acessar a turma {id_turma.upper()} pois não leciona nela.", "danger")
            abort(403)

        return f(*args, **kwargs)
    return decorated_function

def responsavel_aluno_required(f):
    """
    Garante no backend que o responsável logado só visualize dados dos seus dependentes vinculados.
    O perfil Administrativo possui acesso global.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", next=request.path))

        # Administrativo pode visualizar qualquer aluno
        if current_user.is_admin:
            return f(*args, **kwargs)

        if current_user.perfil != "responsavel":
            flash("Apenas responsáveis podem acessar este recurso.", "danger")
            abort(403)

        matricula = kwargs.get("matricula")
        if not matricula or not AcademicService.check_responsavel_has_aluno(current_user.id_perfil, matricula):
            flash("Você não possui autorização para visualizar este aluno (não vinculado à sua conta).", "danger")
            abort(403)

        return f(*args, **kwargs)
    return decorated_function

def aluno_self_required(f):
    """
    Garante no backend que o aluno só acesse suas próprias informações.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", next=request.path))

        if current_user.is_admin:
            return f(*args, **kwargs)

        if current_user.perfil != "aluno":
            flash("Apenas alunos podem acessar este recurso.", "danger")
            abort(403)

        matricula = kwargs.get("matricula")
        if matricula and int(matricula) != current_user.matricula:
            flash("Você só pode visualizar suas próprias informações acadêmicas.", "danger")
            abort(403)

        return f(*args, **kwargs)
    return decorated_function
