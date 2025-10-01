# from .base import *

DEBUG = True

# # Opcional: redefinir banco (não é necessário se já está no base.py)
# # DATABASES já está herdado



from .base import *

# DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Banco de dados local (SQLite para dev)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Desativar e-mails reais no dev
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS (para frontend local)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]