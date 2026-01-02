# SysGov_Project/financeiro/forms.py

from django import forms
from .models import DocumentoFiscal, Pagamento, NotaEmpenho


class DocumentoFiscalForm(forms.ModelForm):
    class Meta:
        model = DocumentoFiscal
        # Usamos 'exclude' para os campos que a view irá preencher automaticamente
        exclude = ['processo_vinculado', 'contrato_vinculado', 'fornecedor']
        # Widgets para estilização com Bootstrap
        widgets = {
            'documento_fiscal_numero': forms.TextInput(attrs={'class': 'form-control'}),
            'documento_fiscal_valor': forms.NumberInput(attrs={'class': 'form-control'}),
            'documento_fiscal_data_emissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'documento_fiscal_numero': "Número do Documento Fiscal (NF)",
            'documento_fiscal_valor': "Valor do Documento Fiscal",
            'documento_fiscal_data_emissao': "Data de Emissão do Documento Fiscal",
        }

class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        # O formulário agora só pede os dados do pagamento, pois o resto vem do Documento Fiscal
        fields = ['nota_fiscal_valor_pago', 'nota_fiscal_pagto_dt', 'forma_pagamento']
        widgets = {
            'nota_fiscal_valor_pago': forms.NumberInput(attrs={'class': 'form-control'}),
            'nota_fiscal_pagto_dt': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'forma_pagamento': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nota_fiscal_valor_pago': "Valor Pago da Nota Fiscal",
            'nota_fiscal_pagto_dt': "Data Efetiva do Pagamento",
            'forma_pagamento': "Forma de Pagamento",
        }
        


class NotaEmpenhoForm(forms.ModelForm):
    class Meta:
        model = NotaEmpenho
        exclude = ['contrato', 'fornecedor']
        widgets = {
            'numero_empenho': forms.TextInput(attrs={'class': 'form-control'}),
            'ano_empenho': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_emissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

