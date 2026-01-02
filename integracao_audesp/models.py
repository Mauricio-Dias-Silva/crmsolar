# SysGov_Project/integracao_audesp/models.py

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# --- MODELO DE CONFIGURAÇÃO (MANTIDO) ---
class AudespConfiguracao(models.Model):
    """
    Armazena configurações globais da integração com o AUDESP.
    """
    municipio_codigo_audesp = models.IntegerField(
        verbose_name="Código do Município (AUDESP)",
        help_text="Código do município conforme tabela do AUDESP/TCE-SP."
    )
    entidade_codigo_audesp = models.IntegerField(
        verbose_name="Código da Entidade (AUDESP)",
        help_text="Código da entidade ou órgão da prefeitura conforme tabela do AUDESP/TCE-SP."
    )
    class Meta:
        verbose_name = "Configuração AUDESP"
        verbose_name_plural = "Configurações AUDESP"
    def __str__(self):
        return f"Config. AUDESP - Mun: {self.municipio_codigo_audesp}, Ent: {self.entidade_codigo_audesp}"

# --- MODELO DE SUBMISSÃO (MELHORADO) ---
STATUS_SUBMISSAO_CHOICES = [
    ('PENDENTE', 'Pendente de Envio'),
    ('ENVIADO', 'Enviado, Aguardando Processamento'),
    ('ACEITO', 'Aceite pelo TCE'),
    ('REJEITADO', 'Rejeitado pelo TCE com Erros'),
    ('ERRO_ENVIO', 'Erro na Comunicação'),
]

class SubmissaoAudesp(models.Model):
    """
    Regista cada tentativa de geração ou submissão de um documento para o AUDESP.
    Usa GenericForeignKey para vincular a qualquer modelo (ETP, Contrato, etc.).
    """
    # Relação genérica para apontar para qualquer documento do sistema
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    documento_submetido = GenericForeignKey('content_type', 'object_id')

    usuario_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, null=True,
        verbose_name="Responsável pelo Envio"
    )
    data_submissao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data/Hora da Ação"
    )
    
    # Novos campos para a integração real
    status_tce = models.CharField(
        max_length=20,
        choices=STATUS_SUBMISSAO_CHOICES,
        default='PENDENTE',
        verbose_name="Status no TCE"
    )
    resposta_tce = models.TextField(
        blank=True, null=True,
        verbose_name="Resposta/Log de Erros do TCE"
    )
    protocolo_tce = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name="Número do Protocolo no TCE"
    )
    data_resposta_tce = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Data da Resposta do TCE"
    )

    class Meta:
        verbose_name = "Submissão AUDESP"
        verbose_name_plural = "Submissões AUDESP"
        ordering = ['-data_submissao']

    def __str__(self):
        # A __str__ agora mostra o novo status
        return f"Envio de {self.content_type.model} #{self.object_id} - Status: {self.get_status_tce_display()}"