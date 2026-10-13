import pytest
from django.db import OperationalError


@pytest.mark.django_db
def test_health_responde_ok_con_la_base_arriba(client):
    respuesta = client.get("/health")

    assert respuesta.status_code == 200
    assert respuesta.json()["status"] == "ok"
    assert respuesta.json()["db"] == "up"


def test_health_responde_503_si_la_base_no_responde(client, monkeypatch):
    class ConexionCaida:
        def cursor(self):
            raise OperationalError("base de datos caída")

    monkeypatch.setattr("config.views.connection", ConexionCaida())

    respuesta = client.get("/health")

    assert respuesta.status_code == 503
    assert respuesta.json()["db"] == "down"
