# ADR 5.6 — Mecanismo de Identidad en la API, Autorización y Estrategia de Revocación

**Contexto:** Se requiere asegurar la superficie de la API impidiendo accesos no autenticados, aplicando Control de Acceso Basado en Roles (RBAC) y gestionando la invalidación inmediata de credenciales ante un cierre de sesión (*logout*).

**Opciones:** 
- Opción A: Autenticación por Sesión con Cookie HttpOnly (Stateful en servidor).
- Opción B: Token firmado JSON Web Token (JWT) almacenado en cliente (Stateless).

**Criterio:** Capacidad de respuesta HTTP en la batería de 7 pruebas de seguridad, segregación de permisos RBAC (401 vs 403) y tiempo de revocación efectiva en segundos tras el cierre de sesión.

**Evidencia:** Ejecución de `probar_seguridad.py` (Log crudo en `spike-5.6/salida_cruda.log`):

| Caso de Prueba | Sesión (Opción A) | JWT Stateless (Opción B) |
| :--- | :--- | :--- |
| **1. Sin Credencial** | HTTP 401 Unauthorized | HTTP 401 Unauthorized |
| **2. Credencial Válida** | HTTP 200 OK | HTTP 200 OK |
| **3. Recurso Ajeno / Admin (RBAC)** | HTTP 403 Forbidden | HTTP 403 Forbidden |
| **4. Token/Cookie Manipulada** | HTTP 401 Unauthorized | HTTP 401 Unauthorized |
| **5. Credencial Expirada** | HTTP 401 Unauthorized | HTTP 401 Unauthorized |
| **6. Ventana de Acceso Post-Logout** | **0 segundos (Instantáneo)** | **300 segundos (Riesgo de uso activo)** |
| **7. Exposición a Ataques de Cliente** | Protegido de XSS (HttpOnly) | Vulnerable si vive en localStorage |

**Decisión:** Opción A (Sesiones en Servidor con Cookies HttpOnly) para la aplicación monolítica, permitiendo la invalidación inmediata de la sesión ($0\text{ segundos}$) sin requerir la implementación de listas negras (*blacklists*) en memoria distribuida (ej. Redis).

**Consecuencias:** Si se escala la aplicación a múltiples instancias de contenedores en la Lección 5.8, se requiere un almacén centralizado de sesiones (Redis/BD) para que todas las réplicas compartan el estado de autenticación.

**Me haría cambiar de opinión:** Si la API fuera consumida exclusivamente por clientes móviles nativos que no soportan el manejo automático de cookies HttpOnly o si el volumen de peticiones requiriera una arquitectura de microservicios $100\%$ desarticulada sin llamadas a base de datos para validar credenciales.