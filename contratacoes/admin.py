# SysGov_Project/contratacoes/admin.py

from django.contrib import admin
# ADICIONADO Contrato À IMPORTAÇÃO
from .models import (
    ETP, TR, PCA, ItemPCA, ItemCatalogo, PesquisaPreco, AtaRegistroPrecos,
    ParecerTecnico, ModeloTexto, RequisitoPadrao, Contrato
)

# Opcional: Classes Admin personalizadas para melhor visualização no Django Admin
class ETPAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'numero_processo', 'setor_demandante', 'autor', 'status', 'data_criacao')
    list_filter = ('status', 'setor_demandante', 'data_criacao')
    search_fields = ('titulo', 'numero_processo', 'descricao_necessidade')
    raw_id_fields = ('processo_vinculado', 'autor', 'item_pca_vinculado')
    date_hierarchy = 'data_criacao'

class TRAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'numero_processo', 'etp_origem', 'autor', 'status', 'data_criacao')
    list_filter = ('status', 'data_criacao')
    search_fields = ('titulo', 'numero_processo', 'objeto')
    raw_id_fields = ('etp_origem', 'processo_vinculado', 'autor')
    date_hierarchy = 'data_criacao'

class PCAAdmin(admin.ModelAdmin):
    list_display = ('ano_vigencia', 'titulo', 'data_aprovacao', 'responsavel_aprovacao')
    list_filter = ('ano_vigencia',)
    search_fields = ('titulo', 'descricao')
    raw_id_fields = ('responsavel_aprovacao',)

class ItemPCAAdmin(admin.ModelAdmin):
    list_display = ('identificador_item', 'descricao_item', 'pca', 'valor_estimado_pca', 'unidade_requisitante')
    list_filter = ('pca__ano_vigencia', 'unidade_requisitante')
    search_fields = ('identificador_item', 'descricao_item')
    raw_id_fields = ('pca',)

class ItemCatalogoAdmin(admin.ModelAdmin):
    list_display = ('nome_padronizado', 'unidade_medida', 'preco_historico_medio', 'data_ultima_atualizacao')
    search_fields = ('nome_padronizado', 'descricao_tecnica')

class PesquisaPrecoAdmin(admin.ModelAdmin):
    list_display = ('etp', 'fornecedor', 'valor_cotado', 'data_pesquisa')
    list_filter = ('data_pesquisa', 'fornecedor')
    search_fields = ('fornecedor',)
    raw_id_fields = ('etp',)

class ParecerTecnicoAdmin(admin.ModelAdmin):
    list_display = ('etp', 'autor', 'data_criacao', 'conteudo')
    list_filter = ('data_criacao', 'autor')
    raw_id_fields = ('etp', 'autor')

class ModeloTextoAdmin(admin.ModelAdmin):
    list_display = ('titulo',)
    search_fields = ('titulo', 'texto')

class RequisitoPadraoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'titulo', 'ativo', 'criado_em')
    list_filter = ('ativo',)
    search_fields = ('codigo', 'titulo', 'descricao')

# NOVA CLASSE ADMIN PARA CONTRATOS
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('numero_contrato', 'ano_contrato', 'contratado', 'valor_total', 'status', 'data_assinatura')
    list_filter = ('status', 'ano_contrato', 'contratado')
    search_fields = ('numero_contrato', 'objeto', 'contratado__razao_social')
    raw_id_fields = ('processo_vinculado', 'licitacao_origem', 'contratado')
    date_hierarchy = 'data_assinatura'


class AtaRegistroPrecosAdmin(admin.ModelAdmin):
    list_display = ('numero_ata', 'ano_ata', 'fornecedor_beneficiario', 'valor_total_registrado', 'status')
    list_filter = ('status', 'ano_ata')
    search_fields = ('numero_ata', 'objeto', 'fornecedor_beneficiario__razao_social')
    raw_id_fields = ('processo_vinculado', 'licitacao_origem', 'fornecedor_beneficiario')
    date_hierarchy = 'data_assinatura'


admin.site.register(Contrato, ContratoAdmin)
admin.site.register(AtaRegistroPrecos)
admin.site.register(ETP, ETPAdmin)
admin.site.register(TR, TRAdmin)
admin.site.register(PCA, PCAAdmin)
admin.site.register(ItemPCA, ItemPCAAdmin)
admin.site.register(ItemCatalogo, ItemCatalogoAdmin)
admin.site.register(PesquisaPreco, PesquisaPrecoAdmin)
admin.site.register(ParecerTecnico, ParecerTecnicoAdmin)
admin.site.register(ModeloTexto, ModeloTextoAdmin)
admin.site.register(RequisitoPadrao, RequisitoPadraoAdmin)
