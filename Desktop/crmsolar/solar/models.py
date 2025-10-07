import re
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings

# --- VALIDADORES ---
def validar_cnpj(cnpj):
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) != 14:
        raise ValidationError("CNPJ inválido. Deve conter 14 dígitos numéricos.")
    return cnpj

def validar_telefone(telefone):
    telefone = re.sub(r'[^0-9]', '', telefone)
    if len(telefone) < 10 or len(telefone) > 11:
        raise ValidationError("Telefone inválido. Deve conter 10 ou 11 dígitos.")
    return telefone

def validar_cpf(cpf):
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) != 11:
        raise ValidationError("CPF inválido. Deve conter 11 dígitos numéricos.")
    return cpf

# --- DEPARTAMENTO E MENU ---
class Departamento(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nome

class MenuPermissao(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    rota = models.CharField(max_length=100, help_text="Exemplo: /clientes/ ou nome da URL Django")
    def __str__(self):
        return self.nome

# --- USUARIO ---
class Usuario(AbstractUser):
    departamento = models.ForeignKey('Departamento', on_delete=models.SET_NULL, null=True, blank=True)
    permissoes_menu = models.ManyToManyField('MenuPermissao', blank=True, related_name='usuarios_com_permissao_menu')
    
    is_crm_staff = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group, blank=True, related_name="solar_usuario_set", related_query_name="solar_usuario"
    )
    user_permissions = models.ManyToManyField(
        Permission, blank=True, related_name="solar_user_permissions_set", related_query_name="solar_user_permission"
    )

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def pode_acessar_crm(self):
        return self.is_active and (self.is_staff or self.is_superuser or self.is_crm_staff)

    @property
    def pode_acessar_ecommerce(self):
        return self.is_active and (self.is_customer or self.is_crm_staff or self.is_superuser)

# --- CLIENTE ---
class Cliente(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='perfil_cliente')
    nome = models.CharField(max_length=200)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    rua = models.CharField(max_length=200, null=True, blank=True)
    numero = models.CharField(max_length=20, null=True, blank=True)
    bairro = models.CharField(max_length=100, null=True, blank=True)
    cep = models.CharField(max_length=10, null=True, blank=True)
    cidade = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=2, null=True, blank=True)
    cnpj = models.CharField(max_length=18, unique=True, null=True, blank=True)
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    possui_whatsapp = models.BooleanField(default=False)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

# --- PROJETO ---
class Projeto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[
        ('Em andamento', 'Em andamento'), 
        ('Concluído', 'Concluído'),
        ('Aguardando aprovação', 'Aguardando aprovação'),
        ('Cancelado', 'Cancelado'),
        ('Pendente Orçamento', 'Pendente Orçamento'),
        ('Em Instalação', 'Em Instalação'),
        ('Manutenção', 'Manutenção'),
        ('Homologado', 'Homologado'),
        ('Proposta Enviada', 'Proposta Enviada'),
    ])
    cliente = models.ForeignKey('Cliente', on_delete=models.SET_NULL, null=True, blank=True)
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='projetos_responsavel')
    rua = models.CharField(max_length=200, null=True, blank=True)
    numero = models.CharField(max_length=20, null=True, blank=True)
    bairro = models.CharField(max_length=100, null=True, blank=True)
    cidade = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=2, null=True, blank=True)
    cep = models.CharField(max_length=10, null=True, blank=True)
    potencia_kwp = models.DecimalField('Potência (kWp)', max_digits=6, decimal_places=2, null=True, blank=True)
    quantidade_modulos = models.PositiveIntegerField('Quantidade de Módulos', null=True, blank=True)
    inversor = models.CharField('Modelo do Inversor', max_length=100, blank=True, null=True)
    fornecedor = models.ForeignKey('Fornecedor', on_delete=models.SET_NULL, null=True, blank=True)
    valor_total = models.DecimalField('Valor Total (R$)', max_digits=12, decimal_places=2, null=True, blank=True)
    forma_pagamento = models.CharField('Forma de Pagamento', max_length=100, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    irradiacao_media_diaria = models.DecimalField(
        max_digits=5, decimal_places=3, null=True, blank=True, 
        help_text="Média diária de irradiação (kWh/m²/dia)."
    )

    def __str__(self):
        return self.nome



class DocumentoProjeto(models.Model):
    projeto = models.ForeignKey('Projeto', on_delete=models.CASCADE, related_name='documentos')
    nome = models.CharField('Nome do Documento', max_length=200)
    arquivo = models.FileField('Arquivo', upload_to='projetos/%Y/%m/%d/')
    data_upload = models.DateTimeField(auto_now_add=True)
    visivel_cliente = models.BooleanField('Visível para o cliente?', default=False)

    def __str__(self):
        return f'{self.nome} ({self.projeto.nome})'
    
class Etapa(models.Model):
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='etapas')
    nome = models.CharField(max_length=100)
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    descricao = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[ # Adicionado
        ('concluida', 'Concluída'),
        ('em_andamento', 'Em Andamento'),
        ('pendente', 'Pendente'),
        ('atrasada', 'Atrasada')
    ], default='pendente')

    def __str__(self):
        return f'{self.nome} ({self.projeto.nome})'

