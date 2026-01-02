# SysGov_Project/licitacoes/models.py

from django.db import models
from django.conf import settings
from core.models import Processo # Importa o modelo Processo do app 'core'
from decimal import Decimal # Para campos decimais
from core.models import Fornecedor

User = settings.AUTH_USER_MODEL

STATUS_EDITAL_CHOICES = [
    ('EM_ELABORACAO', 'Em Elaboração'),
    ('PUBLICADO', 'Publicado'),
    ('ABERTO', 'Aberto para Propostas'),
    ('ENCERRADO', 'Encerrado'),
    ('HOMOLOGADO', 'Homologado'),
    ('CANCELADO', 'Cancelado'),
    ('FRACASSADO', 'Fracassado'),
]

# --- CHOICES para os ENUMS do AUDESP (os que já estavam definidos aqui) ---
TIPO_INSTRUMENTO_CONVOCATORIO_CHOICES = [
    (1, 'Edital'), (2, 'Convite'), (3, 'Dispensa'), (4, 'Inexigibilidade'), (5, 'Outros'),
]

MODALIDADE_LICITACAO_CHOICES = [
    (1, 'Pregão Eletrônico'), (2, 'Concorrência'), (3, 'Tomada de Preços'), (4, 'Convite'),
    (5, 'Concurso'), (6, 'Leilão'), (7, 'Pregão Presencial'), (8, 'Dispensa de Licitação'),
    (9, 'Inexigibilidade de Licitação'), (10, 'Concorrência Eletrônica'), (11, 'Diálogo Competitivo'),
    (12, 'Credenciamento'), (13, 'Procedimento de Manifestação de Interesse (PMI)'),
    (997, 'Outras Modalidades (Lei 8.666/93)'), (998, 'Outras Modalidades (Lei 14.133/21)'),
    (999, 'Não se aplica (Outros Ajustes)'), (1000, 'Concessão'), (1001, 'Permissão'),
    (1002, 'Autorização'), (1003, 'Termo de Permissão de Uso (TPU)'), (1004, 'Termo de Concessão de Uso (TCU)'),
    (1005, 'Termo de Colaboração'), (1006, 'Termo de Fomento'), (1007, 'Acordo de Cooperação'),
    (1008, 'Contrato de Gestão'), (1009, 'Convênio'), (1010, 'Termo de Parceria'),
    (1011, 'Ata de Registro de Preços'), (1012, 'Contrato de Adesão'), (1013, 'Contrato de Obra'),
    (1014, 'Contrato de Serviço'), (1015, 'Contrato de Fornecimento'), (1016, 'Contrato de Locação'),
    (1017, 'Contrato de Concessão de Direito Real de Uso'), (1018, 'Contrato de Concessão de Serviço Público'),
    (1019, 'Contrato de Permissão de Serviço Público'), (1020, 'Contrato de Parceria Público-Privada (PPP)'),
]

MODO_DISPUTA_CHOICES = [
    (1, 'Aberto'), (2, 'Fechado'), (3, 'Aberto e Fechado'), (4, 'Lances Intermediários'),
    (5, 'Lances Sucessivos'), (6, 'Não se aplica'),
]

VEICULO_PUBLICACAO_CHOICES = [
    (1, 'Diário Oficial do Município'), (2, 'Diário Oficial do Estado'), (3, 'Jornal de Grande Circulação'),
    (4, 'Portal da Transparência'), (5, 'PNCP'), (6, 'Site Oficial do Órgão'), (7, 'Boletim Interno'),
    (8, 'Quadro de Avisos'), (9, 'Mídias Sociais'), (10, 'Outros'),
]

TIPO_BENEFICIO_CHOICES = [
    (1, 'Microempresa (ME) / Empresa de Pequeno Porte (EPP)'), (2, 'Cooperativa'),
    (3, 'Empresa de Economia Solidária'), (4, 'Não se aplica'), (5, 'Outros'),
]

CRITERIO_JULGAMENTO_CHOICES = [
    (1, 'Menor Preço'), (2, 'Melhor Técnica'), (3, 'Melhor Técnica e Preço'), (4, 'Maior Lance ou Oferta'),
    (5, 'Maior Retorno Econômico'), (6, 'Maior Desconto'), (7, 'Preço Global'), (8, 'Preço por Item'),
    (9, 'Preço por Lote'), (10, 'Melhor Conteúdo Artístico'), (1000, 'Não se aplica (Dispensa/Inexigibilidade)'), (1001, 'Outros'),
]

ITEM_CATEGORIA_CHOICES = [
    (1, 'Bens Imóveis'), (2, 'Bens Móveis'), (3, 'Não se aplica'),
]


# Modelo para o Edital de Licitação (ADAPTADO PARA AUDESP)
class Edital(models.Model): # Mantém o nome 'Edital' para compatibilidade com o código existente
    processo_vinculado = models.OneToOneField(
        Processo,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='edital_licitacao',
        verbose_name="Processo Licitatório Principal"
    )

    # Campos existentes (adaptados)
    numero_edital = models.CharField(max_length=50, unique=True, verbose_name="Número do Edital")
    titulo = models.CharField(max_length=255, verbose_name="Objeto da Licitação")
    tipo_licitacao = models.CharField( # Este campo pode ser mapeado para 'modalidade' ou 'tipo_instrumento_convocatorio'
        max_length=50,
        choices=[('PREGAO_ELETRONICO', 'Pregão Eletrônico'), ('CONCORRENCIA', 'Concorrência'), ('TOMADA_PRECOS', 'Tomada de Preços')],
        default='PREGAO_ELETRONICO',
        verbose_name="Tipo de Licitação"
    )
    data_publicacao = models.DateField(verbose_name="Data de Publicação")
    data_abertura_propostas = models.DateTimeField(verbose_name="Data/Hora Abertura Propostas")
    local_abertura = models.CharField(max_length=255, verbose_name="Local de Abertura", blank=True, null=True)
    link_edital_completo = models.URLField(verbose_name="Link para Edital Completo", blank=True, null=True, help_text="URL onde o edital pode ser baixado (ex: portal da transparência).")
    valor_estimado = models.DecimalField(max_digits=17, decimal_places=2, verbose_name="Valor Estimado", blank=True, null=True)

    status = models.CharField(
        max_length=30,
        choices=STATUS_EDITAL_CHOICES,
        default='EM_ELABORACAO',
        verbose_name="Status do Edital"
    )
    responsavel_publicacao = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Responsável pela Publicação"
    )
    data_ultima_atualizacao = models.DateTimeField(auto_now=True)

    arquivo_edital = models.FileField(
        upload_to='editais/%Y/%m/',
        verbose_name="Arquivo PDF do Edital",
        help_text="O arquivo PDF original do edital para ser enviado à Audesp.",
        null=True,  # Permite que registros antigos não tenham um arquivo
        blank=True  # Torna o campo opcional no formulário
    )
    
    # --- NOVOS CAMPOS ADAPTADOS DO JSON SCHEMA DO AUDESP (versão inicial do Edital) ---
    retificacao = models.BooleanField(
        default=False,
        verbose_name="É Retificação (AUDESP)?",
        help_text="Indica se este Edital é uma retificação de um anterior para o AUDESP."
    )

    codigo_unidade_compradora = models.CharField(
        max_length=20,
        blank=True, null=True,
        verbose_name="Código Unidade Compradora (AUDESP)",
        help_text="Código da unidade que está realizando a compra para o AUDESP."
    )
    tipo_instrumento_convocatorio_audesp = models.IntegerField(
        choices=TIPO_INSTRUMENTO_CONVOCATORIO_CHOICES,
        null=True, blank=True,
        verbose_name="Tipo Instrumento Convocatório (AUDESP)"
    )
    modalidade_audesp = models.IntegerField(
        choices=MODALIDADE_LICITACAO_CHOICES,
        null=True, blank=True,
        verbose_name="Modalidade (AUDESP)"
    )
    modo_disputa = models.IntegerField(
        choices=MODO_DISPUTA_CHOICES,
        null=True, blank=True,
        verbose_name="Modo de Disputa (AUDESP)"
    )
    numero_compra_audesp = models.CharField(
        max_length=50,
        blank=True, null=True,
        verbose_name="Número da Compra (AUDESP)",
        help_text="Número da contratação no sistema de origem para o AUDESP."
    )
    ano_compra_audesp = models.IntegerField(
        null=True, blank=True,
        verbose_name="Ano da Compra (AUDESP)"
    )
    numero_processo_origem_audesp = models.CharField(
        max_length=50,
        blank=True, null=True,
        verbose_name="Número Processo Origem (AUDESP)",
        help_text="Número do processo administrativo no sistema de origem para o AUDESP."
    )
    objeto_compra_audesp = models.TextField(
        max_length=5120,
        blank=True, null=True,
        verbose_name="Objeto da Compra (AUDESP)",
        help_text="Objeto da contratação para o AUDESP."
    )
    informacao_complementar = models.TextField(
        max_length=5120,
        blank=True, null=True,
        verbose_name="Informações Complementares"
    )
    srp = models.BooleanField(
        default=False,
        verbose_name="Sistema de Registro de Preços (SRP) (AUDESP)?"
    )
    data_encerramento_proposta = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Data e Hora Encerramento Proposta (AUDESP)"
    )
    amparo_legal = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 1021)],
        null=True, blank=True,
        verbose_name="Amparo Legal (AUDESP)"
    )
    link_sistema_origem = models.URLField(
        max_length=500,
        blank=True, null=True,
        verbose_name="Link Sistema de Origem (AUDESP)"
    )
    justificativa_presencial = models.TextField(
        max_length=500,
        blank=True, null=True,
        verbose_name="Justificativa Presencial (AUDESP)"
    )

    class Meta:
        verbose_name = "Edital de Licitação"
        verbose_name_plural = "Editais de Licitação"
        ordering = ['-data_publicacao']

    def __str__(self):
        return f"Edital {self.numero_edital} - {self.titulo}"

# Modelo para Lotes dentro de um Edital
class Lote(models.Model):
    edital = models.ForeignKey(Edital, on_delete=models.CASCADE, related_name='lotes', verbose_name="Edital")
    numero_lote = models.CharField(max_length=10, verbose_name="Número do Lote")
    descricao = models.TextField(verbose_name="Descrição do Lote")
    valor_estimado_lote = models.DecimalField(max_digits=17, decimal_places=2, verbose_name="Valor Estimado do Lote", blank=True, null=True)

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"
        unique_together = ('edital', 'numero_lote')

    def __str__(self):
        return f"Lote {self.numero_lote} - {self.edital.numero_edital}"

# Modelo para Itens dentro de um Lote (ou diretamente no Edital se não tiver lote)
class ItemLicitado(models.Model):
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name='itens', verbose_name="Lote", blank=True, null=True)
    edital = models.ForeignKey(Edital, on_delete=models.CASCADE, related_name='itens_diretos', verbose_name="Edital", blank=True, null=True)

    # Campos existentes
    descricao_item = models.TextField(verbose_name="Descrição do Item")
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantidade")
    unidade_medida = models.CharField(max_length=50, verbose_name="Unidade de Medida")
    valor_referencia = models.DecimalField(max_digits=17, decimal_places=2, verbose_name="Valor de Referência Unitário", blank=True, null=True)
    fornecedor_vencedor = models.CharField(max_length=255, verbose_name="Fornecedor Vencedor", blank=True, null=True)
    valor_ofertado = models.DecimalField(max_digits=17, decimal_places=2, verbose_name="Valor Ofertado (Vencedor)", blank=True, null=True)

    # --- NOVOS CAMPOS ADAPTADOS DO JSON SCHEMA DO AUDESP (itensCompra) ---
    numero_item_audesp = models.IntegerField(
        null=True, blank=True,
        verbose_name="Número do Item (AUDESP)",
        help_text="Número sequencial do item na contratação para o AUDESP."
    )
    material_ou_servico = models.CharField(
        max_length=1,
        choices=[('M', 'Material'), ('S', 'Serviço')],
        null=True, blank=True,
        verbose_name="Material ou Serviço (AUDESP)"
    )
    tipo_beneficio = models.IntegerField(
        choices=TIPO_BENEFICIO_CHOICES,
        null=True, blank=True,
        verbose_name="Tipo de Benefício (AUDESP)"
    )
    incentivo_produtivo_basico = models.BooleanField(
        default=False,
        verbose_name="Incentivo Produtivo Básico (PPB) (AUDESP)?"
    )
    orcamento_sigiloso = models.BooleanField(
        default=False,
        verbose_name="Orçamento Sigiloso (AUDESP)?"
    )
    valor_unitario_estimado_audesp = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        null=True, blank=True,
        verbose_name="Valor Unitário Estimado (AUDESP) (R$)"
    )
    valor_total_audesp = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        null=True, blank=True,
        verbose_name="Valor Total (AUDESP) (R$)"
    )
    criterio_julgamento = models.IntegerField(
        choices=CRITERIO_JULGAMENTO_CHOICES,
        null=True, blank=True,
        verbose_name="Critério de Julgamento (AUDESP)"
    )
    item_categoria = models.IntegerField(
        choices=ITEM_CATEGORIA_CHOICES,
        null=True, blank=True,
        verbose_name="Categoria do Item (AUDESP)"
    )
    patrimonio = models.CharField(
        max_length=255,
        blank=True, null=True,
        verbose_name="Código de Patrimônio (AUDESP)"
    )
    codigo_registro_imobiliario = models.CharField(
        max_length=255,
        blank=True, null=True,
        verbose_name="Código de Registro Imobiliário (AUDESP)"
    )

    class Meta:
        verbose_name = "Item Licitado"
        verbose_name_plural = "Itens Licitados"

    def __str__(self):
        return f"Item: {self.descricao_item[:50]} ({self.unidade_medida})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


# Modelo para o Resultado da Licitação (um Edital pode ter um ou mais resultados, por lote ou geral)
class ResultadoLicitacao(models.Model):
    edital = models.ForeignKey(
        Edital,
        on_delete=models.CASCADE,
        related_name='resultados',
        verbose_name="Edital Vinculado"
    )
    lote = models.ForeignKey(
        Lote,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='resultados_lote',
        verbose_name="Lote (se aplicável)"
    )
    item_licitado = models.ForeignKey(
        ItemLicitado,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='resultados_item',
        verbose_name="Item Licitado (se aplicável)"
    )

    fornecedor_vencedor = models.CharField(max_length=255, verbose_name="Fornecedor Vencedor")
    cnpj_vencedor = models.CharField(max_length=18, blank=True, null=True, verbose_name="CNPJ do Vencedor")
    valor_homologado = models.DecimalField(max_digits=17, decimal_places=2, verbose_name="Valor Homologado (R$)")
    data_homologacao = models.DateField(verbose_name="Data de Homologação")

    link_documento_homologacao = models.URLField(verbose_name="Link Documento Homologação", blank=True, null=True)

    valor_estimado_inicial = models.DecimalField(max_digits=17, decimal_places=2, verbose_name="Valor Estimado Inicial (R$)", blank=True, null=True)
    economia_gerada = models.DecimalField(max_digits=17, decimal_places=2, verbose_name="Economia Gerada (R$)", blank=True, null=True, editable=False)

    responsavel_registro = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Responsável pelo Registro"
    )
    data_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Resultado da Licitação"
        verbose_name_plural = "Resultados das Licitações"
        ordering = ['-data_homologacao']
        unique_together = ('edital', 'lote', 'item_licitado')

    def __str__(self):
        return f"Resultado Edital {self.edital.numero_edital} - {self.fornecedor_vencedor}"

    def save(self, *args, **kwargs):
        if self.valor_estimado_inicial and self.valor_homologado:
            self.economia_gerada = self.valor_estimado_inicial - self.valor_homologado
        super().save(*args, **kwargs)



