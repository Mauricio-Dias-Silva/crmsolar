# SysGov_Project/licitacoes/forms.py

from django import forms
from .models import (
    Edital, Lote, ItemLicitado, ResultadoLicitacao, # APENAS os modelos de licitacoes
    # Importar os CHOICES (se precisar deles diretamente no form e forem definidos em licitacoes.models)
    STATUS_EDITAL_CHOICES, TIPO_INSTRUMENTO_CONVOCATORIO_CHOICES,
    MODALIDADE_LICITACAO_CHOICES, MODO_DISPUTA_CHOICES, VEICULO_PUBLICACAO_CHOICES,
    TIPO_BENEFICIO_CHOICES, CRITERIO_JULGAMENTO_CHOICES, ITEM_CATEGORIA_CHOICES,ParticipanteLicitacao,Fornecedor
)
from django.db.models import Q # Necessário para filtrar querysets em ResultadoLicitacaoForm

# --- Formulários para Edital ---
# licitacoes/forms.py

# --- Formulários para Edital ---
class EditalForm(forms.ModelForm):
    class Meta:
        model = Edital
        fields = [
            'numero_edital', 'titulo', 'tipo_licitacao', 'data_publicacao',
            'data_abertura_propostas', 'local_abertura', 'link_edital_completo',
            'valor_estimado', 'status',
            # Campos AUDESP
            'retificacao', 'codigo_unidade_compradora', 'tipo_instrumento_convocatorio_audesp',
            'modalidade_audesp', 'modo_disputa', 'numero_compra_audesp', 'ano_compra_audesp',
            'numero_processo_origem_audesp', 'objeto_compra_audesp', 'informacao_complementar',
            'srp', 'data_encerramento_proposta', 'amparo_legal', 'link_sistema_origem',
            'justificativa_presencial',
            'arquivo_edital', # Este já estava correto
        ]
        widgets = {
            'numero_edital': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: PE 001/2025'}),
            'titulo': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Objeto detalhado da licitação'}),
            'tipo_licitacao': forms.Select(attrs={'class': 'form-select'}),
            'data_publicacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_abertura_propostas': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'local_abertura': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Sala de Reuniões da SMG'}),
            'link_edital_completo': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://exemplo.gov.br/edital/123'}),
            'valor_estimado': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'retificacao': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'codigo_unidade_compradora': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_instrumento_convocatorio_audesp': forms.Select(attrs={'class': 'form-select'}),
            'modalidade_audesp': forms.Select(attrs={'class': 'form-select'}),
            'modo_disputa': forms.Select(attrs={'class': 'form-select'}),
            'numero_compra_audesp': forms.TextInput(attrs={'class': 'form-control'}),
            'ano_compra_audesp': forms.NumberInput(attrs={'class': 'form-control'}),
            'numero_processo_origem_audesp': forms.TextInput(attrs={'class': 'form-control'}),
            'objeto_compra_audesp': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'informacao_complementar': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'srp': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'data_encerramento_proposta': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'amparo_legal': forms.Select(attrs={'class': 'form-select'}),
            'link_sistema_origem': forms.URLInput(attrs={'class': 'form-control'}),
            'justificativa_presencial': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            
            # vvv ADICIONE ESTA LINHA FALTANTE AQUI vvv
            'arquivo_edital': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'numero_edital': 'Número do Edital', 'titulo': 'Objeto da Licitação',
            'tipo_licitacao': 'Tipo de Licitação', 'data_publicacao': 'Data de Publicação',
            'data_abertura_propostas': 'Data e Hora de Abertura', 'local_abertura': 'Local de Abertura',
            'link_edital_completo': 'Link para Edital Completo', 'valor_estimado': 'Valor Estimado',
            'status': 'Status Atual', 'retificacao': 'É Retificação?',
            'codigo_unidade_compradora': 'Cód. Unidade Compradora (AUDESP)',
            'tipo_instrumento_convocatorio_audesp': 'Tipo Instrumento Convocatório (AUDESP)',
            'modalidade_audesp': 'Modalidade (AUDESP)', 'modo_disputa': 'Modo de Disputa (AUDESP)',
            'numero_compra_audesp': 'Número da Compra (AUDESP)', 'ano_compra_audesp': 'Ano da Compra (AUDESP)',
            'numero_processo_origem_audesp': 'Número Processo Origem (AUDESP)', 'objeto_compra_audesp': 'Objeto da Compra (AUDESP)',
            'informacao_complementar': 'Informações Complementares', 'srp': 'Sistema de Registro de Preços (SRP)?',
            'data_encerramento_proposta': 'Data/Hora Encerramento Proposta (AUDESP)', 'amparo_legal': 'Amparo Legal (AUDESP)',
            'link_sistema_origem': 'Link Sistema de Origem (AUDESP)', 'justificativa_presencial': 'Justificativa Presencial (AUDESP)',

            # vvv E ADICIONE ESTA LINHA FALTANTE AQUI vvv
            'arquivo_edital': 'Arquivo PDF do Edital',
        }

# --- Formulários para Lote e ItemLicitado ---
class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['numero_lote', 'descricao', 'valor_estimado_lote']
        widgets = {
            'numero_lote': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'valor_estimado_lote': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'numero_lote': 'Número do Lote', 'descricao': 'Descrição do Lote',
            'valor_estimado_lote': 'Valor Estimado do Lote',
        }

