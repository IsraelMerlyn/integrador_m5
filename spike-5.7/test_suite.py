import os
import sys
import pytest

# Asegurar importación del módulo local
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app_logic import ServicioPrestamos

@pytest.fixture
def servicio(request):
    bug_flags = getattr(request, "param", {})
    return ServicioPrestamos(bug_flags=bug_flags)

# --- SUITE A: PRUEBAS UNITARIAS ---
def test_unit_validar_dias_negativos_rechazado(servicio):
    assert servicio.validar_prestamo(-5, "Ana Ruiz") is False

def test_unit_calcular_fecha_devolucion_correcta(servicio):
    assert servicio.calcular_fecha_devolucion(10, 5) == 15

# --- SUITE B: PRUEBAS DE INTEGRACIÓN ---
def test_integ_crear_prestamo_datos_invalidos_retorna_400(servicio):
    status, body = servicio.crear_prestamo_endpoint(
        {"dias": -5, "solicitante": "Ana Ruiz"},
        rol_usuario="user",
        usuario_actual="Ana Ruiz"
    )
    assert status == 400

def test_integ_rbac_usuario_no_puede_crear_a_nombre_de_otro(servicio):
    status, body = servicio.crear_prestamo_endpoint(
        {"dias": 5, "solicitante": "Carlos Gómez"},
        rol_usuario="user",
        usuario_actual="Ana Ruiz"
    )
    assert status == 403

def test_integ_filtrar_prestamos_por_usuario(servicio):
    datos = [
        {"id": 1, "solicitante": "Ana Ruiz"},
        {"id": 2, "solicitante": "Carlos Gómez"}
    ]
    resultado = servicio.filtrar_prestamos(datos, "Ana Ruiz")
    assert len(resultado) == 1
    assert resultado[0]["solicitante"] == "Ana Ruiz"

def test_integ_crear_prestamo_exitoso_calcula_devolucion(servicio):
    status, body = servicio.crear_prestamo_endpoint(
        {"dias": 5, "solicitante": "Ana Ruiz"},
        rol_usuario="user",
        usuario_actual="Ana Ruiz"
    )
    assert status == 201
    assert body.get("dia_devolucion") == 15