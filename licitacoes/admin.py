# SysGov_Project/licitacoes/admin.py

from django.contrib import admin
from .models import Edital, Lote, ItemLicitado, Pregao, ParticipanteLicitacao, Lance

@admin.register(Edital)
class EditalAdmin(admin.ModelAdmin):
    # CORRIGIDO: Trocado 'data_abertura_proposta' por 'data_abertura_propostas'
    list_display = ('numero_edital', 'modalidade_audesp', 'titulo', 'data_abertura_propostas')
    list_filter = ('modalidade_audesp', 'srp', 'status')
    search_fields = ('numero_edital', 'titulo', 'objeto_compra_audesp')
    date_hierarchy = 'data_publicacao'

@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('edital', 'numero_lote', 'descricao')
    list_filter = ('edital',)
    search_fields = ('descricao',)

@admin.register(ItemLicitado)
class ItemLicitadoAdmin(admin.ModelAdmin):
    list_display = ('descricao_item', 'quantidade', 'unidade_medida', 'lote')
    list_filter = ('unidade_medida', 'lote__edital')
    search_fields = ('descricao_item',)

@admin.register(Pregao)
class PregaoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'pregoeiro', 'data_abertura_sessao', 'status')
    list_filter = ('status', 'pregoeiro')
    search_fields = ('edital__numero_edital', 'edital__titulo')
    raw_id_fields = ('edital', 'pregoeiro')
    date_hierarchy = 'data_abertura_sessao'

@admin.register(ParticipanteLicitacao)
class ParticipanteLicitacaoAdmin(admin.ModelAdmin):
    list_display = ('fornecedor', 'pregao', 'data_credenciamento', 'desclassificado')
    list_filter = ('pregao__edital__numero_edital', 'desclassificado')
    search_fields = ('fornecedor__razao_social', 'fornecedor__cnpj')
    raw_id_fields = ('pregao', 'fornecedor')

@admin.register(Lance)
class LanceAdmin(admin.ModelAdmin):
    list_display = ('item', 'participante', 'valor_lance', 'data_lance', 'aceito')
    list_filter = ('aceito', 'item__lote__edital')
    search_fields = ('item__descricao_item', 'participante__fornecedor__razao_social')
    raw_id_fields = ('participante', 'item')