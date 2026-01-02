# SysGov_Project/integracao_audesp/urls.py

from django.urls import path
from . import views

app_name = 'integracao_audesp'

urlpatterns = [
    # --- Telas Principais do Módulo ---
    path('painel/', views.painel_audesp_view, name='painel_audesp'),
    path('submissoes/', views.listar_submissoes_audesp, name='listar_submissoes_audesp'),

    # --- PONTOS DE GERAÇÃO DE ARQUIVOS (APIs) ---
    # A URL para gerar o JSON do ETP
    path('etp/<int:etp_id>/json/', views.gerar_etp_audesp_json, name='gerar_etp_audesp_json'),

    # A URL para gerar o JSON do Edital
    path('edital/<int:edital_id>/json/', views.gerar_edital_audesp_json, name='gerar_edital_audesp_json'),
    # A URL para gerar o JSON de "Ajuste" a partir de um Contrato
    path('contrato/<int:contrato_id>/ajuste-json/', views.gerar_contrato_audesp_json, name='gerar_contrato_audesp_json'),
    # Adicione aqui as URLs para gerar os JSONs/XMLs de Documento Fiscal e Pagamento se necessário
]
