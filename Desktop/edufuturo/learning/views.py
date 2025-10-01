from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Enrollment
from courses.models import Course

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student = request.user.student_profile

    if Enrollment.objects.filter(student=student, course=course).exists():
        messages.info(request, "Você já está matriculado neste curso.")
    else:
        Enrollment.objects.create(student=student, course=course)
        messages.success(request, f"Matrícula realizada com sucesso no curso '{course.name}'!")

    return redirect('course_detail', course_id=course.id)

@login_required
def dashboard(request):
    student = request.user.student_profile
    enrollments = student.enrollments.filter(is_active=True)
    in_progress = [e for e in enrollments if e.course.progress_percentage(student) < 100]
    completed = [e for e in enrollments if e.course.progress_percentage(student) == 100]

    return render(request, 'learning/dashboard.html', {
        'enrollments': enrollments,
        'in_progress': in_progress,
        'completed': completed,
    })

@login_required
def mark_lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    student = request.user.student_profile

    progress, created = LessonProgress.objects.get_or_create(
        student=student,
        lesson=lesson
    )
    if not progress.completed:
        progress.completed = True
        progress.save()
        messages.success(request, f"Aula '{lesson.title}' marcada como concluída! 🎉")

    return redirect('lesson_detail', lesson_id=lesson.id)