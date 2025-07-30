# pedidos_coletivos/models.py

from django.db import models
from django.utils import timezone
import uuid
from decimal import Decimal
from django.db import transaction # <--- ESTA LINHA É CRUCIAL!

# Importe os modelos dos seus outros apps
from contas.models import Usuario
from ofertas.models import Oferta

class PedidoColetivo(models.Model):
    # ... (Seu código do modelo PedidoColetivo) ...
    STATUS_PAGAMENTO_CHOICES = [
        ('pendente', 'Pendente'), # Aguardando pagamento do usuário
        ('aprovado_mp', 'Aprovado no MP (Aguardando Lote)'), # Pagamento ok no MP, mas lote não concretizado
        ('recusado', 'Recusado'),
        ('cancelado_cliente', 'Cancelado pelo Cliente'),
        ('lote_cancelado_com_credito', 'Lote Cancelado (Crédito Gerado)'), # Adicionado explicitamente se ainda não estava
    ]

    STATUS_LOTE_CHOICES = [
        ('aberto', 'Lote Aberto (Aguardando Mínimo)'), # Período de venda
        ('concretizado', 'Lote Concretizado'), # Mínimo atingido e pagamentos processados
        ('falha', 'Lote Falhou (Mínimo Não Atingido)'), # Mínimo não atingido
        ('finalizado_admin', 'Finalizado pelo Admin'), # Intervenção manual
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pedidos_coletivos', verbose_name="Usuário")
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE, related_name='pedidos_coletivos', verbose_name="Oferta Coletiva")
    quantidade = models.PositiveIntegerField(default=1, verbose_name="Quantidade Comprada")
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Unitário")
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Total do Pedido")
    data_pedido = models.DateTimeField(auto_now_add=True, verbose_name="Data do Pedido")

    status_pagamento = models.CharField(max_length=30, choices=STATUS_PAGAMENTO_CHOICES, default='pendente', verbose_name="Status do Pagamento") # Aumentado max_length para ter folga
    status_lote = models.CharField(max_length=20, choices=STATUS_LOTE_CHOICES, default='aberto', verbose_name="Status do Lote")

    id_transacao_mp = models.CharField(max_length=255, unique=True, blank=True, null=True, verbose_name="ID Transação MP") 
    id_preferencia_mp = models.CharField(max_length=255, unique=True, blank=True, null=True, verbose_name="ID Preferência MP") 
    metodo_pagamento = models.CharField(max_length=50, blank=True, null=True, verbose_name="Método de Pagamento")

    cupom_gerado = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="Código do Cupom Gerado")
    data_cupom_gerado = models.DateTimeField(null=True, blank=True, verbose_name="Data de Geração do Cupom")

    class Meta:
        verbose_name = "Pedido Coletivo"
        verbose_name_plural = "Pedidos Coletivos"
        ordering = ['-data_pedido']

    def __str__(self):
        return f"Pedido Coletivo #{self.id} de {self.quantidade}x {self.oferta.titulo}"

    @property
    def eh_lote_aprovado_mp(self):
        return self.status_pagamento == 'aprovado_mp'

    @property
    def cupom_esta_disponivel(self):
        return self.cupom_gerado is not None and self.status_lote == 'concretizado'


class CreditoUsuario(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='credito_site', verbose_name="Usuário")
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Saldo de Crédito")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Crédito do Usuário"
        verbose_name_plural = "Créditos dos Usuários"

    def __str__(self):
        return f"Crédito de {self.usuario.username}: R${self.saldo}"

    def adicionar_credito(self, valor, descricao="Crédito adicionado"):
        with transaction.atomic(): # <--- CORREÇÃO AQUI
            self.saldo += Decimal(str(valor))
            self.save()
            HistoricoCredito.objects.create(
                credito_usuario=self,
                tipo_transacao='entrada',
                valor=Decimal(str(valor)),
                saldo_apos_transacao=self.saldo,
                descricao=descricao
            )

    def usar_credito(self, valor, descricao="Crédito usado"):
        valor_decimal = Decimal(str(valor))
        if self.saldo < valor_decimal:
            raise ValueError("Saldo insuficiente para usar este valor.")
        with transaction.atomic(): # <--- CORREÇÃO AQUI
            self.saldo -= valor_decimal
            self.save()
            HistoricoCredito.objects.create(
                credito_usuario=self,
                tipo_transacao='saida',
                valor=valor_decimal,
                saldo_apos_transacao=self.saldo,
                descricao=descricao
            )

class HistoricoCredito(models.Model):
    TIPO_TRANSACAO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]
    credito_usuario = models.ForeignKey(CreditoUsuario, on_delete=models.CASCADE, related_name='historico', verbose_name="Crédito do Usuário")
    tipo_transacao = models.CharField(max_length=10, choices=TIPO_TRANSACAO_CHOICES, verbose_name="Tipo de Transação")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    saldo_apos_transacao = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Saldo Após")
    data_transacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Transação")
    descricao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descrição")

    class Meta:
        verbose_name = "Histórico de Crédito"
        verbose_name_plural = "Históricos de Crédito"
        ordering = ['-data_transacao']

    def __str__(self):
        return f"{self.tipo_transacao.capitalize()} de R${self.valor} para {self.credito_usuario.usuario.username}"