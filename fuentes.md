# Bitácora Completa de Fuentes de Investigación — Módulo 5

## Fuentes Primarias (Documentación Oficial, PEPs y RFCs)

1. **Python Software Foundation (2010).** *PEP 3333 – Python Web Server Gateway Interface v1.0.1*.
   - **URL:** https://peps.python.org/pep-3333/
   - **Fecha de consulta:** 2026-08-09
   - **Aporte:** Especificación del contrato ejecutable WSGI y la limitación de acoplamiento 1-petición a 1-worker activo.

2. **ASGI Special Interest Group (2021).** *ASGI (Asynchronous Server Gateway Interface) Specification v3.0*.
   - **URL:** https://asgi.readthedocs.io/
   - **Fecha de consulta:** 2026-08-09
   - **Aporte:** Estructura de eventos basada en el trinomio `scope`, `receive` y `send` para concurrencia en bucle de eventos.

3. **Internet Engineering Task Force / IETF (2015).** *RFC 7519 – JSON Web Token (JWT)*.
   - **URL:** https://datatracker.ietf.org/doc/html/rfc7519
   - **Fecha de consulta:** 2026-08-09
   - **Aporte:** Especificación de la estructura de claims (`exp`, `sub`, `iat`) y verificación de firma digital.

4. **Internet Engineering Task Force / IETF (2012).** *RFC 6749 – The OAuth 2.0 Authorization Framework*.
   - **URL:** https://datatracker.ietf.org/doc/html/rfc6749
   - **Fecha de consulta:** 2026-08-09
   - **Aporte:** Definición de roles (Resource Owner, Client, Authorization Server) y flujo de código de autorización.

5. **OWASP Foundation (2024).** *Session Management Cheat Sheet*.
   - **URL:** https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
   - **Fecha de consulta:** 2026-08-09
   - **Aporte:** Estándares de seguridad para mitigación de XSS/CSRF mediante banderas `HttpOnly` y `SameSite`.

6. **OWASP Foundation (2024).** *Docker Security Cheat Sheet*.
   - **URL:** https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html
   - **Fecha de consulta:** 2026-08-09
   - **Aporte:** Directivas de principio de menor privilegio creando usuarios dedicados sin acceso a root (`appuser`).

7. **Docker Inc. (2024).** *Dockerfile Best Practices – Multi-stage builds*.
   - **URL:** https://docs.docker.com/build/building/multi-stage/
   - **Fecha de consulta:** 2026-08-09
   - **Aporte:** Patrón de diseño para separar herramientas de compilación de la imagen ejecutable final.

8. **Django Software Foundation (2024).** *Database Access Optimization – select_related and prefetch_related*.
   - **URL:** https://docs.djangoproject.com/en/5.0/topics/db/optimization/
   - **Fecha de consulta:** 2026-08-09
   - **Aporte:** Diferenciación técnica entre `JOIN` SQL y consultas multitabla paralelas en Python para erradicar el problema N+1.

---

## Fuentes Secundarias (Guías de Frameworks y Herramientas)

9. **Ramírez, S. / FastAPI (2023).** *FastAPI Documentation – Request Body and Fields*.
   - **URL:** https://fastapi.tiangolo.com/tutorial/body/
   - **Fecha de consulta:** 2026-08-09
   - **Aporte:** Declaración de esquemas vía Type Hints y Pydantic para validación de entradas.

10. **Pydantic Team (2024).** *Pydantic Model Configuration – Extra Fields Handling*.
    - **URL:** https://docs.pydantic.dev/latest/concepts/config/#extra-attributes
    - **Fecha de consulta:** 2026-08-09
    - **Aporte:** Patrón de seguridad `extra: forbid` para prevenir ataques de Mass Assignment.

11. **Pytest Development Team (2024).** *pytest documentation – How to use fixtures*.
    - **URL:** https://docs.pytest.org/en/stable/explanation/fixtures.html
    - **Fecha de consulta:** 2026-08-09
    - **Aporte:** Patrones para inyección de dependencias y preparación de estado de pruebas reproducibles.

12. **Batchelder, N. / Coverage.py Team (2024).** *Coverage.py Documentation – Limitations*.
    - **URL:** https://coverage.readthedocs.io/
    - **Fecha de consulta:** 2026-08-09
    - **Aporte:** Justificación teórica sobre por qué $100\%$ de ejecución de líneas no equivale a $100\%$ de verificación de aserciones.
