# ofertas/sitemaps.py

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Oferta, Categoria # Importe seus modelos

class OfertaSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Oferta.objects.filter(publicada=True, status__in=['ativa', 'sucesso'])

    def lastmod(self, obj):
        return obj.data_atualizacao 

    def location(self, obj):
        return reverse('ofertas:detalhe_oferta', args=[obj.slug])

class CategoriaSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Categoria.objects.filter(ativa=True)

    def location(self, obj):
        return reverse('ofertas:ofertas_por_categoria', args=[obj.slug])

class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ['ofertas:lista_ofertas', 'ofertas:compre_junto']

    def location(self, item):
        return reverse(item)