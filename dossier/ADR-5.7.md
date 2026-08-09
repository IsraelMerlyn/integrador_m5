# ADR 5.7 — Estrategia de Pruebas, Cobertura de Código e Inyección de Fallos

**Contexto:** Se requiere establecer la estrategia de pruebas para la API, determinando si priorizar pruebas unitarias aisladas o pruebas de integración sobre los endpoints para maximizar la detección de regresiones críticas antes de producción.

**Opciones:** 
- Opción A: Estrategia enfocada en Pruebas Unitarias de funciones de dominio aisladas.
- Opción B: Estrategia combinada con énfasis en Pruebas de Integración sobre endpoints de la API.

**Criterio:** Tasa de captura de 5 fallos inyectados a propósito (Pruebas de Mutación) frente al porcentaje reportado de cobertura de código (*Code Coverage*).

**Evidencia:** Ejecución de `evaluar_pruebas.py` (Log crudo en `spike-5.7/salida_cruda.log`):

- **Cobertura de Código Reportada (*pytest-cov*):** $100\%$ de líneas ejecutadas.
- **Tasa de Detección de Fallos (Efectividad Real):**

| Fallo Inyectado | Atrapado por Unitarias (Opción A) | Atrapado por Integración (Opción B) |
| :--- | :--- | :--- |
| **1. Bypass de validación (días <= 0)** | SÍ | SÍ |
| **2. Falla de RBAC (acceso no autorizado)** | NO (No prueba permisos) | SÍ (Valida HTTP 403) |
| **3. Cálculo erróneo de fecha devolución** | SÍ | SÍ |
| **4. Filtro de lista roto (sin filtrar)** | NO (No prueba consultas) | SÍ |
| **5. Código de estado HTTP 200 en error** | NO (No prueba HTTP) | SÍ (Valida HTTP 400) |
| **RESULTADO TOTAL DETECTADOS** | **2 / 5 (40% Efectividad)** | **5 / 5 (100% Efectividad)** |

**Decisión:** Opción B (Enfoque Prioritario en Pruebas de Integración sobre Endpoints) porque, a pesar de que ambas estrategias alcanzaron un $100\%$ de cobertura de código (*coverage*), las pruebas unitarias solo detectaron el $40\%$ de los fallos reales, mientras que las pruebas de integración capturaron el $100\%$ de los defectos de seguridad, serialización y códigos HTTP.

**Consecuencias:** Las pruebas de integración requieren un tiempo de ejecución ligeramente superior y requieren preparar fixtures de datos de prueba antes de ser ejecutadas.

**Me haría cambiar de opinión:** Si la suite de pruebas de integración se volviera lenta/frágil (*flaky*) debido al crecimiento excesivo de la base de datos de pruebas o si la lógica de negocio pura alcanzara tal complejidad matemática que requiriera cientos de variaciones unitarias sin pasar por la capa HTTP.