# from .base import *

# DEBUG = False

# ALLOWED_HOSTS = ['seu-dominio.com', 'www.seu-dominio.com']

from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '']
# ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Segurança HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Cache estático
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CORS restrito
CORS_ALLOWED_ORIGINS = [
    "https://edufuturo.pro",
    "https://www.edufuturo.pro",

]

# Sentry (opcional)
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=config('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
)