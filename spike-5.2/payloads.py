import datetime
import platform
import httpx

print("TIMESTAMP Y ENTORNO:")
print(datetime.datetime.now().isoformat(), platform.node(), platform.platform())
print("-" * 60)

CASOS = {
    "1_ok": {"herramienta_id": 1, "solicitante": "Ana Ruiz", "fecha_prestamo": "2026-08-07", "dias": 3},
    "2_falta_campo": {"herramienta_id": 1, "solicitante": "Ana Ruiz", "dias": 3},
    "3_tipo_malo": {"herramienta_id": "uno", "solicitante": "Ana Ruiz", "fecha_prestamo": "2026-08-07", "dias": 3},
    "4_fuera_rango": {"herramienta_id": 1, "solicitante": "Ana Ruiz", "fecha_prestamo": "2026-08-07", "dias": -5},
    "5_campo_extra": {"herramienta_id": 1, "solicitante": "Ana Ruiz", "fecha_prestamo": "2026-08-07", "dias": 3, "admin": True},
    "6_fecha_basura": {"herramienta_id": 1, "solicitante": "Ana Ruiz", "fecha_prestamo": "ayer", "dias": 3},
}

SERVIDORES = [
    ("FastAPI (Pydantic)", "http://127.0.0.1:8002"),
    ("Flask (Manual)", "http://127.0.0.1:8000"),
]

for nombre_serv, base in SERVIDORES:
    print(f"=== PRUEBAS CONTRA {nombre_serv} ({base}) ===")
    for caso_nombre, cuerpo in CASOS.items():
        try:
            r = httpx.post(f"{base}/api/prestamos", json=cuerpo, timeout=5)
            print(f"[{caso_nombre}] HTTP {r.status_code} | Resp: {r.text[:110]}")
        except Exception as e:
            print(f"[{caso_nombre}] ERROR CONEXION: {e}")
    print("\n")