from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('aula/<int:lesson_id>/', views.topic_list, name='topic_list'),
    path('comentar/<int:topic_id>/', views.add_comment, name='add_comment'),
    path('verificar/<int:comment_id>/', views.mark_verified, name='mark_verified'),
    path('curtir/<int:comment_id>/', views.upvote_comment, name='upvote'),
]