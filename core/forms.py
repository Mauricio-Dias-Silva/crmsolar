# SysGov_Project/core/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm # Mantenha se precisar de CustomAuthenticationForm, senão pode remover
from .models import Processo , ArquivoAnexo, Fornecedor


# Formulário para a criação de um novo Processo
class ProcessoForm(forms.ModelForm):
    class Meta:
        model = Processo
        # Campos que o usuário poderá preencher no formulário
        # Excluímos 'usuario', 'status', 'data_criacao', 'data_atualizacao'
        # porque eles serão preenchidos automaticamente na view.
        fields = ['titulo', 'descricao', 'numero_protocolo']
        # Definir labels amigáveis para os campos no formulário
        labels = {
            'titulo': 'Título/Assunto do Processo',
            'descricao': 'Descrição Detalhada',
            'numero_protocolo': 'Número de Protocolo (Opcional)',
        }
        # Adicionar classes Bootstrap aos campos de entrada
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Contratação de Software X, Pedido de Licença Ambiental'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detalhe o motivo e a necessidade deste processo...'}),
            'numero_protocolo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2025/001-PMB'}),
        }

# Mantenha CustomAuthenticationForm se precisar dela para outras finalidades,
# senão você pode remover esta classe.
class CustomAuthenticationForm(AuthenticationForm):
    pass




from django import forms
from core.models import ArquivoAnexo  # ajuste o caminho se necessário

class ArquivoAnexoForm(forms.ModelForm):
    class Meta:
        model = ArquivoAnexo
        fields = ['titulo', 'arquivo']  # Apenas os campos que o usuário deve preencher
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título do anexo'}),
            'arquivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = [
            'razao_social', 'nome_fantasia', 'cnpj',
            'endereco', 'cidade', 'estado',
            'telefone', 'email', 'dados_bancarios'
        ]
        widgets = {
            'razao_social': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 2}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'dados_bancarios': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }