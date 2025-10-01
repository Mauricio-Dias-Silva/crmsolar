from django.contrib import admin
from .models import Produto, CarouselImage, Pedido, Item, ProdutoImage, RegiaoFrete
from django import forms # NOVO: Importa forms para usar forms.ModelForm

# Inline para ProdutoImage
class ProdutoImageInline(admin.TabularInline):
    model = ProdutoImage
    extra = 1
    fields = ('image', 'alt_text', 'is_main')

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('name', 'preco', 'categoria_id', 'is_active', 'stock', 'created_at')
    list_filter = ('categoria_id', 'is_active')
    search_fields = ('name', 'description', 'sku')
    
    # Removido 'images' daqui, pois é gerenciado pelo inline
    fields = ('name', 'slug', 'description', 'preco', 'categoria_id', 'is_active', 'stock', 'sku')
    
    readonly_fields = ('created_at', 'updated_at')
    
    # Adicionado o inline das imagens
    inlines = [ProdutoImageInline]

@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'image')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')

class ItemPedidoInline(admin.TabularInline):
    model = Item
    extra = 0
    readonly_fields = ('nome', 'preco_unitario', 'quantidade', 'subtotal', 'stripe_product_id')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'email_cliente', 'total', 'status', 'criado_em', 'data_pagamento')
    list_filter = ('status', 'criado_em')
    search_fields = ('id', 'email_cliente', 'stripe_id')
    readonly_fields = ('criado_em', 'data_pagamento', 'stripe_id')
    inlines = [ItemPedidoInline] # Mostra os itens do pedido dentro do formulário de pedido

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('nome', 'pedido', 'quantidade', 'preco_unitario', 'subtotal')
    list_filter = ('pedido__status',)
    search_fields = ('nome', 'pedido__id')

@admin.register(RegiaoFrete)
class RegiaoFreteAdmin(admin.ModelAdmin):
    list_display = ('prefixo_cep', 'cidade', 'valor_frete', 'prazo_entrega')
    search_fields = ('prefixo_cep', 'cidade')