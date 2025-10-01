from django.db import models
from django.contrib.auth import get_user_model
from courses.models import Course
from uuid import uuid4
from datetime import datetime

User = get_user_model()

class Certificate(models.Model):
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now_add=True)
    certificate_id = models.CharField(max_length=20, unique=True, editable=False)  # ex: CERT-ABCD1234
    verification_hash = models.UUIDField(default=uuid4, unique=True, editable=False)
    is_valid = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'course')  # Um certificado por aluno por curso
        verbose_name = "Certificado"
        verbose_name_plural = "Certificados"

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            # Gera ID: CERT- + 8 caracteres (ex: CERT-A1B2C3D4)
            self.certificate_id = "CERT-" + str(uuid4().hex[:8].upper())
        super().save(*args, **kwargs)

    def get_verification_url(self):
        """URL pública para verificar autenticidade"""
        from django.urls import reverse
        return f"https://edufuturo.pro{reverse('certificates:verify', args=[self.verification_hash])}"

    def __str__(self):
        return f"Certificado: {self.student} - {self.course.name}"