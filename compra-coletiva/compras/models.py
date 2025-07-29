# compras/models.py

from django.db import models
from django.utils import timezone
import uuid 

from contas.models import Usuario 
from ofertas.models import Oferta 

class Compra(models.Model):
    STATUS_PAGAMENTO_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('recusada', 'Recusada'),
        ('cancelada', 'Cancelada'),
        ('reembolsada', 'Reembolsada'), # Adicionado para clareza
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='compras', verbose_name="Usuário")
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE, related_name='compras', verbose_name="Oferta")
    quantidade = models.PositiveIntegerField(default=1, verbose_name="Quantidade")
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Total")
    data_compra = models.DateTimeField(auto_now_add=True, verbose_name="Data da Compra")
    status_pagamento = models.CharField(max_length=20, choices=STATUS_PAGAMENTO_CHOICES, default='pendente', verbose_name="Status do Pagamento")
    
    # Campos Mercado Pago
    id_transacao_mp = models.CharField(max_length=255, unique=True, blank=True, null=True, verbose_name="ID Transação MP") # ID do pagamento no MP
    id_preferencia_mp = models.CharField(max_length=255, unique=True, blank=True, null=True, verbose_name="ID Preferência MP") # ID da preferência de pagamento
    metodo_pagamento = models.CharField(max_length=50, blank=True, null=True, verbose_name="Método de Pagamento")
    
    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ['-data_compra']

    def __str__(self):
        return f"Compra #{self.id} de {self.quantidade}x {self.oferta.titulo} por {self.usuario.username}"

class Cupom(models.Model):
    STATUS_CUPOM_CHOICES = [
        ('disponivel', 'Disponível'),
        ('resgatado', 'Resgatado'),
        ('expirado', 'Expirado'),
        ('cancelado', 'Cancelado'),
    ]

    compra = models.OneToOneField(Compra, on_delete=models.CASCADE, related_name='cupom', null=True, blank=True, verbose_name="Compra Relacionada")
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE, related_name='cupons', verbose_name="Oferta")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='meus_cupons', verbose_name="Usuário Dono do Cupom")
    codigo = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Código do Cupom")
    data_geracao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Geração")
    valido_ate = models.DateTimeField(verbose_name="Válido Até")
    status = models.CharField(max_length=20, choices=STATUS_CUPOM_CHOICES, default='disponivel', verbose_name="Status do Cupom")
    
    data_resgate = models.DateTimeField(null=True, blank=True, verbose_name="Data de Resgate")
    resgatado_por = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='cupons_resgatados_por_mim', 
        verbose_name="Resgatado Por"
    )

    class Meta:
        verbose_name = "Cupom"
        verbose_name_plural = "Cupons"
        ordering = ['-data_geracao']

    def __str__(self):
        return f"Cupom {self.codigo} para {self.oferta.titulo} ({self.usuario.username})"

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = str(uuid.uuid4()).replace('-', '')[:12].upper() 
        super().save(*args, **kwargs)

    @property
    def esta_valido(self):
        return self.status == 'disponivel' and self.valido_ate >= timezone.now()