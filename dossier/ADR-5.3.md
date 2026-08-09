# ADR 5.3 — Arquitectura de la Frontera Front-End / Back-End

**Contexto:** Se requiere decidir si el renderizado de la interfaz del flujo principal (listar/filtrar recurso) debe ocurrir en el servidor (SSR) o desacoplado en el cliente vía llamadas asíncronas a la API (CSR).

**Opciones:** 
- Opción A: Renderizado en Servidor (SSR) con plantillas MVT / Jinja2.
- Opción B: Cliente desacoplado (CSR) con cáscara HTML y Fetch API consumiendo JSON.

**Criterio:** Número de peticiones HTTP requeridas para renderizar la pantalla inicial, bytes totales transferidos, soporte sin JavaScript activado y riesgo de duplicación de lógica/XSS.

**Evidencia:** Ejecución de `medir.py` (Log crudo en `spike-5.3/salida_cruda.log`):

| Métrica | Opción A (SSR Jinja2) | Opción B (CSR Fetch API) |
| :--- | :--- | :--- |
| **Viajes HTTP iniciales** | 1 viaje (HTML Completo) | 2 viajes (1 HTML + 1 JSON API) |
| **Bytes totales transferidos** | ~520 bytes | ~1,050 bytes (Suma de cáscara + JSON) |
| **¿Funciona sin JavaScript?** | SÍ (Formularios HTML nativos) | NO (Lista queda en blanco) |
| **Riesgo de Seguridad** | Bajo (Escape automático Jinja2) | Alto (Uso de `innerHTML` susceptible a XSS) |

**Decisión:** Opción A (SSR) para las vistas administrativas del monolito, manteniendo la API expuesta en 5.2 para integradores externos. El SSR entrega el contenido funcional en 1 solo viaje HTTP, funciona sin dependencias de JavaScript en el cliente y elimina la duplicación de validaciones de filtrado en dos lenguajes.

**Consecuencias:** Cada interacción de filtrado mediante formulario causa una recarga completa de página en el navegador.

**Me haría cambiar de opinión:** Si la aplicación requiriera una experiencia de usuario altamente reactiva tipo SPA (Single Page Application) o fuera consumida prioritariamente desde una aplicación móvil nativa.