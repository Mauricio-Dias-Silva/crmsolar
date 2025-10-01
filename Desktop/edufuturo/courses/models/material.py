# courses/models/material.py
from django.db import models

class Material(models.Model):
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, related_name='materials', verbose_name="Aula")
    title = models.CharField("Título", max_length=200)
    file = models.FileField("Arquivo", upload_to="courses/materials/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiais"

    def __str__(self):
        return self.title