import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (se existir)
load_dotenv()

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CONFIGURAÇÕES DE SEGURANÇA ---

# SECRET_KEY: Tenta pegar do ambiente, usa fallback inseguro apenas para dev local
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-**hfe%*hy@gn9r2wbgo^e)qj&yj$48)xr5iiq$h%4v851m6ui*')

# DEBUG: Converte string para bool. Padrão é True se não definido (cuidado em produção!)
# No Cloud Run, defina DEBUG=False nas variáveis de ambiente.
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# ALLOWED_HOSTS: Permite hosts do ambiente ou '*' como fallback
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# --- APLICAÇÕES INSTALADAS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # WhiteNoise (Recomendado rodar antes de staticfiles para dev com runserver_nostatic)
    'whitenoise.runserver_nostatic',
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
    # WhiteNoise DEVE estar logo após SecurityMiddleware para servir estáticos em produção
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'sysgov_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Context processor customizado (verifique se o app 'core' existe)
                'core.context_processors.notificacoes_nao_lidas', 
            ],
        },
    },
]

WSGI_APPLICATION = 'sysgov_project.wsgi.application'

# ==============================================================================
# BANCO DE DADOS (PADRÃO PYTHONJET - CLOUD RUN / SOCKET)
# ==============================================================================

# Verifica se o Cloud Run injetou a variável de conexão (flag --add-cloudsql-instances)
CLOUD_SQL_CONNECTION_NAME = os.getenv('CLOUD_SQL_CONNECTION_NAME')

if CLOUD_SQL_CONNECTION_NAME:
    # --- PRODUÇÃO (CLOUD RUN) ---
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            # Conexão via Socket UNIX (Essencial para Cloud Run)
            'HOST': f'/cloudsql/{CLOUD_SQL_CONNECTION_NAME}',
            'NAME': os.getenv('DB_NAME', 'sysgov_db'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'PORT': '', # Porta vazia para socket
            # Otimizações para contêineres
            'CONN_MAX_AGE': 600,
            'CONN_HEALTH_CHECKS': True,
        }
    }
else:
    # --- DESENVOLVIMENTO (LOCAL) ---
    # Tenta usar DATABASE_URL se definida, senão usa SQLite
    DATABASES = {
        'default': dj_database_url.config(
            default=f'sqlite:///{BASE_DIR}/db.sqlite3',
            conn_max_age=600
        )
    }

# --- VALIDAÇÃO DE SENHAS ---
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# --- CACHE ---
# Configuração para produção (Redis) se REDIS_URL estiver definida
if os.getenv('REDIS_URL'):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.getenv('REDIS_URL'),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }
else:
    # Fallback local
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'sysgov-cache-unico',
        }
    }

# --- INTERNACIONALIZAÇÃO ---
LANGUAGE_CODE = 'pt-BR'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# --- ARQUIVOS ESTÁTICOS (WHITENOISE) ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Storage otimizado para produção
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- INTEGRAÇÕES E CHAVES ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
AUDESP_API_BASE_URL = os.getenv("AUDESP_API_BASE_URL", "https://audesp-piloto.tce.sp.gov.br")
AUDESP_API_EMAIL = os.getenv("AUDESP_API_EMAIL")
AUDESP_API_PASSWORD = os.getenv("AUDESP_API_PASSWORD")

# --- ALLAUTH ---
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)
SITE_ID = 1
LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = 'core:home'
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'

# --- EMAIL ---
# Em produção, você deve configurar um backend SMTP real (SendGrid, Mailgun, etc.)
# Se DEBUG for False, evite usar console backend.
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Exemplo de config SMTP genérica (preencher via variáveis de ambiente)
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST')
    EMAIL_PORT = os.getenv('EMAIL_PORT', 587)
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# --- CSRF (Para Cloud Run) ---
# Adicione o domínio do Cloud Run aqui para evitar erro 403 no login
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'https://*.run.app').split(',')



# import os
# import dj_database_url
# from decouple import config

# # ... (Mantenha seus imports e BASE_DIR) ...

# # 1. MIDDLEWARE (Adicionar WhiteNoise LOGO APÓS SecurityMiddleware)
# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'whitenoise.middleware.WhiteNoiseMiddleware', # <--- ADICIONAR AQUI
#     # ... (outros middlewares) ...
# ]

# # 2. ARQUIVOS ESTÁTICOS (Configuração para Produção)
# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# # 3. BANCO DE DADOS (Configuração Híbrida Local/Nuvem)
# # Verifica se o Cloud Run injetou a conexão (Socket)
# CLOUD_SQL_CONNECTION_NAME = config('CLOUD_SQL_CONNECTION_NAME', default=None)

# # Configuração Padrão (SQLite para rodar no seu PC)
# DATABASES = {
#     'default': dj_database_url.config(
#         default=f'sqlite:///{BASE_DIR}/db.sqlite3',
#         conn_max_age=600
#     )
# }

# # Configuração Nuvem (Ativa automaticamente no PythonJet)
# if CLOUD_SQL_CONNECTION_NAME:
#     DATABASES['default'] = {
#         'ENGINE': 'django.db.backends.postgresql',
#         'HOST': f'/cloudsql/{CLOUD_SQL_CONNECTION_NAME}',
#         'NAME': config('DB_NAME'),
#         'USER': config('DB_USER'),
#         'PASSWORD': config('DB_PASSWORD'),
#         'PORT': '',
#         'CONN_MAX_AGE': 600,
#         'CONN_HEALTH_CHECKS': True,
#     }

# # 4. SEGURANÇA (Evitar erro 403 no Login)
# CSRF_TRUSTED_ORIGINS = ['https://*.run.app'] # Permite domínios do Cloud Run