from django.db import models
from django.conf import settings
from django.db import models

class Tarefa(models.Model):
    titulo = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    data_entrega = models.DateField(null=True, blank=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tarefas_criadas',
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return self.titulo