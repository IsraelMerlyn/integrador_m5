# ADR 5.5 — Estrategia de Serialización, Carga de Relaciones y Paginación en la API

**Contexto:** Se requiere exponer el endpoint de lista del recurso principal sobre un volumen de 500 registros con entidades relacionadas, evitando la degradación por el problema N+1 y controlando el tamaño de respuesta por petición.

**Opciones:** 
- Opción A: Serializador anidado sin optimización de ORM ni paginación ($N+1\text{ queries}$).
- Opción B: Carga relacional optimizada mediante JOIN / `select_related` sin paginación.
- Opción C: Carga optimizada (`select_related`) combinada con paginación por límite/desplazamiento (`page_size=20`).

**Criterio:** Número de consultas SQL ejecutadas por petición contra la base de datos y tamaño en bytes del payload JSON retornado sobre 500 registros.

**Evidencia:** Ejecución de `medir_queries.py` (Log crudo en `spike-5.5/salida_cruda.log`):

| Configuración de API | Consultas SQL Ejecutadas | Tamaño Payload JSON | Estado de Carga |
| :--- | :--- | :--- | :--- |
| **Opción A (N+1 Sin Optimizar)** | 501 consultas | ~72,800 bytes (~72.8 KB) | Inaceptable (Satura BD) |
| **Opción B (Optimizado con JOIN)** | 1 consulta | ~72,800 bytes (~72.8 KB) | Alto consumo de red |
| **Opción C (Optimizado + Paginado p=20)** | 2 consultas | ~3,100 bytes (~3.1 KB) | **Óptimo** |

**Decisión:** Opción C (Carga relacional JOIN / `select_related` con Paginación `page_size=20`) porque reduce en un $99.6\%$ el número de consultas SQL (de 501 a 2) y en un $95.7\%$ los bytes transferidos por viaje de red, protegiendo al servidor contra agotamiento de memoria y conexiones de base de datos.

**Consecuencias:** Modifica el contrato del API para los clientes consumidores, obligándolos a leer el array en la propiedad `results` y a gestionar la iteración mediante los metadatos de paginación (`count`, `next`, `previous`).

**Me haría cambiar de opinión:** Si el cliente requiriera exportaciones masivas completas de la base de datos en un solo archivo (ej. reportes CSV/PDF), donde la paginación impediría la descarga continua en una sola petición.