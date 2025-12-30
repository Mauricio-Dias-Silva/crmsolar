import os
from pathlib import Path
import dj_database_url
import environ

# Caminho base do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Inicializa o environ
env = environ.Env()
# Tenta ler o arquivo .env se ele existir (ambiente local)
env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):
    env.read_env(env_file)

# --- CONFIGURAÇÕES DE SEGURANÇA ---

# DEBUG: Deve ser False em produção. Lemos como booleano.
# Se a variável não existir, assume False por segurança.
DEBUG = env.bool('DEBUG', default=False)

# SECRET_KEY: Crítica. Deve vir do ambiente.
SECRET_KEY = env('SECRET_KEY', default='sua-chave-secreta-padrao-para-desenvolvimento')

# ALLOWED_HOSTS: Permite hosts específicos ou '*' em ambientes controlados
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])


# Lógica para adicionar dinamicamente o domínio do Cloud Run à lista de confiáveis
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME') # Exemplo genérico
CLOUD_RUN_SERVICE_URL = os.environ.get('CLOUD_RUN_SERVICE_URL') # Se você injetar essa variável
# CSRF: Domínios confiáveis para evitar bloqueios de formulário

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'https://solarhub.com.br',
    'https://www.solarhub.com.br',
    'https://loja.solarhub.com.br',
])

# Adiciona automaticamente a URL do serviço se ela estiver disponível no ambiente
# (Você precisaria garantir que essa variável seja setada no deploy)
SERVICE_URL = os.environ.get('SERVICE_URL')
if SERVICE_URL:
    CSRF_TRUSTED_ORIGINS.append(SERVICE_URL)

# --- APPS E MIDDLEWARE ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # WhiteNoise deve rodar antes dos staticfiles do Django se usar runserver_nostatic
    'whitenoise.runserver_nostatic', 
    'django.contrib.staticfiles',
    
    # Seus Apps
    'solar',
    'widget_tweaks',
    'produtos',
    'pagamento',
    # 'django_admin_logs', # Removido para evitar erros de build/runtime
    'django.contrib.sites',
    'mp_integracao',
    
    # Bibliotecas de Terceiros
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise DEVE estar logo após SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
]

ROOT_URLCONF = 'energia_solar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'solar', 'templates'),
            os.path.join(BASE_DIR, 'produtos', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'energia_solar.wsgi.application'

# ==============================================================================
# BANCO DE DADOS (CONFIGURAÇÃO CLOUD RUN / SOCKET)
# ==============================================================================

# Verifica se estamos no Cloud Run com Cloud SQL ativado
# A flag --add-cloudsql-instances define esta variável automaticamente
CLOUD_SQL_CONNECTION_NAME = env('CLOUD_SQL_CONNECTION_NAME', default=None)

if CLOUD_SQL_CONNECTION_NAME:
    # --- AMBIENTE DE PRODUÇÃO (CLOUD RUN) ---
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            # Caminho do Socket UNIX (Fundamental para conexão rápida e sem erro de porta)
            'HOST': f'/cloudsql/{CLOUD_SQL_CONNECTION_NAME}',
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASSWORD'),
            # Porta fica vazia ao usar socket
            'PORT': '',
            'CONN_MAX_AGE': 600,
            'CONN_HEALTH_CHECKS': True,
        }
    }
else:
    # --- AMBIENTE LOCAL (SQLite ou Postgres Local) ---
    # Tenta usar DATABASE_URL se definida (ex: docker-compose), senão usa SQLite
    DATABASES = {
        'default': env.db_url(
            'DATABASE_URL', 
            default=f'sqlite:///{BASE_DIR}/db.sqlite3'
        )
    }

# ==============================================================================
# ARQUIVOS ESTÁTICOS (WHITENOISE)
# ==============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Armazenamento otimizado para produção (Compressão e Caching)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- OUTRAS CONFIGURAÇÕES ---

# Modelo de usuário
AUTH_USER_MODEL = 'solar.Usuario'

# Autenticação
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Allauth
SITE_ID = 1
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'produtos:home'
LOGOUT_REDIRECT_URL = 'login'
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_LOGOUT_REDIRECT_URL = 'login'

# Sessão
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = not DEBUG # True em produção (HTTPS), False em dev
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp-mail.outlook.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=False)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='')

# API Keys
GEMINI_API_KEY = env('GEMINI_API_KEY', default=None)
STRIPE_SECRET_KEY = env('SECRET_KEY_STRIPE', default='')
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY', default='')
MERCADO_PAGO_PUBLIC_KEY = env('MERCADO_PAGO_PUBLIC_KEY', default='')
MERCADO_PAGO_ACCESS_TOKEN = env('MERCADO_PAGO_ACCESS_TOKEN', default='')
MERCADO_PAGO_CLIENT_ID = env('MERCADO_PAGO_CLIENT_ID', default='')
MERCADO_PAGO_CLIENT_SECRET = env('MERCADO_PAGO_CLIENT_SECRET', default='')
NGROK_URL = env('NGROK_URL', default='')
