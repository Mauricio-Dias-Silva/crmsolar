# compras/models.py

from django.db import models
from django.utils import timezone
import uuid # Para gerar códigos de cupom

from ofertas.models import Oferta # Importe Oferta
from contas.models import Usuario # Importe Usuario (seu modelo de usuário customizado)
# Importe PedidoColetivo explicitamente para usar no OneToOneField
from pedidos_coletivos.models import PedidoColetivo # <-- Importado aqui

class Compra(models.Model):
    # ... (seu código da classe Compra permanece inalterado) ...
    STATUS_PAGAMENTO_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
        ('cancelada', 'Cancelada'),
        ('reembolsada', 'Reembolsada'), # Certifique-se que este status está aqui
        ('aguardando_lote', 'Aguardando Concretização do Lote'), # Certifique-se que este status está aqui
        ('lote_cancelado', 'Lote Cancelado (Reembolsado)'), # Certifique-se que este status está aqui
        ('lote_cancelado_com_credito', 'Lote Cancelado (Crédito Gerado)'), # Certifique-se que este status está aqui
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='compras', verbose_name="Comprador")
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE, related_name='compras', verbose_name="Oferta")
    quantidade = models.PositiveIntegerField(default=1, verbose_name="Quantidade") # Certifique-se que este campo existe
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Total")
    data_compra = models.DateTimeField(auto_now_add=True, verbose_name="Data da Compra")
    status_pagamento = models.CharField(max_length=50, choices=STATUS_PAGAMENTO_CHOICES, default='pendente', verbose_name="Status do Pagamento")
    
    # Campos Mercado Pago (certifique-se que estão aqui)
    id_transacao_mp = models.CharField(max_length=255, unique=True, blank=True, null=True, verbose_name="ID Transação MP") 
    id_preferencia_mp = models.CharField(max_length=255, unique=True, blank=True, null=True, verbose_name="ID Preferência MP") 
    metodo_pagamento = models.CharField(max_length=50, blank=True, null=True, verbose_name="Método de Pagamento")

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ['-data_compra']

    def __str__(self):
        return f"Compra #{self.id} - {self.oferta.titulo}"


class Cupom(models.Model):
    STATUS_CHOICES = [
        ('disponivel', 'Disponível'),
        ('resgatado', 'Resgatado'),
        ('expirado', 'Expirado'),
        ('cancelado', 'Cancelado'), # Adicionado status cancelado
    ]
    
    # related_name='cupom_unidade' para Compra
    compra = models.OneToOneField(Compra, on_delete=models.SET_NULL, null=True, blank=True, related_name='cupom_unidade', verbose_name="Compra por Unidade") # <--- RELATED_NAME CORRIGIDO

    # related_name='cupom_coletivo' para PedidoColetivo
    pedido_coletivo = models.OneToOneField(PedidoColetivo, on_delete=models.SET_NULL, null=True, blank=True, related_name='cupom_coletivo', verbose_name="Pedido Coletivo") # <--- RELATED_NAME CORRIGIDO

    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE, related_name='cupons', verbose_name="Oferta")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='meus_cupons', verbose_name="Comprador")
    codigo = models.CharField(max_length=20, unique=True, blank=True, verbose_name="Código do Cupom")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='disponivel', verbose_name="Status do Cupom")
    valido_ate = models.DateTimeField(verbose_name="Válido Até")
    data_criacao = models.DateTimeField(default=timezone.now) 
    data_resgate = models.DateTimeField(null=True, blank=True, verbose_name="Data de Resgate")

    class Meta:
        verbose_name = "Cupom"
        verbose_name_plural = "Cupons"
        ordering = ['-data_criacao']

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = str(uuid.uuid4()).replace('-', '')[:12].upper() # Gera um código único de 12 caracteres
        super().save(*args, **kwargs)

    def __str__(self):
        return self.codigo

    @property
    def esta_valido(self):
        """Verifica se o cupom é válido (disponível e não expirado)."""
        return self.status == 'disponivel' and self.valido_ate >= timezone.now()