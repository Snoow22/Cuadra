from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_GET
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import bloqueo


@require_GET
@ensure_csrf_cookie
def csrf(request):
    """Entrega la cookie `csrftoken`; el front la reenvía en la cabecera X-CSRFToken."""
    return HttpResponse(status=204)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False)


# DRF exime de CSRF a las vistas sin sesión; el login lo exige igual contra login CSRF (ADR-008).
@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        datos = LoginSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        email = datos.validated_data["email"]

        if bloqueo.esta_bloqueado(email):
            return Response(
                {"detail": "Demasiados intentos fallidos. Intenta de nuevo en un minuto."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        usuario = authenticate(request, email=email, password=datos.validated_data["password"])
        if usuario is None:
            bloqueo.registrar_fallo(email)
            # Mismo mensaje si falla el email, la contraseña o el usuario está inactivo.
            return Response(
                {"detail": "Credenciales inválidas."}, status=status.HTTP_401_UNAUTHORIZED
            )

        login(request, usuario)
        return Response({"id": usuario.pk, "nombre": usuario.nombre, "rol": usuario.rol})
