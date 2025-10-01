# courses/models/course.py
from django.db import models
from users.models import CustomUser

class Course(models.Model):
    name = models.CharField("Nome", max_length=200)
    code = models.CharField("Código", max_length=20, unique=True)
    description = models.TextField("Descrição")
    workload_hours = models.PositiveIntegerField("Carga Horária (horas)")
    start_date = models.DateField("Início")
    end_date = models.DateField("Fim")
    thumbnail = models.ImageField("Capa", upload_to="courses/thumbnails/", null=True, blank=True)
    syllabus = models.FileField("Plano de Ensino", upload_to="courses/syllabi/", null=True, blank=True)
    professors = models.ManyToManyField(CustomUser, limit_choices_to={'role': 'PROFESSOR'}, verbose_name="Professores")
    is_active = models.BooleanField("Ativo", default=True)

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

    def __str__(self):
        return f"{self.code} - {self.name}"

def progress_percentage(self, student):
    """Retorna a porcentagem de conclusão do aluno neste curso"""
    from learning.models import LessonProgress
    lessons = Lesson.objects.filter(module__course=self)
    if not lessons.exists():
        return 0
    completed = LessonProgress.objects.filter(
        student=student,
        lesson__in=lessons,
        completed=True
    ).count()
    total = lessons.count()
    return int((completed / total) * 100)