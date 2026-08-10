# Servicio Web de Gestión de Préstamos y Control de Recursos — Módulo 5

[![Docker Build](https://img.shields.io/badge/Docker-Multi--Stage%20Build-blue?logo=docker)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)
[![Testing](https://img.shields.io/badge/Pytest-Suite%20Passing-brightgreen?logo=pytest)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Servicio web para la gestión, control y auditoría de préstamos de herramientas desarrollado como **Proyecto Integrador del Módulo 5** (Desarrollo de Aplicaciones Web usando Python). Integra una arquitectura web monolítica con renderizado en servidor (SSR), exposición de una API RESTful con paginación optimizada, mitigación de consultas N+1, seguridad basada en sesiones HttpOnly y contenedorización lista para producción.

---

## 📌 Enlaces de Entrega del Proyecto

* **URL Pública Viva (Despliegue en Producción):** `[https://prestamos-servicio-m5.onrender.com](https://prestamos-servicio-m5.onrender.com)`
* **Video de Defensa Técnico (5 minutos):** `[https://www.youtube.com/watch?v=DEMO_VIDEO_ID](https://www.youtube.com/watch?v=DEMO_VIDEO_ID)`

---

## 📂 Estructura del Repositorio

```text
integrador_m5/
├── README.md                 # Especificaciones del proyecto, arranque y entrega
├── Dockerfile                # Receta Docker Multi-Stage optimizada (155 MB, non-root)
├── autocritica.md            # Autocrítica de 3 preguntas de arquitectura
├── fuentes.md                # Bitácora de fuentes primarias y secundarias (≥12 fuentes)
├── dossier/                  # Dossier de Decisiones de Arquitectura (ADR)
│   ├── ADR-5.1.md            # Decisión: Modelo de Ejecución del Servidor (WSGI vs ASGI)
│   ├── ADR-5.2.md            # Decisión: Capa de API y Validación por Esquema
│   ├── ADR-5.3.md            # Decisión: Frontera Front-End / Back-End (SSR vs CSR)
│   ├── ADR-5.4.md            # Decisión: Migración de Esquema (Expand/Contract)
│   ├── ADR-5.5.md            # Decisión: Serialización, Paginación y Caza de N+1
│   ├── ADR-5.6.md            # Decisión: Identidad, Revocación y Cookies HttpOnly
│   ├── ADR-5.7.md            # Decisión: Red de Pruebas e Inyección de Fallos
│   ├── ADR-5.8.md            # Decisión: Empaquetado Docker y Producción
│   └── ADR-9.md              # ADR Integrador: Consolidación y Ajustes del Servicio
├── spike-5.1/ ... 5.8/       # Carpetas con código de investigación y logs crudos
├── src/                      # Código fuente principal de la aplicación web
│   ├── app.py                # Punto de entrada de la aplicación
│   ├── models.py             # Modelos de datos y mapeo relacional
│   └── views/                # Rutas de la API y vistas HTML
├── tests/                    # Suite de pruebas unitarias y de integración (pytest)
│   └── test_integracion.py
└── .git/                     # Historial de versiones con ≥15 commits distribuidos
```

---

## 🏛️ Resumen del Dossier de Decisiones (ADR)

| ADR | Tema de Decisión | Opción Seleccionada | Justificación Clave |
| :--- | :--- | :--- | :--- |
| **ADR 5.1** | Modelo de Ejecución | Servidor ASGI / Uvicorn (Spike) | Responde a 20 peticiones I/O en ~0.5s con 1 worker. |
| **ADR 5.2** | Capa de API | Validación Declarativa / Pydantic | Previene ataques de Mass Assignment (`admin: True`). |
| **ADR 5.3** | Frontera Front/Back | Renderizado en Servidor (SSR) | Entrega contenido en 1 viaje HTTP y mitiga XSS. |
| **ADR 5.4** | Migración de Datos | Patrón Expand/Contract (3 pasos) | 100% de datos preservados (0 filas perdidas). |
| **ADR 5.5** | Optimización API | JOIN Relacional + Paginación | Reduce consultas de 501 a 2 queries (99.6% menos). |
| **ADR 5.6** | Identidad en API | Sesiones con Cookies HttpOnly | Revocación inmediata (0 s) tras cierre de sesión. |
| **ADR 5.7** | Estrategia de Testing | Pruebas de Integración con Pytest | Captura 100% de los fallos inyectados a la API. |
| **ADR 5.8** | Empaquetado | Multi-Stage Build (`python:slim`) | Reduce tamaño de imagen a 155 MB (84.8% ahorro). |
| **ADR 9** | Integración Final | Consolidación en WSGI / Gunicorn | Elimina bloqueos de base de datos (`database is locked`). |

---

## 🚀 Guía de Instalación y Ejecución

### Opción A: Ejecución mediante Docker (Recomendado)

El proyecto incluye un `Dockerfile` optimizado en múltiples etapas (*Multi-Stage Build*) que ejecuta el servicio bajo un usuario no administrado (`appuser`).

1. **Construir la imagen de contenedor:**
   ```bash
   docker build -t prestamos-service:latest .
   ```

2. **Iniciar el contenedor en producción:**
   ```bash
   docker run -d --rm \
     --name prestamos_app \
     -p 8000:8000 \
     -e DEBUG=False \
     -e SECRET_KEY=clave-produccion-segura-2026 \
     prestamos-service:latest
   ```

3. **Verificar el estado del servicio (*Healthcheck*):**
   ```bash
   curl http://localhost:8000/health
   ```
   *Respuesta esperada:* `{"debug_mode": false, "environment": "production", "status": "healthy"}`

---

### Opción B: Ejecución en Entorno Local (Desarrollo)

1. **Clonar el repositorio y entrar al directorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd integrador_m5
   ```

2. **Crear y activar entorno virtual Python 3.12:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Linux/macOS
   # venv\Scripts\activate   # En Windows
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar el servidor con Gunicorn:**
   ```bash
   gunicorn -w 2 -b 127.0.0.1:8000 src.app:app
   ```

---

## 🧪 Ejecución de la Suite de Pruebas

La suite de pruebas automatizadas está desarrollada sobre `pytest` y evalúa la integración de la API, restricciones de seguridad RBAC, paginación e integridad de respuestas HTTP.

Para ejecutar las pruebas y generar el reporte de cobertura de código:

```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

---

## 🧑‍💻 Información del Autor

* **Desarrollador / Estudiante:** Israel Merlyn
* **Especialidad:** Ingeniero en Sistemas / Desarrollo Full-Stack & Arquitectura de Software
* **Asignatura:** Programa de Desarrollo de Software - Módulo 5