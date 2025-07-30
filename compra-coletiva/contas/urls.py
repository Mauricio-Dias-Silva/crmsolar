# contas/urls.py

from django.urls import path
from . import views

app_name = 'contas' 

urlpatterns = [
    path('seja-vendedor/', views.cadastro_vendedor, name='cadastro_vendedor'),
    path('minhas-notificacoes/', views.minhas_notificacoes, name='minhas_notificacoes'), # <--- NOVA URL
]