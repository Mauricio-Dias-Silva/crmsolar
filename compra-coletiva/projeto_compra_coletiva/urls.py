# projeto_compra_coletiva/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rotas de Autenticação (allauth) primeiro, pois são básicas
    path('contas/', include('allauth.urls')), 
    
    # Painéis específicos antes das rotas mais genéricas
    path('painel-vendedor/', include('vendedores_painel.urls')), 
    
    # Rotas de apps que usam models de outros apps (como compras que usa ofertas)
    path('compras/', include('compras.urls')), 
    path('pagamentos/', include('pagamentos.urls')),
    path('pedidos-coletivos/', include('pedidos_coletivos.urls')), # <--- Mantenha esta aqui

    # Por último, a rota mais genérica que inclui a homepage e a lista de ofertas
    # que pode usar info de outros apps (categorias, etc.)
    path('', include('ofertas.urls')), 
]

# Apenas para servir arquivos de mídia durante o desenvolvimento.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)