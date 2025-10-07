# mercadopago/models.py

from django.db import models
from produtos.models import Pedido # Importa o seu modelo de pedido principal do app 'produtos'

class TransacaoMercadoPago(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='transacoes_mp',
        verbose_name="Pedido Original"
    )
    payment_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="ID do Pagamento no Mercado Pago"
    )
    status = models.CharField(
        max_length=50,
        default='pendente',
        verbose_name="Status do Pagamento"
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor da Transação")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    meio_pagamento_tipo = models.CharField(max_length=50, blank=True, null=True, verbose_name="Meio de Pagamento")
    cliente_email = models.EmailField(blank=True, null=True, verbose_name="Email do Cliente")
    data_aprovacao = models.DateTimeField(blank=True, null=True, verbose_name="Data de Aprovação")
    # ----------------------------------------

    def __str__(self):
        return f"Transação MP {self.payment_id} - Pedido {self.pedido.id} - Status: {self.status}"