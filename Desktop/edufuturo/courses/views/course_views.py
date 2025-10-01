# courses/views/course_views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

# AQUI ESTÁ A MUDANÇA: Importar todos os modelos que você precisa
from courses.models import Course, Lesson, Module, Material
from learning.models import LessonProgress # <--- Adicione esta importação para o LessonProgress

def course_list(request):
    """
    Lista todos os cursos ativos para exibição na página inicial.
    """
    courses = Course.objects.filter(is_active=True).order_by('start_date')
    return render(request, 'courses/course_list.html', {'courses': courses})

def course_detail(request, course_id): # <--- A função deve aceitar o argumento 'course_id'
    """
    Exibe os detalhes de um curso específico, incluindo seus módulos e aulas.
    """
    course = get_object_or_404(Course, pk=course_id)
    context = {
        'course': course
    }
    return render(request, 'courses/course_detail.html', context)

def lesson_detail(request, lesson_id):
    """
    Exibe os detalhes de uma aula específica e o progresso do aluno.
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)
    student = None
    progress = None
    if request.user.is_authenticated and hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
        progress, created = LessonProgress.objects.get_or_create(
            student=student,
            lesson=lesson
        )
    return render(request, 'courses/lesson_detail.html', {
        'lesson': lesson,
        'progress': progress
    })
