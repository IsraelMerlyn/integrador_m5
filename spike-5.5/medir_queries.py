import sqlite3
import json
import datetime
import platform

DB_PATH = "spike-5.5/n1_test.db"

class QueryCounter:
    """Wrapper sobre la conexión SQLite para interceptar y contar cada consulta ejecutada."""
    def __init__(self, conn):
        self.conn = conn
        self.count = 0
        self.queries = []
        self.conn.set_trace_callback(self._trace)

    def _trace(self, statement):
        # Filtrar comandos internos de transacción
        if statement.strip().upper() not in ("BEGIN", "COMMIT", "ROLLBACK"):
            self.count += 1
            self.queries.append(statement)

    def reset(self):
        self.count = 0
        self.queries.clear()

def obtener_header():
    print("TIMESTAMP Y ENTORNO:")
    print(datetime.datetime.now().isoformat(), platform.node(), platform.platform())
    print("-" * 65)

def poblar_bd():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS prestamos")
    cur.execute("DROP TABLE IF EXISTS herramientas")

    cur.execute("""
        CREATE TABLE herramientas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE prestamos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            herramienta_id INTEGER NOT NULL,
            solicitante TEXT NOT NULL,
            dias INTEGER NOT NULL,
            FOREIGN KEY(herramienta_id) REFERENCES herramientas(id)
        )
    """)

    # 1. Insertar 20 herramientas
    herramientas = [(f"Herramienta #{i}", f"Categoría {i % 4 + 1}") for i in range(1, 21)]
    cur.executemany("INSERT INTO herramientas (nombre, categoria) VALUES (?, ?)", herramientas)

    # 2. Insertar 500 préstamos vinculados
    nombres = ["Ana Ruiz", "Carlos Gómez", "Beatriz López", "David Hernández", "Elena Martínez"]
    prestamos = [
        ((i % 20) + 1, nombres[i % len(nombres)], (i % 5) + 1)
        for i in range(1, 501)
    ]
    cur.executemany("INSERT INTO prestamos (herramienta_id, solicitante, dias) VALUES (?, ?, ?)", prestamos)

    conn.commit()
    conn.close()

# --- ESCENARIO A: Anidado Sin Optimizar (N+1 Queries) ---
def escenario_a_n_plus_1(tracker, conn):
    tracker.reset()
    cur = conn.cursor()

    # Query 1: Obtener la lista base de 500 préstamos
    cur.execute("SELECT id, herramienta_id, solicitante, dias FROM prestamos")
    filas_prestamos = cur.fetchall()

    resultado = []
    # N Queries (500 iteraciones): Para cada registro, consulta la herramienta individualmente
    for p_id, h_id, solicitante, dias in filas_prestamos:
        cur.execute("SELECT id, nombre, categoria FROM herramientas WHERE id = ?", (h_id,))
        h = cur.fetchone()
        resultado.append({
            "id": p_id,
            "solicitante": solicitante,
            "dias": dias,
            "herramienta": {"id": h[0], "nombre": h[1], "categoria": h[2]}
        })

    payload_json = json.dumps(resultado)
    bytes_size = len(payload_json.encode('utf-8'))
    print(f"[Escenario A - N+1 Sin Optimizar]")
    print(f"  Consultas SQL ejecutadas: {tracker.count}")
    print(f"  Tamaño de la respuesta JSON: {bytes_size:,} bytes\n")
    return tracker.count, bytes_size

# --- ESCENARIO B: Anidado Optimizado con JOIN (select_related) ---
def escenario_b_eager_loading(tracker, conn):
    tracker.reset()
    cur = conn.cursor()

    # Query 1 ÚNICA: JOIN relacional previo
    cur.execute("""
        SELECT p.id, p.solicitante, p.dias, h.id, h.nombre, h.categoria
        FROM prestamos p
        INNER JOIN herramientas h ON p.herramienta_id = h.id
    """)
    filas = cur.fetchall()

    resultado = [
        {
            "id": p_id,
            "solicitante": solicitante,
            "dias": dias,
            "herramienta": {"id": h_id, "nombre": h_nombre, "categoria": h_categoria}
        }
        for p_id, solicitante, dias, h_id, h_nombre, h_categoria in filas
    ]

    payload_json = json.dumps(resultado)
    bytes_size = len(payload_json.encode('utf-8'))
    print(f"[Escenario B - Optimizado con JOIN / select_related]")
    print(f"  Consultas SQL ejecutadas: {tracker.count}")
    print(f"  Tamaño de la respuesta JSON: {bytes_size:,} bytes\n")
    return tracker.count, bytes_size

# --- ESCENARIO C: Optimizado con JOIN + Paginación (page_size=20) ---
def escenario_c_paginado(tracker, conn, page=1, page_size=20):
    tracker.reset()
    cur = conn.cursor()

    # Query 1: Obtener conteo total para metadatos de la API
    cur.execute("SELECT COUNT(*) FROM prestamos")
    total_records = cur.fetchone()[0]

    # Query 2: Obtener únicamente el bloque paginado
    offset = (page - 1) * page_size
    cur.execute("""
        SELECT p.id, p.solicitante, p.dias, h.id, h.nombre, h.categoria
        FROM prestamos p
        INNER JOIN herramientas h ON p.herramienta_id = h.id
        LIMIT ? OFFSET ?
    """, (page_size, offset))
    filas = cur.fetchall()

    items = [
        {
            "id": p_id,
            "solicitante": solicitante,
            "dias": dias,
            "herramienta": {"id": h_id, "nombre": h_nombre, "categoria": h_categoria}
        }
        for p_id, solicitante, dias, h_id, h_nombre, h_categoria in filas
    ]

    respuesta_paginada = {
        "count": total_records,
        "page": page,
        "page_size": page_size,
        "next": f"/api/prestamos?page={page + 1}" if offset + page_size < total_records else None,
        "results": items
    }

    payload_json = json.dumps(respuesta_paginada)
    bytes_size = len(payload_json.encode('utf-8'))
    print(f"[Escenario C - Optimizado + Paginado (page_size={page_size})]")
    print(f"  Consultas SQL ejecutadas: {tracker.count}")
    print(f"  Tamaño de la respuesta JSON: {bytes_size:,} bytes\n")
    return tracker.count, bytes_size

if __name__ == "__main__":
    obtener_header()
    poblar_bd()

    raw_conn = sqlite3.connect(DB_PATH)
    tracker = QueryCounter(raw_conn)

    escenario_a_n_plus_1(tracker, raw_conn)
    escenario_b_eager_loading(tracker, raw_conn)
    escenario_c_paginado(tracker, raw_conn, page=1, page_size=20)

    raw_conn.close()