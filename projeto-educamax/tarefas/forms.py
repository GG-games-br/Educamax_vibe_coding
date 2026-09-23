from django import forms
from .models import Tarefa

class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['titulo', 'descricao', 'data_entrega']
        widgets = {
            'data_entrega': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }