from django.db import models
from django.contrib.auth import get_user_model
from courses.models import Course, Lesson

User = get_user_model()

# Tipo de conquista
class Badge(models.Model):
    name = models.CharField("Nome", max_length=100)
    description = models.TextField("Descrição")
    icon = models.CharField("Ícone (Bootstrap Icons)", max_length=50, default="bi-star")
    xp_value = models.PositiveIntegerField("Pontos de recompensa", default=50)

    class Meta:
        verbose_name = "Badge"
        verbose_name_plural = "Badges"

    def __str__(self):
        return self.name

class Achievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ('user', 'badge')  # Evita duplicatas
        verbose_name = "Conquista"
        verbose_name_plural = "Conquistas"

    def __str__(self):
        return f"{self.user} → {self.badge.name}"

class UserXP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='xp_profile')
    total_xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)

    def calculate_level(self):
        """Nível baseado em XP: 100 por nível"""
        return (self.total_xp // 100) + 1

    def save(self, *args, **kwargs):
        self.level = self.calculate_level()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - Nível {self.level} ({self.total_xp} XP)"