from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    path('conquistas/', views.achievements_view, name='achievements'),
]