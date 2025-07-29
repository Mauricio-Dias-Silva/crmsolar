# compras/admin.py
from django.contrib import admin
from .models import Compra, Cupom

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'oferta', 'quantidade', 'valor_total', 'status_pagamento', 'data_compra')
    list_filter = ('status_pagamento', 'data_compra')
    search_fields = ('usuario__username', 'oferta__titulo', 'id_transacao')
    raw_id_fields = ('usuario', 'oferta')



@admin.register(Cupom)
class CupomAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'oferta', 'usuario', 'status', 'valido_ate', 'data_resgate')
    list_filter = ('status', 'valido_ate')
    search_fields = ('codigo', 'oferta__titulo', 'usuario__username')

    # Remova 'resgatado_por_vendedor' temporariamente para testar
    raw_id_fields = ('compra', 'oferta', 'usuario',) # <--- Mude aqui!

# ... (Seus outros registros de admin)