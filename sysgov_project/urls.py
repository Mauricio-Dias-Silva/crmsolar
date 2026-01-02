# SysGov_Project/sysgov_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('allauth.urls')),
    
    path('contratacoes/', include('contratacoes.urls')),
    path('financeiro/', include('financeiro.urls')),
    path('licitacoes/', include('licitacoes.urls')),

    # Inclua suas URLs do integracao_audesp UMA VEZ.
    # Agora, 'integracao_audesp.urls' contém as URLs reais E as URLs do mock.
    path('audesp/', include('integracao_audesp.urls', namespace='integracao_audesp')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)