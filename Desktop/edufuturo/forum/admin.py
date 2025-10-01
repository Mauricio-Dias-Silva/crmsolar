# forum/admin.py
from django.contrib import admin
from .models import Topic, Comment, Vote

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    # Estes campos agora existem no modelo Topic
    list_display = ('title', 'lesson', 'author', 'created_at', 'is_resolved')
    # Estes filtros agora existem ou são válidos no modelo Topic
    list_filter = ('is_resolved', 'created_at', 'lesson__module__course') # Este filtro agora será válido
    search_fields = ('title', 'author__username', 'content') # Adicione content para busca

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    # Estes campos também precisam existir no modelo Comment
    list_display = ('author', 'topic', 'created_at', 'is_verified', 'parent')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('content', 'author__username')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('voter', 'comment', 'created_at')