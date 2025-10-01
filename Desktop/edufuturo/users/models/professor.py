from django.db import models
from .custom_user import CustomUser

class Professor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='professor_profile')
    # speciality = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prof. {self.user.get_full_name() or self.user.username}"