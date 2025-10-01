from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# config/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('courses.urls')),
    path('aluno/', include('users.urls')),
    path('aprendizado/', include('learning.urls', namespace='learning')),
    path('forum/', include('forum.urls')),
    path('certificados/', include('certificates.urls', namespace='certificates')),
    path('api/v1/', include('api.v1.urls')),
    path('gamificacao/', include('gamification.urls', namespace='gamification')),
    path('notificacoes/', include('notifications.urls')),
    path('buscar/', include('search.urls')),
    path('usuarios/', include('users.urls', namespace='users')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)