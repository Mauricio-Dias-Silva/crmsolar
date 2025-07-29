# ofertas/urls.py

from django.urls import path
from . import views # Importa as visualizações do mesmo diretório

app_name = 'ofertas' # Define um namespace para as URLs do app, ajuda a evitar conflitos

urlpatterns = [
    path('', views.lista_ofertas, name='lista_ofertas'), # Rota para a lista de ofertas (ex: /ofertas/)
    path('categoria/<slug:slug_categoria>/', views.lista_ofertas, name='ofertas_por_categoria'),
    path('<slug:slug_oferta>/', views.detalhe_oferta, name='detalhe_oferta'), # Rota para o detalhe da oferta (ex: /ofertas/minha-oferta/)
]