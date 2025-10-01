from django.urls import path
from . import views

app_name = 'learning'

urlpatterns = [
    path('matricular/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('concluir-aula/<int:lesson_id>/', views.mark_lesson_complete, name='mark_complete'),
]