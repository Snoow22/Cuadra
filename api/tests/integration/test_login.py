from datetime import timedelta

import pytest
from django.db import IntegrityError, transaction
from django.test import Client
from django.utils import timezone

from usuarios.bloqueo import MAX_FALLOS
from usuarios.models import IntentoLoginFallido, Usuario

pytestmark = pytest.mark.django_db

EMAIL = "ana@cuadra.cl"
CLAVE = "clave-correcta-123"


@pytest.fixture
def usuario():
    return Usuario.objects.create_user(EMAIL, "Ana", CLAVE)


def login(client, email=EMAIL, password=CLAVE):
    return client.post("/auth/login", {"email": email, "password": password}, "application/json")


def test_credenciales_validas_abren_sesion(client, usuario):
    respuesta = login(client)

    assert respuesta.status_code == 200
    assert respuesta.json() == {"id": usuario.pk, "nombre": "Ana", "rol": "operador"}
    assert "sessionid" in respuesta.cookies
    assert client.session["_auth_user_id"] == str(usuario.pk)


def test_la_contrasena_se_guarda_con_hash(usuario):
    assert usuario.password != CLAVE
    assert usuario.check_password(CLAVE)


def test_credenciales_invalidas_dan_401_sin_revelar_el_campo(client, usuario):
    mala_clave = login(client, password="otra")
    mal_email = login(client, email="nadie@cuadra.cl")

    assert mala_clave.status_code == mal_email.status_code == 401
    assert mala_clave.json() == mal_email.json() == {"detail": "Credenciales inválidas."}
    assert "sessionid" not in mala_clave.cookies


def test_usuario_inactivo_recibe_el_mismo_401(client, usuario):
    Usuario.objects.filter(pk=usuario.pk).update(activo=False)

    respuesta = login(client)

    assert respuesta.status_code == 401
    assert respuesta.json() == {"detail": "Credenciales inválidas."}


def test_cinco_fallos_en_un_minuto_bloquean_aunque_la_clave_sea_correcta(client, usuario):
    for _ in range(MAX_FALLOS):
        assert login(client, password="otra").status_code == 401

    respuesta = login(client)

    assert respuesta.status_code == 429
    assert "sessionid" not in respuesta.cookies


def test_el_bloqueo_no_distingue_mayusculas_en_el_email(client, usuario):
    for _ in range(MAX_FALLOS):
        login(client, email=EMAIL.upper(), password="otra")

    assert login(client).status_code == 429


def test_el_bloqueo_es_por_cuenta(client, usuario):
    otro = Usuario.objects.create_user("beto@cuadra.cl", "Beto", CLAVE)
    for _ in range(MAX_FALLOS):
        login(client, password="otra")

    respuesta = login(client, email=otro.email)

    assert respuesta.status_code == 200


def test_el_bloqueo_expira_pasado_un_minuto(client, usuario):
    for _ in range(MAX_FALLOS):
        login(client, password="otra")
    IntentoLoginFallido.objects.update(creado_en=timezone.now() - timedelta(seconds=61))

    assert login(client).status_code == 200


def test_cuatro_fallos_no_bloquean(client, usuario):
    for _ in range(MAX_FALLOS - 1):
        login(client, password="otra")

    assert login(client).status_code == 200


def test_login_exige_token_csrf():
    Usuario.objects.create_user(EMAIL, "Ana", CLAVE)
    client = Client(enforce_csrf_checks=True)

    assert login(client).status_code == 403

    assert client.get("/auth/csrf").status_code == 204
    token = client.cookies["csrftoken"].value
    respuesta = client.post(
        "/auth/login",
        {"email": EMAIL, "password": CLAVE},
        "application/json",
        headers={"X-CSRFToken": token},
    )
    assert respuesta.status_code == 200


def test_la_base_rechaza_un_rol_invalido(usuario):
    with pytest.raises(IntegrityError):
        Usuario.objects.filter(pk=usuario.pk).update(rol="dueño")


def test_create_superuser_crea_un_admin():
    admin = Usuario.objects.create_superuser("jefa@cuadra.cl", "Jefa", CLAVE)

    assert admin.rol == Usuario.Rol.ADMIN


def test_emails_que_solo_difieren_en_mayusculas_son_la_misma_cuenta():
    primero = Usuario.objects.create_user("Ana@X.cl", "Ana", CLAVE)

    assert primero.email == "ana@x.cl"
    with pytest.raises(IntegrityError), transaction.atomic():
        Usuario.objects.create_user("ana@x.cl", "Otra Ana", CLAVE)


def test_la_base_rechaza_emails_repetidos_sin_importar_mayusculas():
    Usuario.objects.create_user("ana@x.cl", "Ana", CLAVE)
    otro = Usuario.objects.create_user("beto@x.cl", "Beto", CLAVE)

    with pytest.raises(IntegrityError), transaction.atomic():
        Usuario.objects.filter(pk=otro.pk).update(email="ANA@X.CL")


def test_login_acepta_el_email_en_cualquier_mayuscula(client):
    Usuario.objects.create_user("Ana@X.cl", "Ana", CLAVE)

    assert login(client, email="ANA@x.CL").status_code == 200
