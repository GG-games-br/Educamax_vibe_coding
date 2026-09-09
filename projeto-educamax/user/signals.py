from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, PerfilAluno, PerfilProfessor, PerfilFuncionario, PerfilEmpresa

PROFILE_MAP = {
    CustomUser.Roles.ALUNO: PerfilAluno,
    CustomUser.Roles.PROFESSOR: PerfilProfessor,
    CustomUser.Roles.FUNCIONARIO: PerfilFuncionario,
    CustomUser.Roles.EMPRESA: PerfilEmpresa,
}

@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        model = PROFILE_MAP.get(instance.cargo)
        if model:
            model.objects.get_or_create(user=instance)