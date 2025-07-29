# vendedores_painel/urls.py
from django.urls import path
from . import views

app_name = 'vendedores_painel'

urlpatterns = [
    path('', views.dashboard_vendedor, name='dashboard'), # Esta é a rota principal do painel do vendedor
    path('ofertas/nova/', views.criar_oferta, name='criar_oferta'),
    path('ofertas/<int:pk>/editar/', views.editar_oferta, name='editar_oferta'),
    path('cupons/', views.listar_cupons_vendedor, name='listar_cupons'),
    path('cupons/resgatar/<str:codigo_cupom>/', views.resgatar_cupom, name='resgatar_cupom'),
    path('cupons/buscar/', views.buscar_cupom_para_resgate, name='buscar_cupom'),
]