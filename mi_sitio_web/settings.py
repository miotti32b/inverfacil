import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# =====================
# LOAD ENV VARS
# =====================
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "insecure-key-dev")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()  # production / development

DEBUG = ENVIRONMENT == "development"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "invertiresfacil.com",
    "www.invertiresfacil.com",
]

railway = os.getenv("RAILWAY_PUBLIC_DOMAIN")
if railway:
    ALLOWED_HOSTS.append(railway)


CSRF_TRUSTED_ORIGINS = [
    "https://invertiresfacil.com",
    "https://www.invertiresfacil.com",
]

# =====================
# SECURITY
# =====================

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

    # HSTS (opcional, pero está bien)
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

else:
    SECURE_SSL_REDIRECT = False
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"


# =====================
# APPS
# =====================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "calculadora",

    # allauth
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
]

# =====================
# SITE_ID SITE_ID = int(os.getenv("SITE_ID", "3"))  # 3 por defecto (local)
# =====================

SITE_ID = 3


# =====================
# AUTH / ALLAUTH
# =====================

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# =====================
# GOOGLE / ALLAUTH
# =====================

LOGIN_URL = "/accounts/google/login/"

LOGIN_REDIRECT_URL = "/redirect-post-login/"    # Provisorio, lo definimos ahora
LOGOUT_REDIRECT_URL = "/"

ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
SOCIALACCOUNT_QUERY_EMAIL = True

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True
# =====================
# MIDDLEWARE
# =====================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "allauth.account.middleware.AccountMiddleware",
]

# =====================
# URLS / TEMPLATES
# =====================

ROOT_URLCONF = "mi_sitio_web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "calculadora" / "templates" / "calculadora",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mi_sitio_web.wsgi.application"

# =====================
# DATABASE
# =====================

if DEBUG:
    print("🔵 Using LOCAL SQLITE database")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    print("🟢 Using PRODUCTION Neon PostgreSQL")
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise Exception("❌ ERROR: No DATABASE_URL in production!")
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL, ssl_require=True)
    }

# =====================
# PASSWORDS
# =====================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =====================
# I18N
# =====================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# =====================
# STATIC / MEDIA
# =====================

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =====================
# MERCADOPAGO
# =====================


MERCADOPAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")



# =====================
# OPENAI
# =====================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