class ItemLicitadoForm(forms.ModelForm):
    class Meta:
        model = ItemLicitado
        fields = [
            'lote', 'edital', 'descricao_item', 'quantidade', 'unidade_medida', 'valor_referencia',
            'fornecedor_vencedor', 'valor_ofertado',
            'numero_item_audesp', 'material_ou_servico', 'tipo_beneficio',
            'incentivo_produtivo_basico', 'orcamento_sigiloso',
            'valor_unitario_estimado_audesp', 'valor_total_audesp',
            'criterio_julgamento', 'item_categoria', 'patrimonio', 'codigo_registro_imobiliario'
        ]
        widgets = {
            'lote': forms.Select(attrs={'class': 'form-select'}), 'edital': forms.Select(attrs={'class': 'form-select'}),
            'descricao_item': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}), 'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unidade_medida': forms.TextInput(attrs={'class': 'form-control'}), 'valor_referencia': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fornecedor_vencedor': forms.TextInput(attrs={'class': 'form-control'}), 'valor_ofertado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'numero_item_audesp': forms.NumberInput(attrs={'class': 'form-control'}), 'material_ou_servico': forms.Select(attrs={'class': 'form-select'}),
            'tipo_beneficio': forms.Select(attrs={'class': 'form-select'}), 'incentivo_produtivo_basico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'orcamento_sigiloso': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'valor_unitario_estimado_audesp': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'valor_total_audesp': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'criterio_julgamento': forms.Select(attrs={'class': 'form-select'}), 'item_categoria': forms.Select(attrs={'class': 'form-select'}),
            'patrimonio': forms.TextInput(attrs={'class': 'form-control'}), 'codigo_registro_imobiliario': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'lote': 'Lote', 'edital': 'Edital (Preenchido Automaticamente)',
            'descricao_item': 'Descrição do Item', 'quantidade': 'Quantidade',
            'unidade_medida': 'Unidade de Medida', 'valor_referencia': 'Valor de Referência Unitário',
            'fornecedor_vencedor': 'Fornecedor Vencedor', 'valor_ofertado': 'Valor Ofertado (Vencedor)',
            'numero_item_audesp': 'Número do Item (AUDESP)', 'material_ou_servico': 'Material ou Serviço (AUDESP)',
            'tipo_beneficio': 'Tipo de Benefício (AUDESP)', 'incentivo_produtivo_basico': 'Incentivo Produtivo Básico (AUDESP)?',
            'orcamento_sigiloso': 'Orçamento Sigiloso (AUDESP)?',
            'valor_unitario_estimado_audesp': 'Valor Unitário Estimado (AUDESP)',
            'valor_total_audesp': 'Valor Total (AUDESP)',
            'criterio_julgamento': 'Critério de Julgamento (AUDESP)', 'item_categoria': 'Categoria do Item (AUDESP)',
            'patrimonio': 'Código de Patrimônio (AUDESP)', 'codigo_registro_imobiliario': 'Código de Registro Imobiliário (AUDESP)',
        }

# --- Formulário para ResultadoLicitacao ---
class ResultadoLicitacaoForm(forms.ModelForm):
    class Meta:
        model = ResultadoLicitacao
        fields = [
            'lote', 'item_licitado', 'fornecedor_vencedor', 'cnpj_vencedor',
            'valor_homologado', 'data_homologacao', 'link_documento_homologacao',
            'valor_estimado_inicial'
        ]
        widgets = {
            'lote': forms.Select(attrs={'class': 'form-select'}), 'item_licitado': forms.Select(attrs={'class': 'form-select'}),
            'fornecedor_vencedor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo do fornecedor'}),
            'cnpj_vencedor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XX.XXX.XXX/XXXX-XX'}),
            'valor_homologado': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'data_homologacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'link_documento_homologacao': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'URL da ata de homologação'}),
            'valor_estimado_inicial': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
        }
        labels = {
            'lote': 'Lote', 'item_licitado': 'Item Licitado',
            'fornecedor_vencedor': 'Fornecedor Vencedor', 'cnpj_vencedor': 'CNPJ do Vencedor',
            'valor_homologado': 'Valor Homologado (R$)', 'data_homologacao': 'Data de Homologação',
            'link_documento_homologacao': 'Link Documento Homologação', 'valor_estimado_inicial': 'Valor Estimado Inicial (R$)'
        }

    def __init__(self, *args, **kwargs):
        edital_instance = kwargs.pop('edital_instance', None)
        super().__init__(*args, **kwargs)
        if edital_instance:
            self.fields['lote'].queryset = Lote.objects.filter(edital=edital_instance)
            self.fields['item_licitado'].queryset = ItemLicitado.objects.filter(Q(lote__edital=edital_instance) | Q(edital=edital_instance))
        else:
            self.fields['lote'].queryset = Lote.objects.none()
            self.fields['item_licitado'].queryset = ItemLicitado.objects.none()


class ParticipanteForm(forms.ModelForm):
    # Usamos um ModelChoiceField para criar uma lista suspensa de todos os fornecedores
    fornecedor = forms.ModelChoiceField(
        queryset=Fornecedor.objects.all().order_by('razao_social'),
        label="Selecionar Fornecedor para Credenciar"
    )

    class Meta:
        model = ParticipanteLicitacao
        fields = ['fornecedor']



# Em licitacoes/forms.py
from .models import Lance, ParticipanteLicitacao, ItemLicitado

class LanceForm(forms.ModelForm):
    class Meta:
        model = Lance
        fields = ['participante', 'item', 'valor_lance']

    def __init__(self, *args, **kwargs):
        # Pega o objeto 'pregao' que vamos passar da view
        pregao = kwargs.pop('pregao', None)
        super().__init__(*args, **kwargs)

        if pregao:
            # Filtra o campo 'participante' para mostrar apenas os do pregão atual
            self.fields['participante'].queryset = ParticipanteLicitacao.objects.filter(pregao=pregao)
            # Filtra o campo 'item' para mostrar apenas os do edital do pregão atual
            self.fields['item'].queryset = ItemLicitado.objects.filter(edital=pregao.edital)