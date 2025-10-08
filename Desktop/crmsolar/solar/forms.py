from django import forms
# 💡 IMPORT NECESSÁRIO PARA O FORMSET
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import (
    Usuario, Cliente, Projeto, Etapa, Material, Fornecedor,
    LancamentoFinanceiro, DocumentoProjeto, Departamento, MenuPermissao,
    # 💡 IMPORT DO NOSSO NOVO MODELO
    ItemProposta
)
from produtos.models import Produto
import re

User = get_user_model()


# Lista oficial de estados do Brasil (mantida)
ESTADOS_BRASIL = [
    ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
    ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
    ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'),
]

# --- SEUS FORMULÁRIOS EXISTENTES (Mantidos 100%) ---

class ProjetoForm(forms.ModelForm):
    # Seu ProjetoForm está ótimo e completo, vamos mantê-lo.
    # Ele será o formulário principal na nossa nova tela.
    data_inicio = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        required=False
    )
    data_fim = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        required=False
    )
    estado = forms.ChoiceField(
        choices=ESTADOS_BRASIL,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Projeto
        fields = '__all__'
        exclude = ['latitude', 'longitude', 'inclinacao_telhado', 'azimute_telhado']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cidade'].required = True
        for fname, field in self.fields.items():
            if fname not in ['data_inicio', 'data_fim']:
                if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.Textarea, forms.Select)):
                    field.widget.attrs.setdefault('class', 'form-control')
                elif isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs.setdefault('class', 'form-check-input')


# --- 💡 A GRANDE NOVIDADE: O FORMSET PARA O ORÇAMENTO ---
# Este é o "sub-formulário" que permitirá adicionar múltiplos itens ao projeto.

ItemPropostaFormSet = inlineformset_factory(
    Projeto,                  # O modelo "pai"
    ItemProposta,             # O modelo "filho" que queremos adicionar várias vezes
    fields=('descricao', 'unidade', 'quantidade', 'valor_unitario'), # Os campos que aparecerão na tela
    extra=1,                  # Começa mostrando 1 linha de item vazia
    can_delete=True,          # Permite ao usuário marcar itens para deletar
    widgets={                 # Estilização para deixar bonito
        'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição do Equipamento/Serviço'}),
        'unidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'unid.'}),
        'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Qtd'}),
        'valor_unitario': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor Unit. R$'}),
    }
)




class ClienteForm(forms.ModelForm):
    # (Seu ClienteForm... sem alterações)
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'telefone': forms.TextInput(attrs={'placeholder': '(XX) XXXX-XXXX ou (XX) 9XXXX-XXXX'}),
            'cnpj': forms.TextInput(attrs={'placeholder': 'Apenas dígitos'}),
            'cpf': forms.TextInput(attrs={'placeholder': 'Apenas dígitos'}),
            'possui_whatsapp': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            cpf_limpo = re.sub(r'[^0-9]', '', cpf)
            if len(cpf_limpo) != 11:
                raise forms.ValidationError("CPF inválido. Deve conter 11 dígitos numéricos.")
            return cpf_limpo  # ← retorna o valor limpo
        return None  # ← se vazio, salva como None

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        if cnpj:
            cnpj_limpo = re.sub(r'[^0-9]', '', cnpj)
            if len(cnpj_limpo) != 14:
                raise forms.ValidationError("CNPJ inválido. Deve conter 14 dígitos numéricos.")
            return cnpj_limpo
        return None

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            tel_limpo = re.sub(r'[^0-9]', '', telefone)
            if len(tel_limpo) not in [10, 11]:
                raise forms.ValidationError("Telefone inválido. Deve ter 10 ou 11 dígitos.")
            return tel_limpo
        return None

    def clean(self):
        cleaned_data = super().clean()
        cpf = cleaned_data.get('cpf')
        cnpj = cleaned_data.get('cnpj')

        if not cpf and not cnpj:
            raise forms.ValidationError("É necessário informar CPF ou CNPJ.")

        if cpf and cnpj:
            raise forms.ValidationError("Informe apenas CPF ou CNPJ, não ambos.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fname, field in self.fields.items():
            if fname != 'possui_whatsapp':
                if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.Textarea, forms.EmailInput, forms.Select)):
                    field.widget.attrs.update({'class': 'form-control'})



