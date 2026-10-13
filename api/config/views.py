from django.db import Error, connection
from django.http import JsonResponse

from . import __version__


def health(request):
    """Responde 200 si la API y la base de datos funcionan, 503 si la base no responde."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Error:
        return JsonResponse({"status": "error", "db": "down", "version": __version__}, status=503)
    return JsonResponse({"status": "ok", "db": "up", "version": __version__})
