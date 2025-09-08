# contratacoes/forms.py

from django import forms
from django.core.exceptions import ValidationError
from .models import (
    ETP, TR, PCA, ItemPCA, PesquisaPreco, ParecerTecnico,
    ItemCatalogo, RequisitoPadrao, Contrato,AtaRegistroPrecos
)
from ckeditor.widgets import CKEditorWidget

class AtaRegistroPrecosForm(forms.ModelForm):
    class Meta:
        model = AtaRegistroPrecos
        # Excluímos os campos que serão preenchidos automaticamente pela view
        exclude = ['processo_vinculado', 'data_criacao']
        widgets = {
            'licitacao_origem': forms.Select(attrs={'class': 'form-select'}),
            'fornecedor_beneficiario': forms.Select(attrs={'class': 'form-select'}),
            'numero_ata': forms.TextInput(attrs={'class': 'form-control'}),
            'ano_ata': forms.NumberInput(attrs={'class': 'form-control'}),
            'objeto': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'valor_total_registrado': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_assinatura': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_inicio_vigencia': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim_vigencia': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        
        
class ItemCatalogoForm(forms.ModelForm):
    class Meta:
        model = ItemCatalogo
        fields = ['nome_padronizado', 'descricao_tecnica', 'unidade_medida', 'preco_historico_medio']
        widgets = {
            'nome_padronizado': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao_tecnica': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'unidade_medida': forms.TextInput(attrs={'class': 'form-control'}),
            'preco_historico_medio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'nome_padronizado': 'Nome Padronizado',
            'descricao_tecnica': 'Descrição Técnica',
            'unidade_medida': 'Unidade de Medida',
            'preco_historico_medio': 'Preço Histórico Médio (R$)',
        }


class ParecerTecnicoForm(forms.ModelForm):
    class Meta:
        model = ParecerTecnico
        fields = ['conteudo', 'autor']

    # Este __init__ é útil para aplicar a classe CSS em todos os campos
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'rows': '3'})
    
    # Adicionamos a mesma lógica clean para ignorar formulários em branco
    def clean(self):
        cleaned_data = super().clean()
        
        # Verifica se o usuário preencheu algum campo neste formulário de parecer
        has_data = any(cleaned_data.get(field) for field in self.fields if field != 'DELETE')

        if not has_data:
            return cleaned_data # Ignora o formulário se estiver vazio

        # Se começou a preencher, torna os campos obrigatórios
        errors = {}
        if not cleaned_data.get('conteudo'):
            errors['conteudo'] = 'O conteúdo do parecer é obrigatório se a linha for pre-fllenchida.'
        if not cleaned_data.get('autor'):
            errors['autor'] = 'O autor do parecer é obrigatório se a linha for preenchida.'
            
        if errors:
            raise ValidationError(errors)
            
        return cleaned_data


class PesquisaPrecoForm(forms.ModelForm):
    class Meta:
        model = PesquisaPreco
        fields = ['fornecedor', 'valor_cotado', 'data_pesquisa']
        widgets = { 'data_pesquisa': forms.DateInput(attrs={'type': 'date'}) }
        labels = {
            'fornecedor': 'Fornecedor / Fonte',
            'valor_cotado': 'Valor Cotado (R$)',
            'data_pesquisa': 'Data da Pesquisa',
        }

    def clean(self):
        cleaned_data = super().clean()
        has_data = any(cleaned_data.get(field) for field in self.fields if field != 'DELETE')
        if not has_data:
            return cleaned_data # Ignora se estiver em branco
        errors = {}
        if not cleaned_data.get('fornecedor'):
            errors['fornecedor'] = 'Este campo é obrigatório.'
        if not cleaned_data.get('valor_cotado'):
            errors['valor_cotado'] = 'Este campo é obrigatório.'
        if not cleaned_data.get('data_pesquisa'):
            errors['data_pesquisa'] = 'Este campo é obrigatório.'
        if errors:
            raise ValidationError(errors)
        return cleaned_data
    

