# courses/urls.py
from django.urls import path
from . import views # <--- ESTA É A IMPORTAÇÃO CORRETA PARA AS SUAS VIEWS
# from .course import Course # <--- REMOVA OU COMENTE ESTA LINHA!

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('aula/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
]