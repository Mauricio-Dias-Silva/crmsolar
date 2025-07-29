# ofertas/admin.py
from django.contrib import admin
from .models import Vendedor, Categoria, Oferta

@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ('nome_empresa', 'cnpj', 'email_contato', 'ativo', 'data_cadastro')
    search_fields = ('nome_empresa', 'cnpj')
    list_filter = ('ativo',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug', 'ativa')
    prepopulated_fields = {'slug': ('nome',)} # Gera o slug automaticamente
    search_fields = ('nome',)

@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'vendedor', 'categoria', 'preco_desconto', 'data_inicio', 'data_termino', 'publicada', 'status', 'quantidade_vendida')
    list_filter = ('categoria', 'publicada', 'status', 'vendedor')
    search_fields = ('titulo', 'descricao_detalhada', 'vendedor__nome_empresa')
    prepopulated_fields = {'slug': ('titulo',)}
    date_hierarchy = 'data_inicio' # Permite navegar por data
    raw_id_fields = ('vendedor', 'categoria') # Para campos ForeignKey, melhora a UX com muitos itens