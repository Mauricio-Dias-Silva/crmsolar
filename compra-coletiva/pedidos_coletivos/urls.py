# pedidos_coletivos/urls.py

from django.urls import path
from . import views

app_name = 'pedidos_coletivos'

urlpatterns = [
    path('<slug:slug_oferta>/fazer-pedido/', views.fazer_pedido_coletivo, name='fazer_pedido_coletivo'),
    path('meus-pedidos/', views.meus_pedidos_coletivos, name='meus_pedidos'),
    path('meu-credito/', views.meu_credito, name='meu_credito'), # <--- NOVA URL
]