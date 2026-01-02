# SysGov_Project/financeiro/models.py

from django.db import models
from core.models import Processo, Fornecedor
from contratacoes.models import Contrato

# --- MODELO DOCUMENTO FISCAL (ATUALIZADO) ---
class DocumentoFiscal(models.Model):
    processo_vinculado = models.ForeignKey(
        Processo,
        on_delete=models.CASCADE,
        related_name='documentos_fiscais'
    )
    # Adicionamos a ligação ao Contrato e Fornecedor para facilitar
    contrato_vinculado = models.ForeignKey(
        Contrato,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='documentos_fiscais'
    )
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.PROTECT, null=True, blank=True,
        related_name='documentos_fiscais'
    )
    # Campos essenciais do documento
    documento_fiscal_numero = models.CharField(max_length=15, verbose_name="Número do Documento Fiscal (NF)")
    documento_fiscal_valor = models.DecimalField(max_digits=17, decimal_places=2, verbose_name="Valor do Documento Fiscal")
    documento_fiscal_data_emissao = models.DateField(verbose_name="Data de Emissão do Documento Fiscal")
    
    # Manteremos os campos do AUDESP se eles forem preenchidos aqui
    codigo_ajuste = models.CharField(max_length=20, verbose_name="Código do Ajuste/Empenho", blank=True)
    nota_empenho_numero = models.CharField(max_length=35, verbose_name="Número da Nota de Empenho", blank=True)

    class Meta:
        verbose_name = "Documento Fiscal"
        verbose_name_plural = "Documentos Fiscais"
        ordering = ['-documento_fiscal_data_emissao']

    def __str__(self):
        return f"NF {self.documento_fiscal_numero}"

# --- MODELO PAGAMENTO (REESTRUTURADO) ---
class Pagamento(models.Model):
    # <<< MUDANÇA PRINCIPAL: LIGAÇÃO DIRETA AO DOCUMENTO FISCAL >>>
    documento_fiscal = models.ForeignKey(
        DocumentoFiscal,
        on_delete=models.CASCADE,
        related_name='pagamentos',
        verbose_name="Documento Fiscal Vinculado"
    )
   
    nota_fiscal_valor_pago = models.DecimalField(max_digits=17, decimal_places=2, verbose_name="Valor Pago")
    nota_fiscal_pagto_dt = models.DateField(verbose_name="Data Efetiva do Pagamento")
    forma_pagamento = models.CharField(max_length=100, default="Transferência Bancária", verbose_name="Forma de Pagamento")
    
    # Os outros campos (nº da nota, etc.) agora são acedidos através de 'documento_fiscal'
    # Ex: pagamento.documento_fiscal.documento_fiscal_numero

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ['-nota_fiscal_pagto_dt']

    def __str__(self):
        return f"Pagamento de R$ {self.nota_fiscal_valor_pago} para a NF {self.documento_fiscal.documento_fiscal_numero}"

# --- MODELO NOTA DE EMPENHO (SEM ALTERAÇÕES) ---
STATUS_EMPENHO_CHOICES = [
    ('VALIDO', 'Válido'),
    ('CANCELADO', 'Cancelado'),
    ('LIQUIDADO', 'Liquidado'),
]

class NotaEmpenho(models.Model):
    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.CASCADE,
        related_name='notas_empenho',
        verbose_name="Contrato Vinculado"
    )
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.PROTECT,
        related_name='empenhos',
        verbose_name="Fornecedor"
    )
    numero_empenho = models.CharField(
        max_length=50,
        verbose_name="Número do Empenho"
    )
    ano_empenho = models.IntegerField(
        verbose_name="Ano do Empenho"
    )
    data_emissao = models.DateField(
        verbose_name="Data de Emissão"
    )
    valor = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Valor do Empenho (R$)"
    )
    descricao = models.TextField(
        verbose_name="Descrição/Histórico do Empenho"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_EMPENHO_CHOICES,
        default='VALIDO',
        verbose_name="Status do Empenho"
    )

    class Meta:
        verbose_name = "Nota de Empenho"
        verbose_name_plural = "Notas de Empenho"
        unique_together = ('numero_empenho', 'ano_empenho')
        ordering = ['-ano_empenho', '-data_emissao']

    def __str__(self):
        return f"Empenho {self.numero_empenho}/{self.ano_empenho} - {self.fornecedor.razao_social}"