class Material(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50, blank=True, null=True)
    fabricante = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=50, blank=True, null=True)
    numero_serie = models.CharField(max_length=50, blank=True, null=True)
    unidade_medida = models.CharField(max_length=20)
    quantidade_estoque = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estoque_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    localizacao = models.CharField(max_length=100, blank=True, null=True)
    preco_compra = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    garantia_ate = models.DateField(blank=True, null=True)
    data_entrada = models.DateField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    fornecedor = models.ForeignKey('Fornecedor', on_delete=models.SET_NULL, null=True, blank=True)
    peso = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.nome

class Fornecedor(models.Model):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18, unique=True, validators=[validar_cnpj]) # Adicionado unique=True
    telefone = models.CharField(max_length=20, validators=[validar_telefone])
    email = models.EmailField(blank=True)
    endereco = models.TextField(blank=True)

    def __str__(self):
        return self.nome

class LancamentoFinanceiro(models.Model):
    TIPOS = [
        ('recebimento', 'Recebimento'),
        ('pagamento', 'Pagamento'),
    ]
    STATUS = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('atrasado', 'Atrasado'), # Adicionado
        ('cancelado', 'Cancelado'), # Adicionado
    ]

    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='lancamentos')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS)

    def __str__(self):
        return f'{self.tipo.title()} - {self.valor} ({self.projeto.nome})'




class Financeiro(models.Model):
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    # Add other fields here as needed


# =========================================================
# MODELOS DE SERVIÇO (Movidos do app 'produtos')
# =========================================================

class Proposta(models.Model):
    # MOCK para Rastreamento de Proposta (Funcionalidade 1)
    numero = models.CharField(max_length=10, unique=True)
    cliente_nome = models.CharField(max_length=150)
    cpf_cnpj = models.CharField(max_length=18)
    vendedor = models.CharField(max_length=100)
    potencia_kwp = models.DecimalField(max_digits=5, decimal_places=2)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    STATUS_CHOICES = [
        ('1_ACEITE', '1. Aguardando Aceite'),
        ('2_PROJETO', '2. Em Elaboração de Projeto'),
        ('3_HOMOLOG', '3. Em Homologação na Concessionária'),
        ('4_INSTAL', '4. Instalação Agendada'),
        ('5_FINALIZADO', '5. Sistema Ativo'),
    ]
    status_crm = models.CharField(max_length=20, choices=STATUS_CHOICES, default='1_ACEITE')
    data_validade = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Proposta {self.numero} - {self.cliente_nome}"

    class Meta:
        verbose_name = "Proposta de Cliente"
        verbose_name_plural = "Propostas de Clientes"


class ProjetoExecutado(models.Model):
    # Modelo para o Portfólio de Projetos (Funcionalidade 3)
    titulo = models.CharField(max_length=200, help_text="Ex: Projeto Residencial em Sorocaba")
    potencia_kwp = models.DecimalField(max_digits=5, decimal_places=2)
    localidade = models.CharField(max_length=100)
    tipo_projeto = models.CharField(max_length=20, choices=[('RES', 'Residencial'), ('COM', 'Comercial'), ('IND', 'Industrial')])
    imagem_capa = models.ImageField(upload_to='projetos_portfolio/', help_text="Imagem de alta resolução do projeto instalado")
    is_active = models.BooleanField(default=True, verbose_name="Ativo no Site")
    
    def __str__(self):
        return f"{self.titulo} ({self.potencia_kwp} kWp)"

    class Meta:
        verbose_name = "Projeto Executado"
        verbose_name_plural = "Projetos Executados"
        ordering = ['-potencia_kwp']