class EtapaForm(forms.ModelForm):
    class Meta:
        model = Etapa
        # CORREÇÃO 1: Trocamos 'fields' por 'exclude'
        exclude = ['projeto']
        
        # Seus widgets continuam perfeitos
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # CORREÇÃO 2: Adicionamos estas duas linhas para as datas
        self.fields['data_inicio'].input_formats = ['%d/%m/%Y', '%Y-%m-%d']
        self.fields['data_fim'].input_formats = ['%d/%m/%Y', '%Y-%m-%d']
        
        # Seu loop para as classes CSS continua perfeito
        for fname, field in self.fields.items():
            if fname not in ['data_inicio', 'data_fim', 'descricao']:
                if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.Select)):
                    field.widget.attrs.update({'class': 'form-control'})


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = '__all__'
        widgets = {
            'garantia_ate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_entrada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fname, field in self.fields.items():
            if fname not in ['garantia_ate', 'data_entrada', 'observacoes']:
                if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.Textarea, forms.Select)):
                    field.widget.attrs.update({'class': 'form-control'})

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = '__all__'
        widgets = {
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apenas dígitos'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXX-XXXX ou (XX) 9XXXX-XXXX'}),
            'endereco': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fname, field in self.fields.items():
            if fname not in ['endereco']:
                if isinstance(field.widget, (forms.TextInput, forms.EmailInput, forms.NumberInput, forms.Select)):
                    field.widget.attrs.update({'class': 'form-control'})

class LancamentoFinanceiroForm(forms.ModelForm):
    class Meta:
        model = LancamentoFinanceiro
        fields = '__all__'
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fname, field in self.fields.items():
            if fname != 'data':
                if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.Select)):
                    field.widget.attrs.update({'class': 'form-control'})
                if isinstance(field.widget, forms.Select):
                    field.widget.attrs.update({'class': 'form-select'})

class DocumentoProjetoForm(forms.ModelForm):
    class Meta:
        model = DocumentoProjeto
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control'}),
            'visivel_cliente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fname, field in self.fields.items():
            if fname != 'visivel_cliente':
                if isinstance(field.widget, (forms.TextInput, forms.FileInput)):
                    field.widget.attrs.update({'class': 'form-control'})


User = get_user_model()

class UsuarioCreateForm(forms.ModelForm):
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirme a Senha', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'departamento', 'permissoes_menu', 'is_crm_staff', 'is_customer'
        )
        widgets = {
            'departamento': forms.Select(attrs={'class': 'form-select'}),
            'permissoes_menu': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("As senhas não coincidem.")
        # Validar complexidade da senha sem passar self.instance
        if p1:
            try:
                validate_password(p1)  # <-- não passar self.instance
            except ValidationError as e:
                raise forms.ValidationError(e)
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            self.save_m2m()  # salva ManyToMany
        return user


class UsuarioUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'departamento', 'is_crm_staff', 'is_customer')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.Select(attrs={'class': 'form-select'}),
            'is_crm_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_customer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# --- Form para Ecommerce ---
class ProdutoEcommerceForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'name', 'description', 'preco', 'categoria_id', 'stock', 'sku',
            'is_active', 'peso', 'dimensoes', 'garantia'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'preco': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria_id': forms.TextInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control'}),
            'dimensoes': forms.TextInput(attrs={'class': 'form-control'}),
            'garantia': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fname, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                if not isinstance(field.widget, forms.Select):
                    field.widget.attrs.update({'class': 'form-control'})
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})

# --- Form Perfil Cliente ---
class PerfilClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'email', 'telefone', 'rua', 'numero', 'cep', 'cidade', 'estado', 'cnpj', 'cpf', 'possui_whatsapp']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo ou Razão Social'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seuemail@exemplo.com'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXX-XXXX ou (XX) 9XXXX-XXXX'}),
            'rua': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Rua, Avenida, etc.'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXXXX-XXX'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UF (ex: SP)'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apenas dígitos'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apenas dígitos'}),
            'possui_whatsapp': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fname, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})

       