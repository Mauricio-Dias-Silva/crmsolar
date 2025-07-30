# ofertas/admin.py

from django.contrib import admin
from django.db.models import Sum, Count # Para agregações
# Certifique-se que todos os modelos estão importados aqui, uma única vez.
from .models import Vendedor, Categoria, Oferta, Avaliacao, Banner
# Importe Compra e Cupom para as estatísticas
from compras.models import Compra, Cupom 

# Importe Usuario e criar_notificacao para as notificações no Admin
from contas.models import Usuario # <--- ADICIONADO AQUI
from contas.models import criar_notificacao # <--- ADICIONADO AQUI


# === VendedorAdmin ===
@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ('nome_empresa', 'cnpj', 'email_contato', 'ativo', 'status_aprovacao', 'data_cadastro', 'get_total_vendas_aprovadas', 'get_total_cupons_resgatados')
    list_filter = ('ativo', 'status_aprovacao')
    search_fields = ('nome_empresa', 'cnpj', 'email_contato')
    actions = ['aprovar_vendedores', 'suspender_vendedores', 'rejeitar_vendedores']

    @admin.action(description='Aprovar vendedores selecionados')
    def aprovar_vendedores(self, request, queryset):
        aprovados_count = 0
        for vendedor in queryset:
            # Ação para aprovar: muda status, ativa e notifica
            if vendedor.status_aprovacao != 'aprovado': # Apenas se não estiver já aprovado
                vendedor.status_aprovacao = 'aprovado'
                vendedor.ativo = True
                vendedor.save() # Dispara o save() para que a notificação individual seja gerada
                aprovados_count += 1
                
                # Notificar o vendedor
                if vendedor.usuario_associado:
                    criar_notificacao(
                        vendedor.usuario_associado,
                        f'Status de Vendedor: {vendedor.nome_empresa} Aprovado!',
                        f'Parabéns! Sua empresa {vendedor.nome_empresa} foi aprovada. Você já pode acessar o painel do vendedor e cadastrar ofertas.',
                        'vendedor',
                        reverse('vendedores_painel:dashboard') # Requer importação de reverse
                    )
        if aprovados_count > 0:
            self.message_user(request, f'{aprovados_count} vendedores foram aprovados com sucesso.')
        else:
            self.message_user(request, 'Nenhum vendedor novo foi aprovado ou já estavam aprovados.', level='warning')
    
    @admin.action(description='Suspender vendedores selecionados')
    def suspender_vendedores(self, request, queryset):
        suspensos_count = 0
        for vendedor in queryset:
            # Ação para suspender: muda status, desativa e notifica
            if vendedor.status_aprovacao != 'suspenso': # Apenas se não estiver já suspenso
                vendedor.status_aprovacao = 'suspenso'
                vendedor.ativo = False
                vendedor.save()
                suspensos_count += 1
                
                # Notificar o vendedor
                if vendedor.usuario_associado:
                    criar_notificacao(
                        vendedor.usuario_associado,
                        f'Status de Vendedor: {vendedor.nome_empresa} Suspenso',
                        f'Atenção! Sua conta de vendedor para {vendedor.nome_empresa} foi suspensa. Entre em contato com o suporte para mais informações.',
                        'vendedor',
                        None
                    )
        if suspensos_count > 0:
            self.message_user(request, f'{suspensos_count} vendedores foram suspensos com sucesso.')
        else:
            self.message_user(request, 'Nenhum vendedor novo foi suspenso ou já estavam suspensos.', level='warning')


    @admin.action(description='Rejeitar vendedores selecionados')
    def rejeitar_vendedores(self, request, queryset):
        rejeitados_count = 0
        for vendedor in queryset:
            # Ação para rejeitar: muda status, desativa e notifica
            if vendedor.status_aprovacao != 'rejeitado': # Apenas se não estiver já rejeitado
                vendedor.status_aprovacao = 'rejeitado'
                vendedor.ativo = False
                vendedor.save()
                rejeitados_count += 1
                
                # Notificar o vendedor
                if vendedor.usuario_associado:
                    criar_notificacao(
                        vendedor.usuario_associado,
                        f'Status de Vendedor: {vendedor.nome_empresa} Rejeitado',
                        f'Informamos que seu cadastro para {vendedor.nome_empresa} foi rejeitado. Para mais detalhes, por favor, entre em contato.',
                        'vendedor',
                        None
                    )
        if rejeitados_count > 0:
            self.message_user(request, f'{rejeitados_count} vendedores foram rejeitados com sucesso.')
        else:
            self.message_user(request, 'Nenhum vendedor novo foi rejeitado ou já estavam rejeitados.', level='warning')

    # Métodos para exibir estatísticas no list_display
    @admin.display(description='Vendas Aprovadas (R$)')
    def get_total_vendas_aprovadas(self, obj):
        total_vendas = Compra.objects.filter(
            oferta__vendedor=obj,
            status_pagamento='aprovada'
        ).aggregate(Sum('valor_total'))['valor_total__sum'] or 0.00
        return f'R$ {total_vendas:.2f}'

    @admin.display(description='Cupons Resgatados')
    def get_total_cupons_resgatados(self, obj):
        total_resgatados = Cupom.objects.filter(
            oferta__vendedor=obj,
            status='resgatado'
        ).count()
        return total_resgatados

# === CategoriaAdmin ===
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug', 'ativa')
    prepopulated_fields = {'slug': ('nome',)}
    search_fields = ('nome',)

# === OfertaAdmin ===
@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'vendedor', 'categoria', 'preco_desconto', 'data_inicio', 'data_termino', 'publicada', 'status', 'tipo_oferta', 'quantidade_vendida')
    list_filter = ('categoria', 'publicada', 'status', 'vendedor', 'tipo_oferta')
    search_fields = ('titulo', 'descricao_detalhada', 'vendedor__nome_empresa')
    prepopulated_fields = {'slug': ('titulo',)}
    date_hierarchy = 'data_inicio'
    raw_id_fields = ('vendedor', 'categoria') 
    actions = ['publicar_ofertas', 'despublicar_ofertas']

    @admin.action(description='Publicar ofertas selecionadas')
    def publicar_ofertas(self, request, queryset):
        updated = queryset.update(publicada=True)
        self.message_user(request, f'{updated} ofertas foram publicadas com sucesso.')
    
    @admin.action(description='Despublicar ofertas selecionadas')
    def despublicar_ofertas(self, request, queryset):
        updated = queryset.update(publicada=False)
        self.message_user(request, f'{updated} ofertas foram despublicadas com sucesso.')

# === AvaliacaoAdmin ===
@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('oferta', 'usuario', 'nota', 'data_avaliacao')
    list_filter = ('nota', 'oferta__titulo', 'usuario__username')
    search_fields = ('oferta__titulo', 'usuario__username', 'comentario')
    raw_id_fields = ('oferta', 'usuario')

# === BannerAdmin ===
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ativo', 'ordem', 'url_destino')
    list_filter = ('ativo',)
    search_fields = ('titulo',)