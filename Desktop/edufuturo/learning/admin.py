# learning/admin.py
from django.contrib import admin
from .models import Enrollment, LessonProgress

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """
    Define a exibição e o gerenciamento do modelo Enrollment no admin.
    """
    list_display = ('student', 'course', 'enrollment_date')
    list_filter = ('course', 'enrollment_date')
    search_fields = ('student__user__username', 'course__name')

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    """
    Define a exibição e o gerenciamento do modelo LessonProgress no admin.
    """
    list_display = ('student', 'lesson', 'completed', 'last_accessed', 'quiz_score')
    list_filter = ('completed', 'last_accessed')
    search_fields = ('student__user__username', 'lesson__title')
