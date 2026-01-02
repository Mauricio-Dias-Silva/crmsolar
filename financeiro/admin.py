# SysGov_Project/financeiro/admin.py

from django.contrib import admin
from .models import DocumentoFiscal, Pagamento, NotaEmpenho

@admin.register(DocumentoFiscal)
class DocumentoFiscalAdmin(admin.ModelAdmin):
    list_display = (
        'documento_fiscal_numero', 
        'get_fornecedor_nome', # Usamos um método para buscar o nome
        'documento_fiscal_valor', 
        'documento_fiscal_data_emissao', 
        'contrato_vinculado'
    )
    list_filter = ('documento_fiscal_data_emissao', 'fornecedor')
    search_fields = ('documento_fiscal_numero', 'fornecedor__razao_social', 'contrato_vinculado__numero_contrato')
    raw_id_fields = ('processo_vinculado', 'contrato_vinculado', 'fornecedor')
    date_hierarchy = 'documento_fiscal_data_emissao'

    @admin.display(description='Fornecedor', ordering='fornecedor__razao_social')
    def get_fornecedor_nome(self, obj):
        if obj.fornecedor:
            return obj.fornecedor.razao_social
        return "N/A"

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = (
        'get_documento_fiscal_numero', # Usamos um método
        'nota_fiscal_valor_pago', 
        'nota_fiscal_pagto_dt', 
        'forma_pagamento'
    )
    list_filter = ('nota_fiscal_pagto_dt', 'forma_pagamento')
    # CORRIGIDO: A busca agora usa o caminho correto através do relacionamento
    search_fields = ('documento_fiscal__documento_fiscal_numero', 'documento_fiscal__fornecedor__razao_social')
    raw_id_fields = ('documento_fiscal',)
    date_hierarchy = 'nota_fiscal_pagto_dt'

    @admin.display(description='Nº Documento Fiscal', ordering='documento_fiscal__documento_fiscal_numero')
    def get_documento_fiscal_numero(self, obj):
        return obj.documento_fiscal.documento_fiscal_numero

@admin.register(NotaEmpenho)
class NotaEmpenhoAdmin(admin.ModelAdmin):
    list_display = ('numero_empenho', 'ano_empenho', 'fornecedor', 'valor', 'data_emissao', 'status')
    list_filter = ('status', 'ano_empenho', 'fornecedor')
    search_fields = ('numero_empenho', 'descricao', 'fornecedor__razao_social')
    raw_id_fields = ('contrato', 'fornecedor')
    date_hierarchy = 'data_emissao'