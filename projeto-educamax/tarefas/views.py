from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from user.models import CustomUser
from .forms import TarefaForm
from .models import Tarefa


class ProfessorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.cargo in (
            CustomUser.Roles.PROFESSOR, CustomUser.Roles.ADMIN
        )


class TarefaListView(LoginRequiredMixin, ListView):      # READ
    model = Tarefa


class TarefaCreateView(ProfessorRequiredMixin, CreateView):   # CREATE
    model = Tarefa
    form_class = TarefaForm
    success_url = reverse_lazy('tarefas:lista')

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)


class TarefaUpdateView(ProfessorRequiredMixin, UpdateView):   # UPDATE
    model = Tarefa
    form_class = TarefaForm
    success_url = reverse_lazy('tarefas:lista')

    def get_queryset(self):
        return Tarefa.objects.filter(criado_por=self.request.user)


class TarefaDeleteView(ProfessorRequiredMixin, DeleteView):   # DELETE
    model = Tarefa
    success_url = reverse_lazy('tarefas:lista')

    def get_queryset(self):
        return Tarefa.objects.filter(criado_por=self.request.user)