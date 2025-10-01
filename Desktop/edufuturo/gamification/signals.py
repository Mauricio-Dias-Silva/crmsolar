from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from learning.models import LessonProgress
from forum.models import Topic, Comment
from courses.models import Course
from .models import UserXP, Achievement, Badge

def get_or_create_xp(user):
    xp, created = UserXP.objects.get_or_create(user=user)
    return xp

# Badge: Iniciante
@receiver(post_save, sender=LessonProgress)
def award_first_lesson(sender, instance, **kwargs):
    if instance.completed:
        xp = get_or_create_xp(instance.student.user)
        badge, created = Badge.objects.get_or_create(
            name="Iniciante",
            defaults={"description": "Concluiu a primeira aula", "icon": "bi-play-btn", "xp_value": 20}
        )
        if not Achievement.objects.filter(user=instance.student.user, badge=badge).exists():
            Achievement.objects.create(user=instance.student.user, badge=badge)
            xp.total_xp += badge.xp_value
            xp.save()

# XP por concluir aula
@receiver(post_save, sender=LessonProgress)
def add_xp_for_lesson_completion(sender, instance, **kwargs):
    if instance.completed and not hasattr(instance, '_saved'):  # Evita loop
        xp = get_or_create_xp(instance.student.user)
        xp.total_xp += 10
        xp.save()

# Badge: Curioso
@receiver(post_save, sender=Topic)
def award_first_question(sender, instance, created, **kwargs):
    if created:
        badge, created = Badge.objects.get_or_create(
            name="Curioso",
            defaults={"description": "Fez a primeira pergunta no fórum", "icon": "bi-chat-left-dots", "xp_value": 15}
        )
        if not Achievement.objects.filter(user=instance.author, badge=badge).exists():
            Achievement.objects.create(user=instance.author, badge=badge)
            xp = get_or_create_xp(instance.author)
            xp.total_xp += badge.xp_value
            xp.save()

# Badge: Concluinte + XP por curso
@receiver(m2m_changed, sender=Course.enrollments.through)
def award_course_completion(sender, instance, action, **kwargs):
    if action == "post_add":
        for enrollment in instance.enrollments.all():
            student = enrollment.student
            course = instance
            # Verifica se completou 100%
            if course.progress_percentage(student) == 100:
                xp = get_or_create_xp(student.user)
                # Badge de conclusão
                badge, created = Badge.objects.get_or_create(
                    name=f"Concluiu: {course.name[:20]}",
                    defaults={
                        "description": f"Concluiu o curso {course.name}",
                        "icon": "bi-award",
                        "xp_value": 100
                    }
                )
                if not Achievement.objects.filter(user=student.user, badge=badge).exists():
                    Achievement.objects.create(user=student.user, course=course, badge=badge)
                    xp.total_xp += badge.xp_value
                    xp.save()