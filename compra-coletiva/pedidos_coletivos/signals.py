# pedidos_coletivos/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from contas.models import Usuario
from .models import CreditoUsuario

@receiver(post_save, sender=Usuario)
def criar_ou_atualizar_credito_usuario(sender, instance, created, **kwargs):
    if created:
        CreditoUsuario.objects.create(usuario=instance)
    # Se quiser, você pode adicionar lógica para atualizar aqui também
    # instance.credito_site.save()