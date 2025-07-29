# projeto_compra_coletiva/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importe as views do seu app 'contas' para a rota de registro
from contas import views as contas_views # Importa as views do app 'contas'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ofertas/', include('ofertas.urls')),
    
    # URLs de autenticação do Django (login, logout, password_change, etc.)
    # Elas usarão os templates padrão do Django ou os que criarmos com os nomes esperados.
    path('contas/', include('django.contrib.auth.urls')), 
    
    # Nossa URL de registro personalizada
    path('contas/registro/', contas_views.registro_usuario, name='registro'), 
    
    # Opcional: Uma página inicial para o projeto (se não for a lista de ofertas)
    # path('', views_do_seu_app_core.home, name='home'), 
]

# Apenas para servir arquivos de mídia durante o desenvolvimento.
# REMOVA ISSO EM AMBIENTES DE PRODUÇÃO!
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)