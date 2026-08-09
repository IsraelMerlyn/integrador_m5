# ADR 5.4 — Estrategia de Migración de Esquema y Preservación de Datos

**Contexto:** Se requiere refactorizar la estructura de la base de datos (dividir `solicitante_completo` en `nombre` y `apellido`) sobre un volumen real de 500 registros sin sufrir pérdida de información ni tiempo de inactividad no planificado.

**Opciones:** 
- Opción A: Migración directa en 1 solo paso sugerida por el ORM (`DROP COLUMN` y `ADD COLUMN`).
- Opción B: Patrón Expand/Contract en 3 pasos (1. Crear columnas opcionales $\rightarrow$ 2. Data Migration/Backfill $\rightarrow$ 3. Eliminar columna antigua).

**Criterio:** Porcentaje de registros con datos íntegros preservados tras el cambio de esquema y reversibilidad garantizada de la migración medido por consultas SQL directas.

**Evidencia:** Ejecución de `poblar_y_migrar.py` sobre 500 registros iniciales (450 con datos, 50 nulos) (Log crudo en `spike-5.4/salida_cruda.log`):

| Métrica | Opción A (1 Paso Directo) | Opción B (Expand/Contract 3 Pasos) |
| :--- | :--- | :--- |
| **Filas Totales en BD** | 500 filas | 500 filas |
| **Registros con Dato Íntegro tras Migración** | 0 / 450 (100% Perdido) | 450 / 450 (100% Preservado) |
| **Reversibilidad Exitoso (Rollback)** | NO (Los datos originales no se recuperan) | SÍ (Recuperación total vía Backfill inverso) |

**Decisión:** Opción B (Patrón Expand/Contract) porque la migración directa en un solo paso destruye la totalidad de los datos existentes en la columna, mientras que el flujo de 3 pasos garantiza cero pérdida de datos y permite una reversión limpia mediante scripts de *Backfill*.

**Consecuencias:** Requiere crear y desplegar dos migraciones independientes en lugar de una sola, manteniendo compatibilidad temporal con el esquema antiguo mientras la aplicación se actualiza.

**Me haría cambiar de opinión:** Solo en un entorno de desarrollo local con base de datos recién inicializada o datos sintéticos no críticos donde la velocidad de iteración supere la necesidad de preservar el estado.