# SysGov_Project/financeiro/urls.py

from django.urls import path
from . import views

app_name = 'financeiro' 

urlpatterns = [
    # <<< CORREÇÃO AQUI: O nome agora corresponde ao que o navbar está a chamar >>>
    path('', views.financeiro_dashboard, name='financeiro_dashboard'),

    # --- GESTÃO DE DOCUMENTOS FISCAIS ---
    path('documentos/', views.listar_documentos_fiscais, name='listar_documentos_fiscais'),
    path('contrato/<int:contrato_id>/docfiscal/criar/', views.criar_documento_fiscal, name='criar_documento_fiscal'),
    
    path('docfiscal/<int:pk>/', views.detalhar_documento_fiscal, name='detalhar_documento_fiscal'),
    path('docfiscal/<int:pk>/editar/', views.editar_documento_fiscal, name='editar_documento_fiscal'),
    path('documentos/<int:pk>/xml/', views.download_df_xml, name='download_df_xml'),
    
    # --- GESTÃO DE PAGAMENTOS ---
    path('pagamentos/', views.listar_pagamentos, name='listar_pagamentos'),
    path('docfiscal/<int:doc_fiscal_id>/pagamento/criar/', views.criar_pagamento, name='criar_pagamento'),
    path('pagamentos/<int:pk>/', views.detalhar_pagamento, name='detalhar_pagamento'),
    path('pagamentos/<int:pk>/editar/', views.editar_pagamento, name='editar_pagamento'),
    path('pagamentos/<int:pk>/xml/', views.download_pg_xml, name='download_pg_xml'),

    # --- GESTÃO DE NOTAS DE EMPENHO ---
    path('empenhos/', views.listar_empenhos, name='listar_empenhos'),
    path('contrato/<int:contrato_id>/empenho/criar/', views.criar_empenho, name='criar_empenho'),
    path('empenho/<int:pk>/', views.detalhar_empenho, name='detalhar_empenho'),
    path('empenho/<int:pk>/editar/', views.editar_empenho, name='editar_empenho'),
]