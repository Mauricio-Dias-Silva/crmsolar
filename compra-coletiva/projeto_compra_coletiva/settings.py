# projeto_compra_coletiva/settings.py

import os
from pathlib import Path
import dj_database_url
from decouple import config
from datetime import timedelta
from django.utils import timezone

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY para produção deve ser uma variável de ambiente!
SECRET_KEY = config('SECRET_KEY')

# DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)
DEBUG= True

# ALLOWED_HOSTS para Docker e Produção
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0', 'www.varejounido.com.br', 'varejounido.com.br'] # <--- Adicione seus domínios reais aqui
# Em produção, adicione seus domínios reais aqui (ex: 'nomedoseusite.com')

# --- Aplicativos instalados ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    # django-allauth
    'django.contrib.sites', # Necessário para allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # Seus apps do projeto
    'contas',
    'ofertas',
    'compras',
    'vendedores_painel',
    'pagamentos',
    'pedidos_coletivos',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',    
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # O middleware do allauth deve estar presente e sem erros de digitação.
    'allauth.account.middleware.AccountMiddleware', 
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# URL raiz
ROOT_URLCONF = 'projeto_compra_coletiva.urls'

# --- Configurações de Templates ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Pasta de templates globais
        'APP_DIRS': True, # Permite que o Django procure templates dentro das pastas 'templates' dos apps
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ofertas.context_processors.categorias_globais',
                'contas.context_processors.notificacoes_nao_lidas_globais'
            ],
        },
    },
]

WSGI_APPLICATION = 'projeto_compra_coletiva.wsgi.application'

# --- Configurações de Banco de Dados ---
# Configuração para PostgreSQL (usada por padrão ou via Docker)
# Esta configuração lê a variável de ambiente DATABASE_URL.
# O 'default' é usado se DATABASE_URL não estiver definida (ex: rodando runserver sem Docker)
# DATABASES = {
#     'default': dj_database_url.config(
#         default=config(
#             'DATABASE_URL', 
#             default='postgresql://django_user:django_password@localhost:5432/compra_coletiva_db'
#         ),
#         conn_max_age=600 # Tempo máximo de vida da conexão
#     )
# }

# --- CONFIGURAÇÃO PARA SQLITE (DESCOMENTE PARA USAR COM RUNSERVER SEM DOCKER) ---
# Se quiser usar SQLite (arquivo db.sqlite3) para testes rápidos sem Docker:
# 1. COMENTE TODO O BLOCO 'DATABASES' ACIMA (o do PostgreSQL).
# 2. DESCOMENTE O BLOCO 'DATABASES' ABAIXO.
# 3. Certifique-se de que não há DATABASE_URL no seu .env ou remova-o temporariamente.
# 4. Você precisará rodar python manage.py migrate novamente para criar o db.sqlite3.
#
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# --- Validações de Senha ---
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# --- Internacionalização ---
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True # Habilita suporte a fusos horários

# --- Arquivos Estáticos e de Mídia ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # Onde os arquivos estáticos serão coletados para produção

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles' # Onde os arquivos de mídia (uploads) serão armazenados

# --- Configurações do Modelo de Usuário Personalizado ---
AUTH_USER_MODEL = 'contas.Usuario'

# --- Tipo de Campo ID Padrão (para novas migrações) ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Configurações do django-allauth ---
SITE_ID = 1 # ID do site (necessário para allauth)

# Métodos de login permitidos (username, email, ou ambos)
ACCOUNT_AUTHENTICATION_METHOD = 'username_email' 
ACCOUNT_EMAIL_REQUIRED = True # E-mail é obrigatório no cadastro
ACCOUNT_USERNAME_REQUIRED = True # Username é obrigatório no cadastro
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5 # Limita tentativas de login
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300 # Tempo de bloqueio após limite (em segundos)
ACCOUNT_LOGOUT_ON_GET = True # Faz logout ao acessar a URL de logout via GET (mais simples)
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True # Exige digitar a senha duas vezes no registro
ACCOUNT_UNIQUE_EMAIL = True # Garante que cada email seja único
ACCOUNT_SESSION_REMEMBER = True # Habilita "Lembrar-me" no login
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[Meu Site Coletivo] ' # Prefixo para o assunto dos e-mails

# Configuração de verificação de e-mail (escolha uma):
ACCOUNT_EMAIL_VERIFICATION = 'none' # 'none': não exige verificação (bom para desenvolvimento rápido)
# ACCOUNT_EMAIL_VERIFICATION = 'optional' # 'optional': envia e-mail, mas não bloqueia login
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory' # 'mandatory': exige verificação para login (recomendado em produção)

# URLs de redirecionamento do allauth
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/contas/login/' # Onde o allauth redirecionará para login

# Caso tenha formulário de cadastro customizado (descomente e crie o form se for usar)
# ACCOUNT_FORMS = {
#     'signup': 'contas.forms.CustomSignupForm',
# }

# --- Configurações do Mercado Pago ---
MERCADO_PAGO_PUBLIC_KEY = config('MERCADO_PAGO_PUBLIC_KEY')
MERCADO_PAGO_ACCESS_TOKEN = config('MERCADO_PAGO_ACCESS_TOKEN')

# --- Configurações de E-mail (SMTP) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.mailtrap.io')
EMAIL_PORT = config('EMAIL_PORT', default=2525, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='webmaster@localhost')
SERVER_EMAIL = config('SERVER_EMAIL', default='root@localhost')

# --- Configurações do Celery ---
# Os valores 'redis' aqui referem-se ao nome do serviço 'redis' no docker-compose.yml (se estiver usando Docker)
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Sao_Paulo'
CELERY_ENABLE_UTC = False # Defina como False se CELERY_TIMEZONE for configurado

CELERY_BEAT_SCHEDULE = {
    'verificar-lotes-coletivos-pedidos': {
        'task': 'pedidos_coletivos.tasks.verificar_e_processar_lotes_coletivos', 
        'schedule': timezone.timedelta(minutes=5), # Executa a cada 5 minutos
    },
}

# --- Configurações de Logging (para ver logs no console) ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'pagamentos': { # Logger para o app de pagamentos
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'pedidos_coletivos.tasks': { # Logger para as tarefas do Celery de pedidos coletivos
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': { # Logger geral do Django
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
    'root': { # Logger raiz (para logs não capturados por outros loggers)
        'handlers': ['console'],
        'level': 'WARNING',
    },
}
