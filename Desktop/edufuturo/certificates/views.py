from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.urls import reverse
from .models import Certificate
from courses.models import Course
from .pdf_generator import generate_certificate_pdf
from .utils import generate_qr_code
from learning.models import LessonProgress
import os

@login_required
def issue_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student = request.user.student_profile

    # Verifica se completou 100%
    if course.progress_percentage(student) < 100:
        return HttpResponse("Você ainda não concluiu este curso.", status=403)

    # Evita recriar
    cert, created = Certificate.objects.get_or_create(student=student, course=course)

    return redirect('certificates:download', cert.verification_hash)

@login_required
def download_certificate(request, verification_hash):
    cert = get_object_or_404(Certificate, verification_hash=verification_hash)

    # Gera QR Code em memória
    verify_url = cert.get_verification_url()
    qr_buffer = BytesIO()
    qr = qrcode.make(verify_url)
    qr.save(qr_buffer, format='PNG')
    qr_data = qr_buffer.getvalue()
    qr_base64 = base64.b64encode(qr_data).decode()

    # Contexto
    context = {
        'certificate': cert,
        'qr_code_url': f"image/png;base64,{qr_base64}"
    }

    # Renderiza template
    html_string = render_to_string('certificates/certificate_template.html', context)
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificado_{cert.certificate_id}.pdf"'
    return response

def verify_certificate(request, verification_hash):
    cert = get_object_or_404(Certificate, verification_hash=verification_hash)
    return render(request, 'certificates/verify.html', {'cert': cert})