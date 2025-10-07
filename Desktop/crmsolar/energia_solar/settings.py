# energia_solar/settings.py
import os
from pathlib import Path
import dj_database_url
import environ

# Caminho base do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Lendo variáveis do .env
env = environ.Env(DEBUG=(bool, False))
env.read_env(os.path.join(BASE_DIR, '.env'))

GEMINI_API_KEY = env('GEMINI_API_KEY', default=None) 

if not GEMINI_API_KEY:
    print("AVISO: A variável GEMINI_API_KEY não foi encontrada no arquivo .env")
# Chaves Stripe

STRIPE_SECRET_KEY = env('SECRET_KEY_STRIPE', default='sua_chave_secreta_stripe')
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY', default='pk_test_SUA_CHAVE_PUBLICA_STRIPE_PADRAO')

# Configurações básicas do Django
SECRET_KEY = env('SECRET_KEY', default='sua-chave-secreta-padrao-para-desenvolvimento')
DEBUG = True  # Ajuste conforme necessário

# Hosts permitidos
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'loja.solarhub.com.br', 'solarhub.com.br', 'www.solarhub.com.br', 'f08e3a9c8b36.ngrok-free.app']

# Modelo de usuário customizado
AUTH_USER_MODEL = 'solar.Usuario'

# Aplicativos instalados
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'solar',
    'widget_tweaks',
    'produtos',
    'pagamento',
    'django_admin_logs',
    'django.contrib.sites',
    'mp_integracao',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django_extensions',
    'django.contrib.humanize', 
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)


# URLs de login/logout
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'produtos:home'
LOGOUT_REDIRECT_URL = 'login'
ACCOUNT_LOGOUT_REDIRECT_URL = 'login'

# Configurações do Allauth
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_USERNAME_REQUIRED = True

SITE_ID = 1

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

ROOT_URLCONF = 'energia_solar.urls'

# Templates
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

# Configuração de email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp-mail.outlook.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=False)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='')




# DATABASES = {
#     'default': env.db_url('DATABASE_URL')
# }

# Validação de senha
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://solarhub.com.br',
    'https://www.solarhub.com.br',
    'https://loja.solarhub.com.br',
    'https://f08e3a9c8b36.ngrok-free.app' ,
]
# URL pública do ngrok (para testes Mercado Pago)
NGROK_URL = 'f08e3a9c8b36.ngrok-free.app'




# ------------------------------------------------------------------
# MERCADO PAGO CONFIGURAÇÕES
# ------------------------------------------------------------------
MERCADO_PAGO_PUBLIC_KEY = env('MERCADO_PAGO_PUBLIC_KEY', default='')
MERCADO_PAGO_ACCESS_TOKEN = env('MERCADO_PAGO_ACCESS_TOKEN', default='')
MERCADO_PAGO_CLIENT_ID = env('MERCADO_PAGO_CLIENT_ID', default='')
MERCADO_PAGO_CLIENT_SECRET = env('MERCADO_PAGO_CLIENT_SECRET', default='')




# The commented out section `# DATABASES = { ... }` is an example configuration for setting up a
# SQLite database in a Django project.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'), # This is the corrected line
    }
}