import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from rest_framework.views import APIView

from usuarios.models import Usuario
from usuarios.permisos import EsAdmin, EsOperadorOAdmin

pytestmark = pytest.mark.django_db

NUEVO = {"email": "nuevo@cuadra.cl", "nombre": "Nuevo", "password": "clave-larga-123"}


class VistaAnular(APIView):
    """Stand-in de 'anular documentos' (HU-10/14) hasta que existan."""

    permission_classes = [EsAdmin]

    def post(self, request):
        return Response({"ok": True})


class VistaMovimientos(APIView):
    """Stand-in de movimientos, compras y ventas."""

    permission_classes = [EsOperadorOAdmin]

    def post(self, request):
        return Response({"ok": True})


@pytest.fixture
def admin():
    return Usuario.objects.create_user("admin@cuadra.cl", "Admin", "x" * 10, rol="admin")


@pytest.fixture
def operador():
    return Usuario.objects.create_user("op@cuadra.cl", "Op", "x" * 10, rol="operador")


def llamar(vista, usuario):
    peticion = APIRequestFactory().post("/")
    if usuario:
        force_authenticate(peticion, user=usuario)
    return vista.as_view()(peticion)


def cliente(usuario=None):
    client = APIClient()
    if usuario:
        client.force_login(usuario)
    return client


def test_operador_no_puede_crear_usuarios(operador):
    respuesta = cliente(operador).post("/usuarios", NUEVO, format="json")

    assert respuesta.status_code == 403
    assert not Usuario.objects.filter(email=NUEVO["email"]).exists()


def test_operador_no_puede_anular_documentos(operador):
    assert llamar(VistaAnular, operador).status_code == 403


def test_operador_puede_registrar_movimientos_compras_y_ventas(operador):
    assert llamar(VistaMovimientos, operador).status_code == 200


def test_admin_puede_crear_usuarios(admin):
    respuesta = cliente(admin).post("/usuarios", {**NUEVO, "rol": "operador"}, format="json")

    assert respuesta.status_code == 201
    assert "password" not in respuesta.json()
    creado = Usuario.objects.get(email=NUEVO["email"])
    assert creado.rol == "operador"
    assert creado.check_password(NUEVO["password"])


def test_admin_puede_anular_y_registrar(admin):
    assert llamar(VistaAnular, admin).status_code == 200
    assert llamar(VistaMovimientos, admin).status_code == 200


def test_sin_sesion_recibe_403_segun_adr_008():
    assert cliente().post("/usuarios", NUEVO, format="json").status_code == 403
    assert llamar(VistaAnular, None).status_code == 403
    assert llamar(VistaMovimientos, None).status_code == 403


def test_crear_usuario_con_email_repetido_da_400(admin):
    cliente(admin).post("/usuarios", NUEVO, format="json")

    respuesta = cliente(admin).post("/usuarios", NUEVO, format="json")

    assert respuesta.status_code == 400
    assert Usuario.objects.filter(email=NUEVO["email"]).count() == 1


@pytest.mark.parametrize(
    "password",
    ["corta1", "12345678901", "password123", "nuevo@cuadra.cl"],
    ids=["muy_corta", "solo_numeros", "comun", "parecida_al_email"],
)
def test_contrasena_debil_da_400_y_no_crea_el_usuario(admin, password):
    respuesta = cliente(admin).post("/usuarios", {**NUEVO, "password": password}, format="json")

    assert respuesta.status_code == 400
    assert respuesta.json()["password"]
    assert not Usuario.objects.filter(email=NUEVO["email"]).exists()


def test_crear_usuario_con_email_repetido_en_otra_mayuscula_da_400(admin):
    cliente(admin).post("/usuarios", NUEVO, format="json")

    respuesta = cliente(admin).post(
        "/usuarios", {**NUEVO, "email": NUEVO["email"].upper()}, format="json"
    )

    assert respuesta.status_code == 400
    assert Usuario.objects.filter(email__iexact=NUEVO["email"]).count() == 1


def test_contrasena_parecida_al_nombre_da_400(admin):
    datos = {**NUEVO, "nombre": "Beatriz", "password": "beatriz2026"}

    respuesta = cliente(admin).post("/usuarios", datos, format="json")

    assert respuesta.status_code == 400
    assert respuesta.json()["password"]


def test_crear_usuario_exige_token_csrf(admin):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    sin_token = client.post("/usuarios", NUEVO, format="json")

    assert sin_token.status_code == 403
    assert "CSRF" in sin_token.json()["detail"]
    assert not Usuario.objects.filter(email=NUEVO["email"]).exists()

    # Con el token la misma petición pasa: el 403 anterior era por CSRF y no por el rol.
    client.get("/auth/csrf")
    token = client.cookies["csrftoken"].value
    con_token = client.post("/usuarios", NUEVO, format="json", headers={"X-CSRFToken": token})
    assert con_token.status_code == 201
