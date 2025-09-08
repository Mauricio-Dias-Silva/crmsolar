# SysGov_Project/sysgov_project/settings.py

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-**hfe%*hy@gn9r2wbgo^e)qj&yj$48)xr5iiq$h%4v851m6ui*'
DEBUG = True
ALLOWED_HOSTS = []

# --- APLICAÇÕES INSTALADAS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Nossas Apps
    'core',
    'contratacoes',
    'financeiro',
    'licitacoes',
    'integracao_audesp',

    # Apps de Terceiros
    'ckeditor',
    'widget_tweaks',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', # Importante para allauth
]

ROOT_URLCONF = 'sysgov_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Aponta para a pasta de templates na raiz
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.notificacoes_nao_lidas', # Nosso context processor de notificações
            ],
        },
    },
]

WSGI_APPLICATION = 'sysgov_project.wsgi.application'

# --- BASE DE DADOS ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- VALIDAÇÃO DE SENHAS ---
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# --- INTERNACIONALIZAÇÃO ---
LANGUAGE_CODE = 'pt-BR'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# --- FICHEIROS ESTÁTICOS E DE MEDIA ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -----------------------------------------------------------
# ::: CONFIGURAÇÕES DO DJANGO ALLAUTH (VERSÃO FINAL) :::
# -----------------------------------------------------------
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)
SITE_ID = 1
LOGIN_REDIRECT_URL = 'core:home'   # Redireciona para a nossa página inicial após o login
LOGOUT_REDIRECT_URL = 'core:home'  # Redireciona para a página inicial após o logout
ACCOUNT_EMAIL_VERIFICATION = 'none' # Para desenvolvimento, não exige verificação de email
ACCOUNT_EMAIL_REQUIRED = True       # Mas o campo de email é obrigatório no registo
ACCOUNT_USERNAME_REQUIRED = True    # O nome de utilizador é obrigatório
ACCOUNT_AUTHENTICATION_METHOD = 'username_email' # Permite login com username OU email

# -----------------------------------------------------------
# ::: CONFIGURAÇÃO DE EMAIL PARA DESENVOLVIMENTO :::
# -----------------------------------------------------------
# Esta linha mágica diz ao Django para, em vez de enviar emails de verdade,
# imprimi-los no console/terminal onde o servidor está a ser executado.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

