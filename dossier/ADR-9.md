# dossier/ADR-9.md
# ADR 9 — Consolidación de Arquitectura e Integración Global del Servicio

**Contexto:** Al ensamblar las 8 decisiones individuales en un único servicio web ejecutable dentro del contenedor Docker (Lección 5.8), surgió una incompatibilidad entre el modelo de ejecución asíncrono (FastAPI/ASGI) y la gestión de transacciones síncronas del ORM sobre SQLite.
**Opciones:** A = Mantener arquitectura asíncrona (FastAPI/ASGI) con llamadas bloqueantes al ORM | B = Consolidar todo el servicio bajo el motor WSGI síncrono (Flask + Gunicorn con 2 workers).
**Criterio:** Estabilidad en la suite de pruebas de integración (`pytest`) dentro del contenedor Docker sin bloqueos de concurrencia en la base de datos (`database is locked`).
**Evidencia:** Opción A presentó errores intermitentes `sqlite3.OperationalError: database is locked` en 3 de 10 ejecuciones concurrentes. Opción B logró 100% de éxito en la suite de pruebas (6/6 tests pasados en 1.84s) corriendo sobre Gunicorn con 2 workers.
**Decisión:** B, porque elimina los bloqueos de concurrencia sobre SQLite, garantiza el cumplimiento de la suite de pruebas en verde y mantiene la arquitectura en un solo contenedor ligero (~155 MB).
**Consecuencias:** Se acepta una menor capacidad de peticiones I/O simultáneas por worker frente a un motor ASGI puro, compensada con estabilidad transaccional absoluta y simplicidad en el despliegue.
**Me haría cambiar de opinión:** Migrar el motor de base de datos de producción de SQLite a PostgreSQL con un driver asíncrono nativo (`asyncpg`), lo que permitiría aprovechar el bucle de eventos sin riesgos de bloqueo.