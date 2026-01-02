# SysGov_Project/core/models.py

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey # <<< Importação para GFK
from django.contrib.contenttypes.models import ContentType # <<< Importação para GFK

# --- Seu modelo Processo existente ---
class Processo(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    STATUS_CHOICES = [
        ('EM_ANALISE', 'Em Análise'),
        ('APROVADO', 'Aprovado'),
        ('REJEITADO', 'Rejeitado'),
        ('CONCLUIDO', 'Concluído'),
        ('AGUARDANDO_INFORMACAO', 'Aguardando Informação'),
    ]
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='EM_ANALISE',
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    numero_protocolo = models.CharField(max_length=50, unique=True, blank=True, null=True)

    class Meta:
        verbose_name = "Processo"
        verbose_name_plural = "Processos"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Processo {self.numero_protocolo or 'N/A'} - {self.titulo} ({self.get_status_display()})"


# --- NOVO MODELO: Arquivo Anexo ---
class ArquivoAnexo(models.Model):
    titulo = models.CharField(max_length=255, verbose_name="Título do Anexo")
    arquivo = models.FileField(
        upload_to='anexos_gerais/%Y/%m/%d/', # Caminho para salvar os arquivos
        verbose_name="Arquivo"
    )
    data_upload = models.DateTimeField(auto_now_add=True, verbose_name="Data de Upload")
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Enviado por"
    )

    # Campos para GFK (Generic Foreign Key) - Para anexar a qualquer modelo
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "Arquivo Anexo"
        verbose_name_plural = "Arquivos Anexos"
        ordering = ['-data_upload']

    def __str__(self):
        return self.titulo

    def get_file_extension(self):
        import os
        name, extension = os.path.splitext(self.arquivo.name)
        return extension.lower()

    def is_pdf(self):
        return self.get_file_extension() == '.pdf'

    def is_image(self):
        ext = self.get_file_extension()
        return ext in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')

    def is_xml(self):
        return self.get_file_extension() == '.xml'
    


class Fornecedor(models.Model):
    razao_social = models.CharField(
        max_length=255,
        verbose_name="Razão Social"
    )
    nome_fantasia = models.CharField(
        max_length=255,
        blank=True, null=True,
        verbose_name="Nome Fantasia"
    )
    cnpj = models.CharField(
        max_length=18, # Formato XX.XXX.XXX/XXXX-XX
        unique=True,
        verbose_name="CNPJ"
    )
    endereco = models.CharField(
        max_length=255,
        blank=True, null=True,
        verbose_name="Endereço"
    )
    cidade = models.CharField(
        max_length=100,
        blank=True, null=True
    )
    estado = models.CharField(
        max_length=2,
        blank=True, null=True,
        verbose_name="UF"
        # No futuro, podemos adicionar choices com todos os estados
    )
    telefone = models.CharField(
        max_length=20,
        blank=True, null=True
    )
    email = models.EmailField(
        blank=True, null=True,
        verbose_name="E-mail de Contato"
    )
    dados_bancarios = models.TextField(
        blank=True, null=True,
        verbose_name="Dados Bancários",
        help_text="Informações como Banco, Agência e Conta para pagamentos."
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ['razao_social']

    def __str__(self):
        return f"{self.razao_social} ({self.cnpj})"
    
    
class Notificacao(models.Model):
    usuario_destino = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notificacoes',
        verbose_name="Utilizador de Destino"
    )
    mensagem = models.CharField(
        max_length=255,
        verbose_name="Mensagem da Notificação"
    )
    link_acao = models.URLField(
        max_length=500,
        blank=True, null=True,
        verbose_name="Link para Ação"
    )
    lida = models.BooleanField(
        default=False,
        verbose_name="Lida?"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Notificação para {self.usuario_destino.username}: {self.mensagem[:30]}..."