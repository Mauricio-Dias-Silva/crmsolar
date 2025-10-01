# courses/models/module.py
from django.db import models

class Module(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='modules', verbose_name="Curso")
    title = models.CharField("Título", max_length=200)
    description = models.TextField("Descrição", blank=True)
    order = models.PositiveIntegerField("Ordem", default=1)

    class Meta:
        verbose_name = "Módulo"
        verbose_name_plural = "Módulos"
        ordering = ['order']

    def __str__(self):
        return f"{self.course.code} - Módulo {self.order}: {self.title}"