class ETPForm(forms.ModelForm):
    class Meta:
        model = ETP
        fields = [
            'titulo', 'numero_processo', 'setor_demandante', 'item_pca_vinculado',
            'descricao_necessidade', 'objetivo_contratacao', 'requisitos_contratacao',
            'levantamento_solucoes_mercado', 'estimativa_quantidades', 'estimativa_valor',
            'resultados_esperados', 'viabilidade_justificativa_solucao',
            'contratacoes_correlatas', 'alinhamento_planejamento',
        ]
        # Widgets já definem a classe, então o __init__ foi removido por ser redundante.
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_processo': forms.TextInput(attrs={'class': 'form-control'}),
            'setor_demandante': forms.TextInput(attrs={'class': 'form-control'}),
            'item_pca_vinculado': forms.Select(attrs={'class': 'form-select'}), # form-select é melhor para <select>
            'descricao_necessidade': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'objetivo_contratacao': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'requisitos_contratacao': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'levantamento_solucoes_mercado': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
            'estimativa_quantidades': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'estimativa_valor': forms.NumberInput(attrs={'class': 'form-control'}),
            'resultados_esperados': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'viabilidade_justificativa_solucao': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
            'contratacoes_correlatas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'alinhamento_planejamento': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'estimativa_valor': 'Estimativa do Valor (R$)',
            'item_pca_vinculado': 'Vincular ao Item do PCA',
        }

class ETPStatusForm(forms.ModelForm):
    class Meta:
        model = ETP
        fields = ['status', 'observacoes_analise']
        widgets = {
            'observacoes_analise': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}), # form-select é melhor
        }

class TRForm(forms.ModelForm):
    class Meta:
        model = TR
        # Trocado '__all__' por campos explícitos para mais segurança e clareza
        exclude = ['autor', 'data_criacao']
        widgets = {
            'objeto': CKEditorWidget(),
            'justificativa': CKEditorWidget(),
            'especificacoes_tecnicas': CKEditorWidget(),
            'metodologia_execucao': CKEditorWidget(),
            'cronograma_fisico_financeiro': CKEditorWidget(),
            'criterios_habilitacao': CKEditorWidget(),
            'criterios_aceitacao': CKEditorWidget(),
            'criterios_pagamento': CKEditorWidget(),
            'obrigacoes_partes': CKEditorWidget(),
            'sancoes_administrativas': CKEditorWidget(),
            'fiscalizacao_contrato': CKEditorWidget(),
        }

    # Este __init__ é útil e foi mantido, pois aplica estilo apenas nos campos que não são CKEditor
    def __init__(self, *args, **kwargs):
        self.etp_origem_instance = kwargs.pop('etp_origem', None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, CKEditorWidget):
                field.widget.attrs.update({'class': 'form-control'})
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})


    def clean(self):
        cleaned_data = super().clean()
        etp = self.etp_origem_instance 
        if etp and etp.requisitos_contratacao and not cleaned_data.get('especificacoes_tecnicas'):
            self.add_error('especificacoes_tecnicas', 'Este campo é obrigatório, pois o ETP de origem possui requisitos.')
        return cleaned_data

class TRStatusForm(forms.ModelForm):
    class Meta:
        model = TR
        fields = ['status', 'observacoes_analise']
        widgets = {
            'observacoes_analise': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class PCAForm(forms.ModelForm):
    class Meta:
        model = PCA
        exclude = ['responsavel_aprovacao']
        widgets = {
            'ano_vigencia': forms.NumberInput(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'data_aprovacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'arquivo_pca': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ItemPCAForm(forms.ModelForm):
    class Meta:
        model = ItemPCA
        exclude = ['pca']
        widgets = {
            'identificador_item': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao_item': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'valor_estimado_pca': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidade_requisitante': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        # Excluímos campos que serão preenchidos automaticamente pela view
        exclude = ['processo_vinculado', 'data_criacao']
        widgets = {
            'licitacao_origem': forms.Select(attrs={'class': 'form-select'}),
            'contratado': forms.Select(attrs={'class': 'form-select'}),
            'numero_contrato': forms.TextInput(attrs={'class': 'form-control'}),
            'ano_contrato': forms.NumberInput(attrs={'class': 'form-control'}),
            'objeto': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_assinatura': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_inicio_vigencia': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim_vigencia': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }