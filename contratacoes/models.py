# SysGov_Project/contratacoes/models.py

from django.db import models
from django.conf import settings # Para referenciar o modelo de usuário do Django
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from core.models import Processo, ArquivoAnexo, Fornecedor
from licitacoes.models import Edital
# --- Definição dos status possíveis para documentos ---
STATUS_DOCUMENTO_CHOICES = [
    ('EM_ELABORACAO', 'Em Elaboração'),
    ('AGUARDANDO_REVISAO', 'Aguardando Revisão'),
    ('REVISADO', 'Revisado'),
    ('APROVADO', 'Aprovado'),
    ('RECUSADO', 'Recusado'),
    ('CANCELADO', 'Cancelado'),
]

class ETP(models.Model):
    processo_vinculado = models.OneToOneField(
        Processo,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='etp_documento',
        verbose_name="Processo Principal (ProGestor Público)"
    )

    titulo = models.CharField(
        max_length=255,
        verbose_name="Título do ETP",
        help_text="Título descritivo do Estudo Técnico Preliminar."
    )

    numero_processo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Número do Processo SEI/Interno",
        help_text="Número do processo administrativo relacionado a este ETP."
    )

    data_criacao = models.DateField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    data_ultima_atualizacao = models.DateTimeField(auto_now=True)

    setor_demandante = models.CharField(
        max_length=100,
        verbose_name="Setor Demandante",
        help_text="Nome do setor que solicitou a contratação."
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Elaborador"
    )

    descricao_necessidade = models.TextField(
        verbose_name="1. Descrição da Necessidade",
        help_text="Detalhe o problema a ser resolvido ou a necessidade."
    )
    objetivo_contratacao = models.TextField(
        verbose_name="2. Objetivo da Contratação",
        help_text="Qual o resultado esperado com a contratação?"
    )
    requisitos_contratacao = models.TextField(
        verbose_name="3. Requisitos da Contratação",
        help_text="Características mínimas que a solução deve ter."
    )
    levantamento_solucoes_mercado = models.TextField(
        verbose_name="4. Levantamento de Soluções de Mercado",
        help_text="Pesquisa e análise das alternativas disponíveis no mercado."
    )
    estimativa_quantidades = models.TextField(
        verbose_name="5. Estimativa das Quantidades",
        help_text="Qual a quantidade/dimensão da contratação."
    )
    estimativa_valor = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="6. Estimativa do Valor da Contratação (R$)",
        help_text="Valor estimado da contratação."
    )
    resultados_esperados = models.TextField(
        verbose_name="7. Resultados Esperados",
        help_text="Benefícios que a contratação trará."
    )
    viabilidade_justificativa_solucao = models.TextField(
        verbose_name="8. Viabilidade e Justificativa da Solução Escolhida",
        help_text="Qual a melhor solução e por que é a melhor."
    )
    contratacoes_correlatas = models.TextField(
        verbose_name="9. Contratações Correlatas e/ou Interdependentes",
        null=True,
        blank=True,
        help_text="Essa contratação depende de outras?"
    )
    alinhamento_planejamento = models.TextField(
        verbose_name="10. Alinhamento com o Planejamento Estratégico",
        help_text="A contratação está de acordo com os objetivos maiores da instituição?"
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_DOCUMENTO_CHOICES,
        default='EM_ELABORACAO',
        verbose_name="Status do Documento"
    )
    observacoes_analise = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações da Análise"
    )

    item_pca_vinculado = models.ForeignKey(
        "ItemPCA",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Item do PCA Vinculado"
    )
    anexos = models.ManyToManyField(
        ArquivoAnexo, # <<< ATUALIZADO: Agora usa ArquivoAnexo do core
        blank=True,
        verbose_name="Anexos do ETP"
    )

    permissions = [
                ("pode_submeter_etp_analise", "Pode submeter ETP para análise de requerimentos"),
                ("pode_aprovar_etp_analise", "Pode aprovar ETP pela Análise de Requerimentos"),
                ("pode_recusar_etp_analise", "Pode recusar ETP pela Análise de Requerimentos"),
                ("pode_aprovar_etp_orcamento", "Pode aprovar ETP pelo Setor de Orçamento"),
                ("pode_recusar_etp_orcamento", "Pode recusar ETP pelo Setor de Orçamento"),
            ]

    class Meta:
        verbose_name = "Estudo Técnico Preliminar (ETP)"
        verbose_name_plural = "Estudos Técnicos Preliminares (ETP)"
        ordering = ['-data_criacao']

    def __str__(self):
        processo_str = self.processo_vinculado.numero_protocolo or self.processo_vinculado.titulo if self.processo_vinculado else "Nenhum Processo"
        return f"ETP: {self.titulo} (Proc: {processo_str})"

    def get_analise_preliminar(self):
        pendencias = []

        if not self.descricao_necessidade:
            pendencias.append("A descrição da necessidade está vazia. Detalhe o problema.")
        if not self.objetivo_contratacao:
            pendencias.append("O objetivo da contratação não foi preenchido. Qual o resultado esperado?")
        if not self.requisitos_contratacao:
            pendencias.append("Os requisitos da contratação não foram informados. Quais as características mínimas?")
        if not self.levantamento_solucoes_mercado:
            pendencias.append("Não foi realizado o levantamento de soluções de mercado.")
        if not self.estimativa_quantidades:
            pendencias.append("A estimativa de quantidades não foi preenchida.")
        if self.estimativa_valor is None or self.estimativa_valor <= 0:
            pendencias.append("O valor estimado da contratação é nulo ou zero. Favor informar um valor válido.")
        if not self.viabilidade_justificativa_solucao:
            pendencias.append("A justificativa da solução escolhida está vazia.")
        if not self.alinhamento_planejamento:
            pendencias.append("O alinhamento com o planejamento estratégico não foi detalhado.")

        if not self.item_pca_vinculado:
            pendencias.append("O ETP não está vinculado a um item do Plano de Contratações Anual (PCA).")
        else:
            MARGEM_TOLERANCIA = Decimal('0.10')
            valor_etp = self.estimativa_valor or Decimal('0')
            valor_pca = self.item_pca_vinculado.valor_estimado_pca or Decimal('0')

            if valor_pca > 0:
                diferenca_percentual = abs(valor_etp - valor_pca) / valor_pca
                if diferenca_percentual > MARGEM_TOLERANCIA:
                    pendencias.append(
                        f"Princípio da Economicidade: Valor estimado do ETP (R$ {valor_etp:,.2f}) "
                        f"difere mais de 10% do valor do PCA (R$ {valor_pca:,.2f}). "
                        f"Diferença: {diferenca_percentual:.2%}. Justificar."
                    )
            elif valor_etp > 0:
                pendencias.append(
                    f"Valor do ETP (R$ {valor_etp:,.2f}) informado, mas valor no PCA é zero."
                )

            setor = self.setor_demandante.strip().lower() if self.setor_demandante else ""
            unidade = self.item_pca_vinculado.unidade_requisitante.strip().lower() if self.item_pca_vinculado.unidade_requisitante else ""

            if setor and unidade and setor != unidade:
                pendencias.append(
                    f"Alinhamento com PCA: Setor demandante do ETP ('{self.setor_demandante}') "
                    f"difere da unidade requisitante no PCA ('{self.item_pca_vinculado.unidade_requisitante}')."
                )

            if self.descricao_necessidade and self.item_pca_vinculado.descricao_item:
                pendencias.append(
                    f"Alinhamento com PCA: Verifique se a descrição do ETP ('{self.descricao_necessidade[:50]}...') "
                    f"está alinhada com a descrição do PCA ('{self.item_pca_vinculado.descricao_item[:50]}...')."
                )

        if not self.pesquisas_preco.exists():
            pendencias.append(
                'Nenhuma pesquisa de preço foi adicionada. Adicione pelo menos 3 pesquisas para garantir a economicidade.'
            )
        elif self.pesquisas_preco.count() < 3:
            pendencias.append(
                f'Apenas {self.pesquisas_preco.count()} pesquisas de preço foram adicionadas. Adicione pelo menos {3 - self.pesquisas_preco.count()} mais para garantir a economicidade.'
            )
        else:
            pass

        return pendencias

# --- Modelo para TR (Termo de Referência) ---
class TR(models.Model):
    etp_origem = models.OneToOneField(
        ETP,
        on_delete=models.CASCADE,
        related_name='termo_referencia',
        verbose_name="ETP de Origem",
        help_text="Estudo Técnico Preliminar que deu origem a este Termo de Referência."
    )
    titulo = models.CharField(
        max_length=255,
        verbose_name="Título do Termo de Referência",
        help_text="Título descritivo do Termo de Referência."
    )

    processo_vinculado = models.OneToOneField(
        Processo,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='tr_documento',
        verbose_name="Processo Principal (ProGestor Público)"
    )
    numero_processo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Número do Processo SEI/Interno",
        help_text="Número do processo administrativo relacionado a este TR."
    )
    data_criacao = models.DateField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Elaborador"
    )

    objeto = models.TextField(
        verbose_name="1. Objeto",
        help_text="Descrição clara e concisa do que será contratado."
    )
    justificativa = models.TextField(
        verbose_name="2. Justificativa",
        help_text="Relembre a necessidade e os objetivos da contratação."
    )
    especificacoes_tecnicas = models.TextField(
        verbose_name="3. Especificações Técnicas do Objeto",
        help_text="Detalhe as características técnicas do bem ou serviço."
    )
    metodologia_execucao = models.TextField(
        verbose_name="4. Metodologia de Execução (se serviço)",
        null=True,
        blank=True,
        help_text="Como o serviço deve ser executado."
    )
    prazo_execucao_entrega = models.CharField(
        max_length=255,
        verbose_name="5. Prazo de Execução/Entrega",
        help_text="Quando o bem deve ser entregue ou o serviço concluído."
    )
    cronograma_fisico_financeiro = models.TextField(
        verbose_name="6. Cronograma Físico-Financeiro (se aplicável)",
        null=True,
        blank=True,
        help_text="Detalhe das etapas e dos pagamentos."
    )
    criterios_habilitacao = models.TextField(
        verbose_name="7. Critérios de Habilitação (Técnica)",
        help_text="Requisitos que a empresa precisa comprovar."
    )
    criterios_aceitacao = models.TextField(
        verbose_name="8. Critérios de Aceitação do Objeto",
        help_text="Como a administração vai verificar se o que foi entregue está de acordo."
    )
    criterios_pagamento = models.TextField(
        verbose_name="9. Critérios de Pagamento",
        help_text="Como e quando os pagamentos serão feitos."
    )
    obrigacoes_partes = models.TextField(
        verbose_name="10. Obrigações da Contratada e da Contratante",
        help_text="O que cada parte deve fazer."
    )
    sancoes_administrativas = models.TextField(
        verbose_name="11. Sanções Administrativas",
        help_text="Quais as penalidades em caso de descumprimento."
    )
    fiscalizacao_contrato = models.TextField(
        verbose_name="12. Fiscalização do Contrato",
        help_text="Quem será o fiscal do contrato e suas atribuições."
    )
    vigencia_contrato = models.CharField(
        max_length=255,
        verbose_name="13. Vigência do Contrato",
        help_text="Por quanto tempo o contrato será válido."
    )
    estimativa_preco_tr = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="14. Estimativa de Preço (R$)",
        help_text="Valor estimado da contratação para o TR."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_DOCUMENTO_CHOICES,
        default='EM_ELABORACAO',
        verbose_name="Status do TR"
    )
    observacoes_analise = models.TextField(
        verbose_name="Observações da Análise",
        null=True,
        blank=True,
        help_text="Comentários e feedback da equipe de análise."
    )
    anexos = models.ManyToManyField(
        ArquivoAnexo, # <<< ATUALIZADO: Agora usa ArquivoAnexo do core
        blank=True,
        verbose_name="Anexos do TR",
        help_text="Anexos relevantes para este Termo de Referência."
    )

    class Meta:
        verbose_name = "Termo de Referência (TR)"
        verbose_name_plural = "Termos de Referência (TR)"
        ordering = ['-data_criacao']

    def __str__(self):
        processo_str = self.processo_vinculado.numero_protocolo or self.processo_vinculado.titulo if self.processo_vinculado else "Nenhum Processo"
        return f"TR: {self.titulo} (Proc: {processo_str})"

# --- Modelo Anexo REMOVIDO daqui (agora usa core.ArquivoAnexo) ---

# --- Novo Modelo para o PCA (Plano de Contratações Anual) ---
class PCA(models.Model):
    ano_vigencia = models.IntegerField(
        unique=True,
        verbose_name="Ano de Vigência",
        help_text="Ano ao qual este Plano de Contratações Anual se refere (Ex: 2025)."
    )
    data_aprovacao = models.DateField(
        verbose_name="Data de Aprovação do PCA",
        help_text="Data em que o PCA foi formalmente aprovado."
    )
    responsavel_aprovacao = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name="Responsável pela Aprovação"
    )
    arquivo_pca = models.FileField(
        upload_to='pca_arquivos/',
        null=True,
        blank=True,
        verbose_name="Arquivo PCA Completo (PDF)"
    )
    titulo = models.CharField(max_length=255, verbose_name="Título do PCA", default="PCA")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição do PCA")


    class Meta:
        verbose_name = "Plano de Contratações Anual (PCA)"
        verbose_name_plural = "Planos de Contratações Anuais (PCA)"
        ordering = ['-ano_vigencia']

    def __str__(self):
        return f"PCA {self.ano_vigencia}"

# --- Novo Modelo para Itens do PCA ---
class ItemPCA(models.Model):
    pca = models.ForeignKey(
        PCA,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name="Plano de Contratações Anual"
    )
    identificador_item = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Identificador do Item no PCA",
        help_text="Código ou descrição que identifica o item no PCA (Ex: 'SERVIÇO-TI-001', 'MAT-ESC-005')."
    )
    descricao_item = models.TextField(
        verbose_name="Descrição do Item",
        help_text="Descrição detalhada do item a ser contratado/adquirido conforme o PCA."
    )
    valor_estimado_pca = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Valor Estimado no PCA (R$)",
        help_text="Valor previsto para a contratação/aquisição no PCA."
    )
    unidade_requisitante = models.CharField(
        max_length=100,
        verbose_name="Unidade Requisitante Prevista",
        help_text="Unidade que previu a demanda por este item no PCA."
    )

    class Meta:
        verbose_name = "Item do PCA"
        verbose_name_plural = "Itens do PCA"
        unique_together = ('pca', 'identificador_item')
        ordering = ['identificador_item']

    def __str__(self):
        return f"{self.identificador_item} - {self.descricao_item} (PCA {self.pca.ano_vigencia})"

