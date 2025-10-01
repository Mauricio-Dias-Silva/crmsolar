# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Student, Professor

@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == "STUDENT":
            Student.objects.create(user=instance, enrollment_number=f"STD{instance.id:06d}")
        elif instance.role == "PROFESSOR":
            Professor.objects.create(user=instance)