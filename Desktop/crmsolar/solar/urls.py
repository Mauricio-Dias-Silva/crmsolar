# solar/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views # Importado, mas não usado diretamente aqui
from . import views
from django.shortcuts import redirect

app_name = 'crm'

urlpatterns = [
    # Rotas do CRM
    path('', views.home, name='home'),

    # Clientes (CRM)
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/cadastrar/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('clientes/<int:pk>/', views.detalhe_cliente, name='detalhe_cliente'),
    path('clientes/<int:pk>/editar/', views.editar_cliente, name='editar_cliente'),
    path('clientes/<int:pk>/excluir/', views.excluir_cliente, name='excluir_cliente'),

    
    # URL principal para a Dashboard do Cliente (E-commerce)
    # A view 'cliente_dashboard' é a que agora lida com a lógica de perfil.
    path('cliente/dashboard/', views.cliente_dashboard, name='cliente_dashboard'), # URL principal para o dashboard do cliente
    path('cliente/completar-perfil/', views.completar_perfil_cliente, name='completar_perfil_cliente'),
    path('cliente/painel/<int:pk>/', views.cliente_painel_detalhe, name='cliente_painel_detalhe'),

    # Usuários (CRM)
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/novo/', views.cadastrar_usuario, name='cadastrar_usuario'),
    path('usuarios/<int:usuario_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:usuario_id>/resetar_senha/', views.resetar_senha_usuario, name='resetar_senha_usuario'),
    path('usuarios/<int:usuario_id>/excluir/', views.excluir_usuario, name='excluir_usuario'),

    # Projetos (CRM)
    path('projetos/', views.lista_projetos, name='lista_projetos'),
    path('projetos/cadastrar/', views.cadastrar_projeto, name='cadastrar_projeto'),
    path('projetos/<int:pk>/', views.detalhe_projeto, name='detalhe_projeto'),
    path('projetos/<int:pk>/cadastrar_etapa/', views.cadastrar_etapa, name='cadastrar_etapa'),
    path('projetos/dashboard/', views.dashboard_projetos, name='dashboard_projetos'),
    path('projetos/<int:pk>/editar/', views.editar_projeto, name='editar_projeto'),
    path('projetos/<int:pk>/excluir/', views.excluir_projeto, name='excluir_projeto'),
    path('projetos/<int:projeto_id>/upload_documento/', views.upload_documento_projeto, name='upload_documento_projeto'),
    path('projetos/<int:projeto_id>/excluir_documento/<int:doc_id>/', views.excluir_documento_projeto, name='excluir_documento_projeto'),
    path('projeto/<int:pk>/recalcular-irradiacao/', views.recalcular_irradiacao, name='recalcular_irradiacao'),
    path('projetos/<int:pk>/proposta-pdf/', views.gerar_proposta_pdf, name='gerar_proposta_pdf'), 
    path('projetos/novo/', views.projeto_create_update, name='cadastrar_projeto'),
    path('projetos/<int:pk>/editar/', views.projeto_create_update, name='editar_projeto'),
    

    # Materiais (CRM)
    path('materiais/', views.lista_materiais, name='lista_materiais'),
    path('materiais/cadastrar/', views.cadastrar_material, name='cadastrar_material'),
    path('materiais/<int:pk>/editar/', views.editar_material, name='editar_material'),

    # Fornecedores (CRM)
    path('fornecedores/', views.lista_fornecedores, name='lista_fornecedores'),
    path('fornecedores/cadastrar/', views.cadastrar_fornecedor, name='cadastrar_fornecedor'),
    path('fornecedores/<int:pk>/editar/', views.editar_fornecedor, name='editar_fornecedor'),

    # Financeiro (CRM)
    path('financeiro/', views.lista_financeiro, name='lista_financeiro'),
    path('financeiro/cadastrar/', views.cadastrar_lancamento, name='cadastrar_lancamento'),
    path('financeiro/dashboard/', views.dashboard_financeiro, name='dashboard_financeiro'),

    # Área do Cliente (Login/Logout e Painel de Progresso - E-commerce)
    # Redirecionamento para o login_cliente via progresso/ (melhor que a lambda, para consistência)
    path('progresso/', lambda request: redirect('crm:login_cliente')), # Redireciona para o login do cliente
    path('progresso/login/', views.login_cliente, name='login_cliente'),
    path('progresso/logout/', views.logout_view, name='logout_cliente'),
    

    # Gerenciamento de Produtos do E-commerce (para CRM)
    path('produtos-ecommerce/', views.lista_produtos_ecommerce, name='lista_produtos_ecommerce'),

    # Rota de ADIÇÃO MANUAL. Nome corrigido para corresponder ao template.
    path('produtos-ecommerce/adicionar/', views.adicionar_produto, name='adicionar_produto_ecommerce'), # NOME CORRIGIDO AQUI
    path('produtos-ecommerce/adicionar-ia/', views.adicionar_produto_ia, name='adicionar_produto_ia'), # PATH CORRIGIDO AQUI
    path('produtos-ecommerce/selecionar-metodo/', views.selecionar_metodo_criacao, name='selecionar_metodo_criacao'), # ROTA ADICIONADA AQUI
    path('produtos-ecommerce/editar/<int:produto_id>/', views.editar_produto_ecommerce, name='editar_produto_ecommerce'),
    path('produtos-ecommerce/excluir/<int:produto_id>/', views.excluir_produto_ecommerce, name='excluir_produto_ecommerce'),
    path('produtos-ecommerce/excluir-imagem/<int:image_id>/', views.excluir_imagem_produto, name='excluir_imagem_produto'),
    path('produtos-ecommerce/para-revisar/', views.lista_produtos_para_revisao, name='lista_produtos_para_revisao'),
    path('produtos-ecommerce/revisao-ia/', views.resultados_ia, name='pagina_de_resultados_ia'), 
]


handler403 = 'solar.views.acesso_negado'