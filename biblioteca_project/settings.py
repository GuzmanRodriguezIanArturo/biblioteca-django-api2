from pathlib import Path
from datetime import timedelta 
# Se eliminó el import de decouple que causaba el error

"""
Django settings for biblioteca_project project.
"""
# BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CONFIGURACIÓN DE SEGURIDAD ---
SECRET_KEY = 'django-insecure-4(w-#6-sr1^nn4-p6!ixu70n9&n@k!g5z2=&4m60n=nom69@f-'
DEBUG = True  # Cambiado de config('DEBUG') a valor directo
ALLOWED_HOSTS = [] # Cambiado de config('ALLOWED_HOSTS', cast=Csv()) a valor directo


# Application definition

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'oauth2_provider',
    'channels',
    
    # Third-party apps
    'rest_framework',
    'corsheaders',
    'django_filters',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django_extensions',
    'graphene_django',
    
    # Tu aplicación
    'libros',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'libros.middleware.SecurityMiddleware',
    'libros.middleware.RateLimitMiddleware',
]

ROOT_URLCONF = 'biblioteca_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # ← AGREGAR esto
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'biblioteca_project.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'biblioteca_uni4',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306', # Asegúrate de que tu MySQL realmente use el 3308, si no cambia a 3306
        'OPTIONS': {
            'charset': 'utf8mb4',
            # SE ELIMINÓ: 'init_command': "SET sql_mode='STRICT_TRANS_TABLES', innodb_large_prefix=1",
        },
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
LANGUAGE_CODE = 'en-MX'
TIME_ZONE = 'America/Hermosillo'
USE_I18N = True
USE_TZ = True


# Static files
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================
# CONFIGURACIÓN DE CORS
# ==============================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://tudominio.com",
    "https://www.tudominio.com",
]
CORS_ALLOW_CREDENTIALS = True

# Headers permitidos
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
# =======================
# REST FRAMEWORK CONFIG
# =======================

# =======================
# REST FRAMEWORK CONFIG
# =======================


REST_FRAMEWORK = {
    # AUTENTICACIÓN: Qué métodos acepta tu API
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',  # ← PON ESTE PRIMERO
        'rest_framework_simplejwt.authentication.JWTAuthentication',   # JWT (Token moderno)
        'rest_framework.authentication.TokenAuthentication',           # Token tradicional
        'rest_framework.authentication.SessionAuthentication',         # Sesión (para admin)
    ],
    
    # PERMISOS: Qué pueden hacer los usuarios
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    # ... resto de tu configuración

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    
   'DEFAULT_THROTTLE_CLASSES': [
        'libros.throttles.BurstRateThrottle',
        'libros.throttles.SustainedRateThrottle',
    ],
    
    'DEFAULT_THROTTLE_RATES': {
        'burst': '60/min',        # 60 por minuto
        'sustained': '1000/day',  # 1000 por día
        'anon_burst': '20/min',   # Anónimos: 20 por minuto
        'premium': '10000/day',   # Premium: 10000 por día
    }
}
# =======================
# SIMPLE JWT CONFIG
# =======================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
}

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# DJANGO ALLAUTH CONFIG
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_EMAIL_VERIFICATION = 'optional'
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'

# Proveedores OAuth configurados
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': 'GOOGLE_CLIENT_ID',
            'secret': 'GOOGLE_CLIENT_SECRET',
            'key': ''
        }
    }
}

# OAuth2 Provider Settings
OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read scope - Permite leer datos',
        'write': 'Write scope - Permite escribir datos',
        'groups': 'Access to groups - Acceso a grupos de usuario'
    },
    'ACCESS_TOKEN_EXPIRE_SECONDS': 3600,  # 1 hora
    'REFRESH_TOKEN_EXPIRE_SECONDS': 86400,  # 1 día
    'AUTHORIZATION_CODE_EXPIRE_SECONDS': 600,  # 10 minutos
    'ROTATE_REFRESH_TOKEN': True,
}

# ASGI Application
ASGI_APPLICATION = 'biblioteca_project.asgi.application'

# Channel Layers - Opción 1: Con Redis (RECOMENDADO para producción)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}


# GraphQL Settings
GRAPHENE = {
    'SCHEMA': 'libros.schema.schema',
    'MIDDLEWARE': [
        'graphene_django.debug.DjangoDebugMiddleware',
    ],
}

# Solo para PRODUCCIÓN (no desarrollo)
if not DEBUG:
    # Forzar HTTPS
    SECURE_SSL_REDIRECT = True
    
    # Cookies seguras
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Headers de seguridad
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Proxy SSL headers
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Orígenes confiables para CSRF
CSRF_TRUSTED_ORIGINS = [
    "https://tudominio.com",
    "https://www.tudominio.com",
]


# Cookie CSRF segura en producción
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = 'Strict'