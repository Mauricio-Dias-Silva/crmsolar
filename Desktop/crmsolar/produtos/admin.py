from django.contrib import admin
from .models import Produto, CarouselImage, Pedido, Item, ProdutoImage, RegiaoFrete
from django import forms 


# Inline para ProdutoImage
class ProdutoImageInline(admin.TabularInline):
    model = ProdutoImage
    extra = 1
    fields = ('image', 'alt_text', 'is_main')

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('name', 'preco', 'categoria_id', 'is_active', 'stock', 'garantia_anos_equipamento', 'created_at')
    list_filter = ('categoria_id', 'is_active', 'tipo_equipamento')
    search_fields = ('name', 'description', 'sku')
    prepopulated_fields = {'slug': ('name',)}
    
    inlines = [ProdutoImageInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'preco', 'is_active', 'tipo_equipamento', 'garantia_anos_equipamento')
        }),
        ('Detalhes de Estoque', {
            'fields': ('categoria_id', 'stock', 'sku', 'peso', 'dimensoes', 'garantia')
        }),
    )
    readonly_fields = ('created_at', 'updated_at',)


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
    list_filter = ('status', 'criado_em', 'metodo_pagamento')
    search_fields = ('id__exact', 'email_cliente', 'stripe_id', 'mercadopago_id')
    readonly_fields = ('criado_em', 'data_pagamento', 'stripe_id', 'metodo_pagamento', 'mercadopago_id')
    inlines = [ItemPedidoInline]

@admin.register(RegiaoFrete)
class RegiaoFreteAdmin(admin.ModelAdmin):
    list_display = ('prefixo_cep', 'cidade', 'valor_frete', 'prazo_entrega')
    search_fields = ('prefixo_cep', 'cidade')
