# notifications/models.py
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from users.models import CustomUser

class Notification(models.Model):
    recipient = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='notifications_received'
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    # CAMPOS QUE ESTAVAM FALTANDO e que o admin espera:
    verb = models.CharField(max_length=255, verbose_name="Verbo/Ação", blank=True, null=True)
    
    NOTIFICATION_TYPE_CHOICES = (
        ('course_update', 'Atualização de Curso'),
        ('forum_reply', 'Resposta no Fórum'),
        ('quiz_result', 'Resultado de Quiz'),
        ('system_alert', 'Alerta do Sistema'),
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES,
        verbose_name="Tipo de Notificação",
        blank=True, null=True
    )

    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"

    def __str__(self):
        return f"Notificação para {self.recipient.username}: {self.message[:50]}..."