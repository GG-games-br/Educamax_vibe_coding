from django.urls import path
from . import views
urlpatterns = [
path('aluno/', views.dashboard_aluno, name='dashboard_aluno'),
path('professor/', views.dashboard_professor, name='dashboard_professor'),
path('empresa/', views.dashboard_empresa, name='dashboard_empresa'),
    
]
