from django.db.models.signals import post_save
from django.dispatch import receiver
from courses.models import Lesson
from .utils import create_notification

@receiver(post_save, sender=Lesson)
def notify_new_lesson(sender, instance, created, **kwargs):
    if created:
        module = instance.module
        course = module.course
        for enrollment in course.enrollments.filter(is_active=True):
            student = enrollment.student
            create_notification(
                recipient=student.user,
                verb=f"Nova aula disponível: {instance.title}",
                actor=instance.module.course.professors.first(),
                target=instance,
                notification_type='success'
            )