# --- Novo Modelo para Catálogo de Itens Contratados ---
class ItemCatalogo(models.Model):
    nome_padronizado = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Nome Padronizado do Item",
        help_text="Nome comum e padronizado do bem ou serviço no catálogo."
    )
    descricao_tecnica = models.TextField(
        verbose_name="Descrição Técnica Detalhada",
        help_text="Especificações técnicas, características físicas, normas aplicáveis. (Use um editor WYSIWYG se possível)."
    )
    unidade_medida = models.CharField(
        max_length=50,
        verbose_name="Unidade de Medida",
        help_text="Ex: UN (Unidade), KG (Quilograma), M2 (Metro Quadrado), HORA (Hora)."
    )
    preco_historico_medio = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Preço Histórico Médio (R$)",
        help_text="Média dos preços de contratações anteriores."
    )
    data_ultima_atualizacao = models.DateField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        verbose_name = "Item de Catálogo"
        verbose_name_plural = "Itens de Catálogo"
        ordering = ['nome_padronizado']

    def __str__(self):
        return self.nome_padronizado

class PesquisaPreco(models.Model):
    etp = models.ForeignKey('ETP', related_name='pesquisas_preco', on_delete=models.CASCADE)
    fornecedor = models.CharField(max_length=255)
    valor_cotado = models.DecimalField(max_digits=12, decimal_places=2)
    data_pesquisa = models.DateField()

    class Meta:
        verbose_name = "Pesquisa de Preço"
        verbose_name_plural = "Pesquisas de Preço"

    def __str__(self):
        return f"{self.fornecedor} - R$ {self.valor_cotado}"

class ParecerTecnico(models.Model):
    etp = models.ForeignKey('ETP', on_delete=models.CASCADE, related_name='pareceres')
    conteudo = models.TextField()
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Parecer Técnico"
        verbose_name_plural = "Pareceres Técnicos"

    def __str__(self):
        return f"Parecer de {self.autor} em {self.data_criacao.date()}"

