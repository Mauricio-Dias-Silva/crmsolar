# ofertas/urls.py

from django.urls import path
from . import views

app_name = 'ofertas' 

urlpatterns = [
    path('', views.lista_ofertas, name='lista_ofertas'), # Página inicial (apenas unidade)
    path('categoria/<slug:slug_categoria>/', views.lista_ofertas, name='ofertas_por_categoria'), 
    path('compre-junto/', views.compre_junto_view, name='compre_junto'), # <--- AGORA APONTA PARA A NOVA VIEW!
    path('<slug:slug_oferta>/', views.detalhe_oferta, name='detalhe_oferta'), 
]