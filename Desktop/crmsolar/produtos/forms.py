from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Produto
from solar.models import Cliente

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

    def clean_username(self) -> str:
        username: str = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Já existe um usuário com este nome de usuário.")
        return username

    def clean_email(self) -> str:
        email: str = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Já existe um usuário com este e-mail.")
        return email

    def clean_password2(self) -> str:
        p1: str = self.cleaned_data.get("password")
        p2: str = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("As senhas não coincidem.")
        validate_password(p1)
        return p2

    def clean_cpf(self) -> str:
        cpf: str = self.cleaned_data.get('cpf', '')
        cpf = cpf.replace('.', '').replace('-', '')
        if Cliente.objects.filter(cpf=cpf).exists():
            raise ValidationError("Já existe um cliente com esse CPF.")
        return cpf

    def clean_cnpj(self) -> str:
        cnpj: str = self.cleaned_data.get('cnpj', '')
        cnpj = cnpj.replace('.', '').replace('/', '').replace('-', '')
        if cnpj and Cliente.objects.filter(cnpj=cnpj).exists():  # Adicionado 'if cnpj' para evitar erro se campo estiver ausente
            raise ValidationError("Já existe um cliente com esse CNPJ.")
        return cnpj

    def save(self, commit: bool = True) -> User:
        cleaned: dict[str, Any] = self.cleaned_data

        user: User = User.objects.create_user(
            username=cleaned["username"],
            email=cleaned["email"],
            password=cleaned["password"],
            is_customer=True,
            is_crm_staff=False,
            is_staff=False,
            is_superuser=False,
        )

        cliente: Cliente = Cliente.objects.create(
            usuario=user,
            nome=cleaned["username"],  # Usando username como nome inicial do cliente
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
        cliente.save()  # Salva o objeto Cliente no banco de dados

        return user


class ProdutoEcommerceForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'name', 'description', 'preco', 'categoria_id',
            'stock', 'sku', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
