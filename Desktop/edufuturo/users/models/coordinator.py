# users/models/coordinator.py
from django.db import models
from .custom_user import CustomUser # Importa seu CustomUser

class Coordinator(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='coordinator_profile')
    department = models.CharField(max_length=100, blank=True, null=True)
    # Adicione outros campos específicos de Coordenador aqui

    def __str__(self):
        return f"Coordenador: {self.user.username}"
    
    # Se você quiser que o Coordenador tenha o role de COODINATOR automaticamente:
    def save(self, *args, **kwargs):
        if not self.user.role == CustomUser.Role.COORDINATOR:
            self.user.role = CustomUser.Role.COORDINATOR
            self.user.save()
        super().save(*args, **kwargs)