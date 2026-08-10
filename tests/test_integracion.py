import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from app import app, init_db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"
    init_db()
    with app.test_client() as client:
        yield client

def test_healthcheck(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json["status"] == "healthy"

def test_listar_prestamos_paginado(client):
    res = client.get("/api/prestamos")
    assert res.status_code == 200
    assert "count" in res.json
    assert "results" in res.json

def test_crear_prestamo_sin_auth_retorna_401(client):
    res = client.post("/api/prestamos", json={"herramienta_id": 1, "solicitante": "Ana Ruiz", "dias": 3})
    assert res.status_code == 401

def test_crear_prestamo_con_auth_exito(client):
    client.post("/api/login", json={"username": "ana_ruiz", "role": "user"})
    res = client.post("/api/prestamos", json={"herramienta_id": 1, "solicitante": "Ana Ruiz", "dias": 5})
    assert res.status_code == 201
    assert res.json["solicitante"] == "Ana Ruiz"

def test_crear_prestamo_validacion_dias_invalido(client):
    client.post("/api/login", json={"username": "ana_ruiz", "role": "user"})
    res = client.post("/api/prestamos", json={"herramienta_id": 1, "solicitante": "Ana Ruiz", "dias": -5})
    assert res.status_code == 400

def test_eliminar_prestamo_usuario_normal_retorna_403(client):
    client.post("/api/login", json={"username": "ana_ruiz", "role": "user"})
    res = client.delete("/api/prestamos/1")
    assert res.status_code == 403

def test_eliminar_prestamo_admin_exito(client):
    client.post("/api/login", json={"username": "admin", "role": "admin"})
    p_res = client.post("/api/prestamos", json={"herramienta_id": 1, "solicitante": "Para Eliminar", "dias": 2})
    p_id = p_res.json["id"]
    
    del_res = client.delete(f"/api/prestamos/{p_id}")
    assert del_res.status_code == 200