from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_GET
from rest_framework import serializers, status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import bloqueo
from .models import Usuario
from .permisos import EsAdmin


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
        email = datos.validated_data["email"].strip().lower()

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


class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = Usuario
        fields = ["id", "email", "nombre", "rol", "password"]
        read_only_fields = ["id"]

    def validate_email(self, email):
        # Antes de crear: el UniqueValidator automático distingue mayúsculas y no vería el choque.
        email = email.strip().lower()
        if Usuario.objects.filter(email=email).exists():
            raise serializers.ValidationError("Ya existe un usuario con ese email.")
        return email

    def validate(self, datos):
        # Con el usuario en memoria, el validador de similitud compara contra email y nombre.
        try:
            validate_password(
                datos["password"], Usuario(email=datos["email"], nombre=datos["nombre"])
            )
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)}) from None
        return datos

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)


class UsuarioCreateView(CreateAPIView):
    """Crear usuarios: solo admin (HU-02)."""

    permission_classes = [EsAdmin]
    serializer_class = UsuarioSerializer