STATUS_PREGAO_CHOICES = [
    ('AGENDADO', 'Agendado'),
    ('ABERTO_PARA_LANCES', 'Aberto para Lances'),
    ('EM_DISPUTA', 'Em Disputa'),
    ('FINALIZADO', 'Finalizado'),
    ('SUSPENSO', 'Suspenso'),
    ('CANCELADO', 'Cancelado'),
]

class Pregao(models.Model):
    edital = models.OneToOneField(
        Edital,
        on_delete=models.CASCADE,
        related_name='pregao',
        verbose_name="Edital de Referência"
    )
    pregoeiro = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='pregoes_conduzidos',
        verbose_name="Pregoeiro Responsável"
    )
    data_abertura_sessao = models.DateTimeField(
        verbose_name="Data e Hora de Abertura da Sessão"
    )
    data_encerramento_sessao = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Data e Hora de Encerramento"
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_PREGAO_CHOICES,
        default='AGENDADO',
        verbose_name="Status da Sessão"
    )
    observacoes = models.TextField(
        blank=True, null=True,
        verbose_name="Observações e Ata da Sessão"
    )

    class Meta:
        verbose_name = "Pregão (Sessão de Disputa)"
        verbose_name_plural = "Pregões (Sessões de Disputa)"
        ordering = ['-data_abertura_sessao']

    def __str__(self):
        return f"Pregão do Edital {self.edital.numero_edital} - Status: {self.get_status_display()}"
    


class ParticipanteLicitacao(models.Model):
    pregao = models.ForeignKey(
        Pregao,
        on_delete=models.CASCADE,
        related_name='participantes',
        verbose_name="Pregão"
    )
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.CASCADE,
        related_name='participacoes',
        verbose_name="Fornecedor Licitante"
    )
    data_credenciamento = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Credenciamento"
    )
    desclassificado = models.BooleanField(
        default=False,
        verbose_name="Desclassificado?"
    )
    motivo_desclassificacao = models.TextField(
        blank=True, null=True,
        verbose_name="Motivo da Desclassificação"
    )

    class Meta:
        verbose_name = "Participante da Licitação"
        verbose_name_plural = "Participantes da Licitação"
        # Garante que um fornecedor só possa se inscrever uma vez por pregão
        unique_together = ('pregao', 'fornecedor')
        ordering = ['data_credenciamento']

    def __str__(self):
        return f"{self.fornecedor.razao_social} no Pregão do Edital {self.pregao.edital.numero_edital}"
    



class Lance(models.Model):
    participante = models.ForeignKey(
        ParticipanteLicitacao,
        on_delete=models.CASCADE,
        related_name='lances',
        verbose_name="Participante"
    )
    item = models.ForeignKey(
        ItemLicitado,
        on_delete=models.CASCADE,
        related_name='lances',
        verbose_name="Item do Edital"
    )
    valor_lance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Valor do Lance"
    )
    data_lance = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data e Hora do Lance"
    )
    aceito = models.BooleanField(
        default=False,
        verbose_name="Lance Vencedor?"
    )

    class Meta:
        verbose_name = "Lance"
        verbose_name_plural = "Lances"
        ordering = ['item', 'valor_lance'] # Ordena por item e depois pelo menor valor

    def __str__(self):
        return f"Lance de R$ {self.valor_lance} para o item '{self.item.descricao_item}'"