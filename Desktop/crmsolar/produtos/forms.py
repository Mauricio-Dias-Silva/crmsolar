from django import forms
from .models import Produto # Presumindo que Produto está no mesmo app que o forms.py
from solar.models import Cliente # Presumindo que Cliente está no app 'solar'
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class CustomRegisterForm(forms.Form):
    username = forms.CharField(label='Usuário', max_length=150)
    email = forms.EmailField(label='E-mail')
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirme a Senha', widget=forms.PasswordInput)

    telefone = forms.CharField(label='Telefone')
    cpf = forms.CharField(label='CPF')
    rua = forms.CharField(label='Rua')
    numero = forms.CharField(label='Número')
    cep = forms.CharField(label='CEP')
    cidade = forms.CharField(label='Cidade')
    estado = forms.CharField(label='Estado')
    possui_whatsapp = forms.BooleanField(label='Possui WhatsApp', required=False)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Já existe um usuário com este nome de usuário.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Já existe um usuário com este e-mail.")
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get("password")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("As senhas não coincidem.")
        validate_password(p1)
        return p2

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '')
        cpf = cpf.replace('.', '').replace('-', '')
        if Cliente.objects.filter(cpf=cpf).exists():
            raise ValidationError("Já existe um cliente com esse CPF.")
        return cpf

    def clean_cnpj(self):
        # Assumindo que 'cnpj' pode ser um campo opcional no seu form,
        # ou que é tratado em outro lugar se o cliente for PJ.
        # Se este clean_method for usado, o campo 'cnpj' deve existir no form.
        cnpj = self.cleaned_data.get('cnpj', '')
        cnpj = cnpj.replace('.', '').replace('/', '').replace('-', '')
        if cnpj and Cliente.objects.filter(cnpj=cnpj).exists(): # Adicionado 'if cnpj' para evitar erro se campo estiver ausente
            raise ValidationError("Já existe um cliente com esse CNPJ.")
        return cnpj

    # --- MÉTODO SAVE CORRIGIDO ---
    def save(self, commit=True):
        cleaned = self.cleaned_data
        
        # --- CORREÇÃO AQUI ---
        # Passar os campos booleanos diretamente para create_user
        user = User.objects.create_user(
            username=cleaned["username"],
            email=cleaned["email"],
            password=cleaned["password"],
            # ATENÇÃO: Adicione esses kwargs aqui
            is_customer=True,      # Defina True diretamente
            is_crm_staff=False,    # Defina False diretamente
            is_staff=False,        # Defina False
            is_superuser=False,    # Defina False
        )

        cliente = Cliente.objects.create(
            usuario=user,
            nome=cleaned["username"], # Usando username como nome inicial do cliente
            email=cleaned["email"],
            telefone=cleaned["telefone"],
            cpf=cleaned["cpf"],
            possui_whatsapp=cleaned["possui_whatsapp"],
            rua=cleaned["rua"],
            numero=cleaned["numero"],
            cep=cleaned["cep"],
            cidade=cleaned["cidade"],
            estado=cleaned["estado"],
        )
        cliente.save() # Salva o objeto Cliente no banco de dados

        return user # Retorna o objeto User criado
# --- FIM DO MÉTODO SAVE CORRIGIDO ---
        
# Formulário para Adicionar Produtos (Este estava correto)
class ProdutoEcommerceForm(forms.ModelForm):
    # O campo de imagens será tratado diretamente na view
    
    class Meta:
        model = Produto
        fields = [
            'name', 'description', 'preco', 'categoria_id',
            'stock', 'sku', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }