from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
# El .env vive en la raíz del repositorio. Lo que ya esté definido en el entorno tiene prioridad.
environ.Env.read_env(BASE_DIR.parent / ".env")

# Sin valor por defecto: si falta, la aplicación no arranca.
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# Cada app se agrega junto con su primera historia de usuario (ADR-007).
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "rest_framework",
    "usuarios",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]

AUTH_USER_MODEL = "usuarios.Usuario"

# Sesión con cookie y CSRF (ADR-008). Para sumar tokens basta agregar su clase a la lista.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    # Sólo JSON: la API navegable de DRF necesita TEMPLATES y no se usa.
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}

# En producción (DEBUG=False) las cookies sólo viajan por HTTPS.
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = not DEBUG

# Se aplican al crear usuarios (POST /usuarios y createsuperuser), no al verificar el login.
_VALIDACION = "django.contrib.auth.password_validation"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": f"{_VALIDACION}.UserAttributeSimilarityValidator"},
    {"NAME": f"{_VALIDACION}.MinimumLengthValidator"},
    {"NAME": f"{_VALIDACION}.CommonPasswordValidator"},
    {"NAME": f"{_VALIDACION}.NumericPasswordValidator"},
]

ROOT_URLCONF = "config.urls"

DATABASES = {"default": env.db("DATABASE_URL")}

LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_TZ = True
