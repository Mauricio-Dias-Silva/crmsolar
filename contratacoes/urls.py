# SysGov_Project/contratacoes/urls.py

from django.urls import path
from . import views

app_name = 'contratacoes'

urlpatterns = [
    # Dashboard ou página inicial do módulo de contratações
    path('', views.contratacoes_dashboard, name='dashboard_contratacoes'), # <<< AJUSTADO: Usando a view de dashboard

    # URLs para ETPs
    path('etps/', views.listar_etps, name='listar_etps'),
    path('etps/criar/', views.criar_etp, name='criar_etp'),
    path('etps/criar/<int:processo_id>/', views.criar_etp, name='criar_etp_para_processo'),
    path('etps/<int:pk>/', views.detalhar_etp, name='detalhar_etp'),
    path('etps/<int:pk>/editar/', views.editar_etp, name='editar_etp'),
    path('etps/<int:pk>/status/', views.atualizar_status_etp, name='atualizar_status_etp'),
    path('etps/<int:etp_id>/anexos/adicionar/', views.adicionar_anexo_etp, name='adicionar_anexo_etp'), # Nova URL para adicionar anexo ao ETP
    path('etps/<int:pk>/pdf/', views.gerar_etp_pdf, name='gerar_etp_pdf'), 
    path('etps/<int:etp_id>/anexos/adicionar/', views.adicionar_anexo_etp, name='adicionar_anexo_etp'),
    path('etps/<int:pk>/gerar-tr/', views.gerar_tr_a_partir_etp, name='gerar_tr_a_partir_etp'),
    path('etp/assistente-ia/', views.gerar_etp_ia_view, name='gerar_etp_ia'),
    path('etp/<int:pk>/processar-acao/', views.processar_acao_etp, name='processar_acao_etp'),
    
    # URLs para TRs
    path('trs/', views.listar_trs, name='listar_trs'),
    path('trs/criar/', views.criar_tr, name='criar_tr'),
    path('trs/criar/<int:etp_id>/', views.criar_tr, name='criar_tr_a_partir_etp'), # Cria TR a partir de um ETP
    path('trs/criar/processo/<int:processo_id>/', views.criar_tr, name='criar_tr_para_processo'), # Cria TR a partir de um Processo
    path('trs/<int:pk>/', views.detalhar_tr, name='detalhar_tr'),
    path('trs/<int:pk>/editar/', views.editar_tr, name='editar_tr'),
    path('trs/<int:pk>/status/', views.atualizar_status_tr, name='atualizar_status_tr'),
    path('trs/<int:pk>/pdf/', views.gerar_tr_pdf, name='gerar_tr_pdf'), 
    
    

    # URLs para PCAs (Plano de Contratações Anual)
    path('pcas/', views.listar_pca, name='listar_pca'),
    path('pcas/criar/', views.criar_pca, name='criar_pca'),
    path('pcas/<int:pk>/', views.detalhar_pca, name='detalhar_pca'),
    path('pcas/<int:pk>/editar/', views.editar_pca, name='editar_pca'),
    path('pcas/<int:pca_pk>/adicionar-item/', views.adicionar_item_pca, name='adicionar_item_pca'), # <<< NOVA URL AQUI

    # URLs para Itens de Catálogo
    path('catalogo/', views.listar_catalogo_itens, name='listar_catalogo_itens'),
    path('catalogo/novo/', views.criar_item_catalogo, name='criar_item_catalogo'), # Exemplo de URL de criação
    path('catalogo/item/<int:pk>/editar/', views.editar_item_catalogo, name='editar_item_catalogo'),
    # URLs para Modelos de Texto
    path('modelos-texto/', views.listar_modelos_texto, name='listar_modelos_texto'),

    # URLs para Requisitos Padrão
    path('requisitos-padrao/', views.listar_requisitos_padrao, name='listar_requisitos_padrao'),

    # <<< NOVAS URLS: Modelos de Texto e Requisitos Padrão >>>
    path('modelos-texto/', views.listar_modelos_texto, name='listar_modelos_texto'),
    path('requisitos-padrao/', views.listar_requisitos_padrao, name='listar_requisitos_padrao'),

    path('processo/<int:processo_id>/contrato/criar/', views.criar_contrato, name='criar_contrato'),
    path('contratos/', views.listar_contratos, name='listar_contratos'),
    path('contrato/<int:pk>/', views.detalhar_contrato, name='detalhar_contrato'),
    path('contrato/<int:pk>/editar/', views.editar_contrato, name='editar_contrato'),
    path('contrato/<int:pk>/pdf/', views.gerar_contrato_pdf, name='gerar_contrato_pdf'),
    
    path('atas-rp/', views.listar_atas_rp, name='listar_atas_rp'),
    path('atas-rp/<int:pk>/', views.detalhar_ata_rp, name='detalhar_ata_rp'),
    path('processo/<int:processo_id>/ata-rp/criar/', views.criar_ata_rp, name='criar_ata_rp'),
    path('atas-rp/<int:pk>/editar/', views.editar_ata_rp, name='editar_ata_rp'),
]