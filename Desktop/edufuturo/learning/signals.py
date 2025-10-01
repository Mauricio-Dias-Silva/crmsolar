from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Enrollment, LessonProgress
from courses.models import Lesson

@receiver(post_save, sender=Enrollment)
def create_initial_progress(sender, instance, created, **kwargs):
    if created:
        student = instance.student
        course = instance.course
        for module in course.modules.all():
            for lesson in module.lessons.all():
                LessonProgress.objects.get_or_create(
                    student=student,
                    lesson=lesson
                )