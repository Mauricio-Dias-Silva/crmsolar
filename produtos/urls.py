from django.urls import path
from . import views

app_name = 'produtos'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('search/', views.search, name='search'),
    path('produto/<int:produto_id>/', views.produto_detalhe, name='produto_detalhe'),
    path('categoria/<slug:categoria_slug>/', views.produtos_por_categoria, name='produtos_por_categoria'),
    path('produto/<int:produto_id>/frete/', views.calcular_frete, name='calcular_frete'),
    path('register/', views.register, name='register'),
    path('politica-de-privacidade/', views.politica_privacidade, name='politica_privacidade'),
    path('termos-de-servico/', views.termos_de_servico, name='termos_de_servico'),
    path('ver_carrinho/', views.ver_carrinho, name='ver_carrinho'),
    path('adicionar_ao_carrinho/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('remover_do_carrinho/<int:produto_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
    path('calcular_frete_carrinho/', views.calcular_frete_carrinho, name='calcular_frete_carrinho'),
    path('meus-pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('meus-pedidos/<int:pedido_id>/', views.detalhe_pedido, name='detalhe_pedido'),
]
