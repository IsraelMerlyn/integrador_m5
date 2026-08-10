# ADR 5.8 — Estrategia de Empaquetado en Contenedores (Docker) y Servidor de Producción

**Contexto:** Se requiere empaquetar el servicio web y sus dependencias en una imagen reproducible que arranque de forma segura en servidores de producción (Render, PythonAnywhere, Docker Hub) sin dependencias del sistema anfitrión ni secretos expuestos.

**Opciones:** 
- Opción A: Imagen de una sola etapa (*Single-Stage*) basada en la imagen estándar `python:3.12`.
- Opción B: Imagen de múltiples etapas (*Multi-Stage Build*) basada en `python:3.12-slim` corriendo bajo un usuario sin privilegios (*appuser*).

**Criterio:** Tamaño final de la imagen en Megabytes (MB), tiempo de compilación inicial, tiempo de arranque en frío (*cold start*) y postura de seguridad del proceso (ejecución sin privilegios root).

**Evidencia:** Ejecución de `medir_docker.py` y despliegue del servicio (Log crudo en `spike-5.8/salida_cruda.log`):

| Métrica | Opción A (Single-Stage) | Opción B (Multi-Stage Build) |
| :--- | :--- | :--- |
| **Tamaño Final de Imagen** | ~1,020 MB (~1.02 GB) | **~155 MB (Reducción del 84.8%)** |
| **Tiempo de Compilación** | ~28.5 segundos | ~18.2 segundos |
| **Tiempo de Arranque en Frío** | ~2.1 segundos | ~2.2 segundos |
| **Usuario del Contenedor** | `root` (Riesgo de seguridad) | `appuser` (No-root / Aislado) |
| **Healthcheck Integrado** | NO | SÍ (`http://127.0.0.1:8000/health`) |

**Decisión:** Opción B (Multi-Stage Build con `python:3.12-slim` y usuario no-root) porque reduce el tamaño de la imagen en un $84.8\%$ (de 1.02 GB a 155 MB), eliminando compiladores e hiper-dependencias de desarrollo de la imagen final y garantizando la ejecución del proceso bajo un usuario no administrado.

**Consecuencias:** Exige mantener un `Dockerfile` estructurado en dos etapas (`builder` y `runner`), copiando explícitamente los binarios de librerías desde el directorio de instalación pre-compilado.

**Me haría cambiar de opinión:** Si la aplicación requiriera librerías de C/C++ muy complejas con enlaces dinámicos en tiempo de ejecución que fallaran al ser movidos entre la etapa de compilación y la imagen final `slim`.