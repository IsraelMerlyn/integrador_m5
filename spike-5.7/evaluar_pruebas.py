import datetime
import os
import platform
import sys
import pytest

# Asegurar importación del módulo local
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
if DIRECTORIO_ACTUAL not in sys.path:
    sys.path.insert(0, DIRECTORIO_ACTUAL)

from app_logic import ServicioPrestamos

def obtener_header():
    print("TIMESTAMP Y ENTORNO:")
    print(datetime.datetime.now().isoformat(), platform.node(), platform.platform())
    print("-" * 65)

FALLOS_INYECTADOS = [
    ("bug1_validacion_bypassed", "1. Bypass de validación (días <= 0)"),
    ("bug2_rbac_flaw", "2. Falla de RBAC (acceso a otro usuario)"),
    ("bug3_calculo_erroneo", "3. Cálculo erróneo de devolución"),
    ("bug4_filtro_roto", "4. Filtro roto (devuelve todo)"),
    ("bug5_status_code_malo", "5. Estado HTTP 200 en lugar de 400"),
]

def probar_fallo(flag_key, test_names):
    servicio_mutado = ServicioPrestamos(bug_flags={flag_key: True})
    atrapado = False
    
    # Evaluar Pruebas Unitarias
    if "unit" in test_names:
        try:
            assert servicio_mutado.validar_prestamo(-5, "Ana Ruiz") is False
            assert servicio_mutado.calcular_fecha_devolucion(10, 5) == 15
        except (AssertionError, KeyError):
            atrapado = True

    # Evaluar Pruebas de Integración
    if "integ" in test_names:
        try:
            st1, _ = servicio_mutado.crear_prestamo_endpoint({"dias": -5, "solicitante": "Ana Ruiz"}, "user", "Ana Ruiz")
            assert st1 == 400
            
            st2, _ = servicio_mutado.crear_prestamo_endpoint({"dias": 5, "solicitante": "Carlos Gómez"}, "user", "Ana Ruiz")
            assert st2 == 403
            
            res = servicio_mutado.filtrar_prestamos([{"id": 1, "solicitante": "Ana Ruiz"}, {"id": 2, "solicitante": "Carlos"}], "Ana Ruiz")
            assert len(res) == 1

            st3, body3 = servicio_mutado.crear_prestamo_endpoint({"dias": 5, "solicitante": "Ana Ruiz"}, "user", "Ana Ruiz")
            assert st3 == 201
            assert body3.get("dia_devolucion") == 15
        except (AssertionError, KeyError):
            atrapado = True

    return atrapado

def evaluar_suite_completa():
    print("=== EVALUACIÓN DE SUITE DE PRUEBAS MEDIANTE INYECCIÓN DE FALLOS ===")
    print(f"{'Fallo Inyectado':<40} | {'Atrapado Unitarias':<18} | {'Atrapado Integración':<18}")
    print("-" * 82)

    total_unit = 0
    total_integ = 0

    for flag_key, descripcion in FALLOS_INYECTADOS:
        atrapado_unit = probar_fallo(flag_key, ["unit"])
        atrapado_integ = probar_fallo(flag_key, ["integ"])

        if atrapado_unit: total_unit += 1
        if atrapado_integ: total_integ += 1

        print(f"{descripcion:<40} | {'SÍ' if atrapado_unit else 'NO':<18} | {'SÍ' if atrapado_integ else 'NO':<18}")

    print("-" * 82)
    print(f"TOTAL FALLOS ATRAPADOS: Unitarias = {total_unit}/5 ({total_unit*20}%) | Integración = {total_integ}/5 ({total_integ*20}%)")

if __name__ == "__main__":
    obtener_header()
    evaluar_suite_completa()
    print("\n--- EJECUTANDO COBERTURA DE CÓDIGO CON PYTEST-COV ---")
    ruta_test = os.path.join(DIRECTORIO_ACTUAL, "test_suite.py")
    pytest.main([ruta_test, "--cov=app_logic", "--cov-report=term-missing", "-q"])