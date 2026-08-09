import asyncio
import datetime
import platform
import time
import httpx

# IMPRESION OBLIGATORIA DE EVIDENCIA NO FALSIFICABLE
print("TIMESTAMP Y ENTORNO:")
print(datetime.datetime.now().isoformat(), platform.node(), platform.platform())
print("-" * 60)

async def medir(url, nombre, n=20):
    t0 = time.perf_counter()
    async with httpx.AsyncClient(timeout=30) as client:
        respuestas = await asyncio.gather(*[client.get(url) for _ in range(n)])
    
    exitosas = sum(r.status_code == 200 for r in respuestas)
    tiempo_total = round(time.perf_counter() - t0, 2)
    print(f"[{nombre}] {url}")
    print(f"  Peticiones completadas: {exitosas}/{n}")
    print(f"  Tiempo total: {tiempo_total} segundos\n")

async def main():
    print("--- INICIANDO PRUEBA DE CARGA (20 PETICIONES CONCURRENTES) ---\n")
    await medir("http://127.0.0.1:8001/lento", "1. WSGI (Flask + Gunicorn 1 worker)")
    await medir("http://127.0.0.1:8002/lento", "2. ASGI (FastAPI + Uvicorn 1 worker)")

if __name__ == "__main__":
    asyncio.run(main())