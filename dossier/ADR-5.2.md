# ADR 5.2 — Estrategia de Validación de Datos y Exposición de API

**Contexto:** Se requiere decidir cómo exponer el recurso principal como API JSON asegurando la integridad de los datos de entrada frente a payloads mal formados o inyectados.

**Opciones:** 
- Opción A: API dentro del framework actual (Flask) con validación imperativa manual.
- Opción B: Servicio dedicado FastAPI con validación por esquema declarativo (Pydantic).

**Criterio:** Capacidad de captura automática de 6 payloads inválidos, código de estado retornado (422 vs 400), líneas de código de validación requeridas y generación nativa de documentación OpenAPI.

**Evidencia:** Ejecución de `payloads.py` (Log crudo en `spike-5.2/salida_cruda.log`):

| Caso | Payload | FastAPI (Opción B) | Flask Manual (Opción A) |
| :--- | :--- | :--- | :--- |
| `1_ok` | Válido | HTTP 201 (Aceptado) | HTTP 201 (Aceptado) |
| `2_falta_campo` | Sin `fecha_prestamo` | HTTP 422 (Atrapado) | HTTP 400 (Atrapado) |
| `3_tipo_malo` | `herramienta_id: "uno"` | HTTP 422 (Atrapado) | HTTP 400 (Atrapado) |
| `4_fuera_rango` | `dias: -5` | HTTP 422 (Atrapado) | HTTP 400 (Atrapado) |
| `5_campo_extra` | `admin: True` | HTTP 422 (Atrapado) | HTTP 201 (NO Atrapado) |
| `6_fecha_basura`| `fecha_prestamo: "ayer"`| HTTP 422 (Atrapado) | HTTP 400 (Atrapado) |

- **Líneas de validación escritas:** Opción A = ~35 líneas imperativas | Opción B = 5 líneas declarativas.
- **Soporte OpenAPI nativo:** Opción A = No (`/docs` inexistente) | Opción B = Sí (`/docs` auto-generado).

**Decisión:** Opción B (FastAPI) porque la validación declarativa redujo en un 85% el código de validación, atrapó el 100% de los casos (incluyendo campos no declarados como `admin: True` que en Flask causan sobre-asignación de propiedades) y genera la especificación OpenAPI de forma automática.

**Consecuencias:** Operar un proceso adicional requiere configurar la comunicación entre el front-end y la API vía CORS y gestionar el despliegue de dos puntos de entrada o un proxy inverso en la Lección 5.8.

**Me haría cambiar de opinión:** Si la aplicación fuera un monolito simple sin consumo externo (móvil o cliente desacoplado) y el costo operativo de un proceso extra superara los beneficios del contrato OpenAPI.