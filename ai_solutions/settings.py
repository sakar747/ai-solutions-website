import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(*names, default="False"):
    for name in names:
        value = os.environ.get(name)
        if value is not None:
            return value.lower() == "true"
    return default.lower() == "true"


def env_value(*names, default=None):
    for name in names:
        value = os.environ.get(name)
        if value not in (None, ""):
            return value
    return default


# Security settings
SECRET_KEY = env_value(
    "DJANGO_SECRET_KEY",
    "SECRET_KEY",
    default="dev-secret-key-change-before-submission",
)
DEBUG = env_bool("DJANGO_DEBUG", "DEBUG", default="True")

# Render domain is included by default so the deployed site does not show DisallowedHost.
ALLOWED_HOSTS = env_value(
    "DJANGO_ALLOWED_HOSTS",
    default="127.0.0.1,localhost,.onrender.com",
).split(",")

# Required for POST forms on Render when DEBUG=False.
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in env_value(
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        default="https://*.onrender.com",
    ).split(",")
    if origin.strip()
]

INSTALLED_APPS = [
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "website",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "ai_solutions.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ai_solutions.wsgi.application"

# The prototype uses PyMongo directly for project data. Django sessions use signed cookies,
# so no SQL database is required for the custom admin login. SQLite is only kept so Django's
# checks can run normally and optional local commands still work.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

LANGUAGE_CODE = "en-us"
TIME_ZONE = env_value("DJANGO_TIME_ZONE", default="Asia/Kathmandu")
USE_I18N = True
USE_TZ = True

# Static files for local development and Render deployment.
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "website" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# MongoDB settings. Use MongoDB Atlas on Render by setting MONGO_URI and MONGO_DB_NAME.
# If MongoDB is unavailable, the app falls back to a local JSON store for demonstration.
MONGO_URI = env_value("MONGO_URI", "MONGODB_URI", default="mongodb://localhost:27017")
MONGO_DB_NAME = env_value("MONGO_DB_NAME", "MONGODB_NAME", default="ai_solutions_db")

# Prototype admin credentials. Set these in Render Environment Variables.
ADMIN_USERNAME = env_value("ADMIN_USERNAME", "STAFF_USERNAME", default="admin")
ADMIN_PASSWORD = env_value("ADMIN_PASSWORD", "STAFF_PASSWORD", default="admin123")

# Security header for HTTPS behind Render's proxy.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
