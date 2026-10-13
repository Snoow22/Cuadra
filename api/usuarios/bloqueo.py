"""Bloqueo temporal del login tras varios fallos seguidos (HU-01, ADR-008)."""

from datetime import timedelta

from django.db.models.functions import Now

from .models import IntentoLoginFallido

MAX_FALLOS = 5
VENTANA = timedelta(minutes=1)


def _clave(email):
    # Sin distinguir mayúsculas, para que "Ana@x.cl" y "ana@x.cl" sumen al mismo contador.
    return email.strip().lower()


def registrar_fallo(email):
    # Los fallos fuera de la ventana ya no cuentan; se purgan para que la tabla no crezca.
    IntentoLoginFallido.objects.filter(creado_en__lt=Now() - VENTANA).delete()
    IntentoLoginFallido.objects.create(email=_clave(email))


def esta_bloqueado(email):
    # shortcut: leer y luego registrar no es atómico; una ráfaga en paralelo puede colar
    # algunos intentos de más antes del bloqueo. Si importa, serializar con un lock por email.
    recientes = IntentoLoginFallido.objects.filter(
        email=_clave(email), creado_en__gte=Now() - VENTANA
    )
    return recientes.count() >= MAX_FALLOS
