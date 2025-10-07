# energia_solar/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views # <-- Garanta que esta importação existe
from solar import views as solar_views
from produtos import views as produtos_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Login e Logout UNIFICADOS
    path('login/', solar_views.login_ecommerce_view, name='login_ecommerce'),
    path('crm/login/', solar_views.login_view, name='login_crm'),
    path('logout/', solar_views.logout_view, name='logout'),
    path('login/', solar_views.login_ecommerce_view, name='login'), 
    
    # NOVAS LINHAS: URLs de Redefinição de Senha
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # Rotas do e-commerce (app produtos)
    path('', include('produtos.urls', namespace='produtos')),
    
    # Rotas do CRM (app solar)
    path('crm/', include('solar.urls', namespace='crm')),
    
    # Rotas de Pagamento (app pagamento - Stripe)
    path('pagamento/', include('pagamento.urls', namespace='pagamento')),
    
    # Rotas de Pagamento (app mercadopago - Mercado Pago)
    path('mercadopago/', include('mp_integracao.urls', namespace='mercadopago')),
    path('register/', solar_views.register_ecommerce_user, name='register_ecommerce_user'),    
    
    # Allauth
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)