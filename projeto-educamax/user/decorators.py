from django.contrib.auth.decorators import user_passes_test

def role_required(*roles):
    """
    Usage: @role_required('ALUNO')
           @role_required('PROFESSOR', 'FUNCIONARIO')
    Redirects unauthenticated or wrong-role users to LOGIN_URL.
    """
    return user_passes_test(lambda u: u.is_authenticated and u.cargo in roles)