# projeto_compra_coletiva/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap # <--- Importe sitemap view

# Importe suas classes de sitemap
from ofertas.sitemaps import OfertaSitemap, CategoriaSitemap, StaticViewSitemap # <--- Importe seus sitemaps


# Dicionário de sitemaps para a URLconf
sitemaps = {
    'ofertas': OfertaSitemap,
    'categorias': CategoriaSitemap,
    'static': StaticViewSitemap,
}


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('contas/', include('contas.urls')), 
    path('contas/', include('allauth.urls')), 

    path('painel-vendedor/', include('vendedores_painel.urls')), 
    path('', include('ofertas.urls')), 
    path('compras/', include('compras.urls')), 
    path('pagamentos/', include('pagamentos.urls')),
    path('pedidos-coletivos/', include('pedidos_coletivos.urls')),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'), # <--- NOVA URL DO SITEMAP
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)