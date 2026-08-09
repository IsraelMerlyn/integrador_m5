# ADR 5.1 — Modelo de Ejecución del Servidor Web (WSGI vs ASGI)

**Contexto:** Se requiere definir el arquitectura de servidor de aplicaciones capaz de manejar peticiones concurrentes con operaciones de I/O de alta latencia (~0.5s) sin bloquear el procesamiento.

**Opciones:** 
- Opción A: Servidor WSGI síncrono (Flask + Gunicorn, 1 worker).
- Opción B: Servidor ASGI asíncrono (FastAPI + Uvicorn, 1 worker).

**Criterio:** Tiempo total en segundos para completar 20 peticiones HTTP concurrentes con 1 solo worker asignado.

**Evidencia:** 20 peticiones concurrentes a endpoint de 0.5s (Log crudo en `spike-5.1/salida_cruda.log`):
- Opción A (WSGI): <INSERTA_SEGUNDOS_WSGI> segundos.
- Opción B (ASGI): <INSERTA_SEGUNDOS_ASGI> segundos.

**Decisión:** Opción B (ASGI) porque bajo la presencia de latencia de I/O no bloqueante, un solo worker ASGI completa el lote en ~<INSERTA_SEGUNDOS_ASGI>s frente a los ~<INSERTA_SEGUNDOS_WSGI>s requeridos por WSGI donde las peticiones se encolan secuencialmente.

**Consecuencias:** Todo el código que consulte base de datos o APIs externas en rutas asíncronas debe usar librerías compatibles con `async/await` (ej. `httpx`, `asyncpg`). Un `time.sleep()` accidental dentro de un `async def` bloquearía el bucle de eventos completo.

**Me haría cambiar de opinión:** Si la aplicación fuera puramente intensiva en CPU o dependiera exclusivamente de drivers de base de datos ORM síncronos sin soporte asíncrono, WSGI con múltiples workers de procesos sería la arquitectura más estable.