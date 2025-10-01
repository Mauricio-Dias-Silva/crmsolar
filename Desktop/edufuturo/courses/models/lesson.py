from django.db import models

class Lesson(models.Model):
    module = models.ForeignKey('Module', on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField("Título", max_length=200)
    content = models.TextField("Conteúdo")
    duration_minutes = models.PositiveIntegerField("Duração (minutos)", default=0)
    video_url = models.URLField("URL do Vídeo", blank=True, null=True)
    order = models.PositiveIntegerField("Ordem", default=1)

    class Meta:
        ordering = ['order']
        verbose_name = "Aula"
        verbose_name_plural = "Aulas"

    def __str__(self):
        return self.title

    @property
    def get_embed_url(self):
        if "youtube.com" in self.video_url:
            return self.video_url.replace("watch?v=", "embed/")
        return self.video_url

def get_progress_for_student(self, student):
    from learning.models import LessonProgress
    progress, created = LessonProgress.objects.get_or_create(
        student=student,
        lesson=self
    )
    return progress