class ModeloTexto(models.Model):
    titulo = models.CharField(max_length=255)
    texto = models.TextField()

    class Meta:
        verbose_name = "Modelo de Texto"
        verbose_name_plural = "Modelos de Texto"

    def __str__(self):
        return self.titulo

class RequisitoPadrao(models.Model):
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição", blank=True, null=True)
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Requisito Padrão"
        verbose_name_plural = "Requisitos Padrão"
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.titulo}"
    



STATUS_CONTRATO_CHOICES = [
    ('VIGENTE', 'Vigente'),
    ('ENCERRADO', 'Encerrado'),
    ('CANCELADO', 'Cancelado'),
]

class Contrato(models.Model):
    processo_vinculado = models.ForeignKey(
        Processo,
        on_delete=models.PROTECT,
        related_name='contratos',
        verbose_name="Processo Vinculado"
    )
    licitacao_origem = models.ForeignKey(
        Edital,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='contratos_gerados',
        verbose_name="Licitação de Origem"
    )
    contratado = models.ForeignKey(
        Fornecedor,
        on_delete=models.PROTECT,
        related_name='contratos',
        verbose_name="Fornecedor Contratado"
    )
    numero_contrato = models.CharField(
        max_length=50,
        verbose_name="Número do Contrato"
    )
    ano_contrato = models.IntegerField(
        verbose_name="Ano do Contrato"
    )
    objeto = models.TextField(
        verbose_name="Objeto do Contrato"
    )
    valor_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Valor Total do Contrato (R$)"
    )
    data_assinatura = models.DateField(
        verbose_name="Data de Assinatura"
    )
    data_inicio_vigencia = models.DateField(
        verbose_name="Início da Vigência"
    )
    data_fim_vigencia = models.DateField(
        verbose_name="Fim da Vigência"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CONTRATO_CHOICES,
        default='VIGENTE',
        verbose_name="Status do Contrato"
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        unique_together = ('numero_contrato', 'ano_contrato') # Garante que não haja contratos duplicados
        ordering = ['-ano_contrato', '-numero_contrato']

    def __str__(self):
        return f"Contrato {self.numero_contrato}/{self.ano_contrato} - {self.contratado.razao_social}"
    
    
STATUS_ATA_CHOICES = [
    ('VIGENTE', 'Vigente'),
    ('EXPIRADA', 'Expirada'),
    ('CANCELADA', 'Cancelada'),
]

class AtaRegistroPrecos(models.Model):
    processo_vinculado = models.ForeignKey(
        Processo,
        on_delete=models.PROTECT,
        related_name='atas_rp',
        verbose_name="Processo Vinculado"
    )
    licitacao_origem = models.ForeignKey(
        Edital,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='atas_geradas',
        verbose_name="Licitação de Origem"
    )
    fornecedor_beneficiario = models.ForeignKey(
        Fornecedor,
        on_delete=models.PROTECT,
        related_name='atas_rp',
        verbose_name="Fornecedor Beneficiário"
    )
    numero_ata = models.CharField(
        max_length=50,
        verbose_name="Número da Ata"
    )
    ano_ata = models.IntegerField(
        verbose_name="Ano da Ata"
    )
    objeto = models.TextField(
        verbose_name="Objeto da Ata de RP"
    )
    valor_total_registrado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Valor Total Registrado (R$)"
    )
    data_assinatura = models.DateField(
        verbose_name="Data de Assinatura"
    )
    data_inicio_vigencia = models.DateField(
        verbose_name="Início da Vigência"
    )
    data_fim_vigencia = models.DateField(
        verbose_name="Fim da Vigência"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_ATA_CHOICES,
        default='VIGENTE',
        verbose_name="Status da Ata"
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Ata de Registro de Preços"
        verbose_name_plural = "Atas de Registro de Preços"
        unique_together = ('numero_ata', 'ano_ata')
        ordering = ['-ano_ata', '-numero_ata']

    def __str__(self):
        return f"Ata de RP {self.numero_ata}/{self.ano_ata} - {self.fornecedor_beneficiario.razao_social}"