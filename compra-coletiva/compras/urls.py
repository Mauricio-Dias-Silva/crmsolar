# compras/urls.py

from django.urls import path
from . import views # Importa as visualizações do mesmo diretório

app_name = 'compras' # Define um namespace para as URLs do app

urlpatterns = [
    # URL para a página de confirmação de compra e processamento
    path('comprar/<slug:slug_oferta>/', views.comprar_oferta, name='comprar_oferta'),
    
    # URL para a área do usuário (meus cupons)
    path('meus-cupons/', views.meus_cupons, name='meus_cupons'),
]