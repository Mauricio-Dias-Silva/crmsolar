# vendedores_painel/urls.py

from django.urls import path
from . import views

app_name = 'vendedores_painel'

urlpatterns = [
    path('', views.dashboard_vendedor, name='dashboard'),
    path('ofertas/nova/', views.criar_oferta, name='criar_oferta'),
    path('ofertas/<int:pk>/editar/', views.editar_oferta, name='editar_oferta'),
    
    # CORRIGIDO AQUI: A URL deve apontar para a view 'gerenciar_cupons'
    path('cupons/', views.gerenciar_cupons, name='gerenciar_cupons'), # <--- CORRIGIDO
    
    # Garanta que a URL de resgate de cupom também aponte para a view correta e receba o ID
    path('cupons/resgatar/<int:cupom_id>/', views.resgatar_cupom, name='resgatar_cupom'), # <--- Verificar se está cupom_id
    path('cupons/buscar/', views.buscar_cupom_para_resgate, name='buscar_cupom'), 
]