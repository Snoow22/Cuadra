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

# Vacío a propósito: el modelo de usuario propio se define en la fase 2, antes de la primera
# migración (ADR-007). Cada app se agrega junto con su primera historia de usuario.
INSTALLED_APPS = []

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"

DATABASES = {"default": env.db("DATABASE_URL")}

LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_TZ = True
