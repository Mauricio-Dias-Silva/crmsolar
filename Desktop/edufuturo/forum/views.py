from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from .models import Topic, Comment, Vote
from .forms import TopicForm, CommentForm

@login_required
def topic_list(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    topics = Topic.objects.filter(lesson=lesson).prefetch_related(
        'comments__author', 
        'comments__votes', 
        'comments__replies__author'
    )
    form = TopicForm()

    if request.method == 'POST' and request.user.role in ['STUDENT', 'PROFESSOR']:
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.lesson = lesson
            topic.author = request.user
            topic.save()
            messages.success(request, "Tópico criado com sucesso!")
            return redirect('forum:topic_list', lesson_id=lesson.id)

    return render(request, 'forum/topic_list.html', {
        'lesson': lesson,
        'topics': topics,
        'form': form
    })

@login_required
def add_comment(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.topic = topic
            comment.author = request.user
            comment.save()
            messages.success(request, "Comentário adicionado!")
    return redirect('forum:topic_list', lesson_id=topic.lesson.id)

@login_required
def mark_verified(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user.role == 'PROFESSOR' and comment.topic.lesson.professors.filter(id=request.user.id).exists():
        comment.is_verified = True
        comment.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'forbidden'}, status=403)

@login_required
def upvote_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    vote, created = Vote.objects.get_or_create(voter=request.user, comment=comment)
    if not created:
        vote.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({
        'likes': comment.votes.count(),
        'liked': liked
    })