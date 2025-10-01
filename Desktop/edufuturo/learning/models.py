from django.db import models
from django.contrib.auth import get_user_model
from datetime import timedelta

# Importa os modelos de outros aplicativos
from users.models import Student
from courses.models import Course, Lesson, Module

# Obtém o modelo de usuário personalizado
CustomUser = get_user_model()

class Enrollment(models.Model):
    """Representa a matrícula de um aluno em um curso."""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="Aluno"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="Curso"
    )
    enrollment_date = models.DateTimeField("Data de Matrícula", auto_now_add=True)

    class Meta:
        # Garante que um aluno só possa se matricular uma vez em um curso
        unique_together = ('student', 'course')
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'

    def __str__(self):
        return f"Matrícula de {self.student.user.username} em {self.course.name}"

class LessonProgress(models.Model):
    """Acompanha o progresso de um aluno em uma lição específica."""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='lesson_progresses',
        verbose_name="Aluno"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='progresses',
        verbose_name="Aula"
    )
    completed = models.BooleanField("Concluído", default=False)
    completed_at = models.DateTimeField("Data de Conclusão", null=True, blank=True)
    time_spent = models.DurationField("Tempo Gasto", default=timedelta(0))
    quiz_score = models.FloatField("Pontuação do Quiz", null=True, blank=True)

    class Meta:
        # Garante que um aluno só possa ter um progresso por lição
        unique_together = ('student', 'lesson')
        verbose_name = 'Progresso da Aula'
        verbose_name_plural = 'Progressos das Aulas'

    def __str__(self):
        return f"{self.student.user.username} - {self.lesson.title} ({'Concluída' if self.completed else 'Em Andamento'})"

