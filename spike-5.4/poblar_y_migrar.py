import sqlite3
import datetime
import platform
import os

DB_NAME = "spike-5.4/prestamos.db"

def obtener_header():
    print("TIMESTAMP Y ENTORNO:")
    print(datetime.datetime.now().isoformat(), platform.node(), platform.platform())
    print("-" * 65)

def conectar_bd():
    return sqlite3.connect(DB_NAME)

def inicializar_y_poblar():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    conn = conectar_bd()
    cur = conn.cursor()
    
    # Crear esquema inicial
    cur.execute("""
        CREATE TABLE prestamos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            herramienta_id INTEGER NOT NULL,
            solicitante_completo TEXT,
            dias INTEGER NOT NULL
        )
    """)

    # Poblar 500 filas realistas (con 10% de NULL/vaca para probar borde)
    nombres = ["Ana", "Carlos", "Beatriz", "David", "Elena", "Fernando", "Gabriela", "Hugo"]
    apellidos = ["Ruiz", "Gómez", "López", "Hernández", "Martínez", "Pérez", "Sánchez", "Torres"]
    
    registros = []
    for i in range(1, 501):
        if i % 10 == 0:
            # 10% de registros con campo nulo/vacío a propósito
            solicitante = None
        else:
            nom = nombres[i % len(nombres)]
            ape = apellidos[i % len(apellidos)]
            solicitante = f"{nom} {ape}"
        
        registros.append(( (i % 20) + 1, solicitante, (i % 5) + 1 ))

    cur.executemany("""
        INSERT INTO prestamos (herramienta_id, solicitante_completo, dias)
        VALUES (?, ?, ?)
    """, registros)

    conn.commit()
    conn.close()

def conteo_sql_directo(etiqueta, conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM prestamos")
    total = cur.fetchone()[0]

    # Verificar presencia de datos en la columna original o separada
    cur.execute("SELECT COUNT(*) FROM prestamos WHERE solicitante_completo IS NOT NULL AND solicitante_completo != ''")
    con_dato_orig = cur.fetchone()[0]

    # Verificar si existen las nuevas columnas
    cur.execute("PRAGMA table_info(prestamos)")
    columnas = [col[1] for col in cur.fetchall()]
    
    con_dato_nuevo = 0
    if "nombre" in columnas and "apellido" in columnas:
        cur.execute("SELECT COUNT(*) FROM prestamos WHERE nombre IS NOT NULL AND apellido IS NOT NULL")
        con_dato_nuevo = cur.fetchone()[0]

    print(f"[{etiqueta}] Total Filas: {total} | Con Dato Original: {con_dato_orig} | Con Dato Mapeado Nuevo: {con_dato_nuevo}")
    return total, con_dato_orig, con_dato_nuevo

def estrategia_1_destructiva_directa():
    print("\n=== ESTRATEGIA 1: Migración Directa de 1 Paso (Destructiva) ===")
    inicializar_y_poblar()
    conn = conectar_bd()
    cur = conn.cursor()

    conteo_sql_directo("E1 - Antes de Migrar", conn)

    # Simulación de herramienta ORM que borra la columna vieja y crea dos nuevas vacías
    print(">> Ejecutando: DROP COLUMN solicitante_completo y ADD COLUMN nombre, apellido...")
    try:
        cur.execute("ALTER TABLE prestamos DROP COLUMN solicitante_completo")
        cur.execute("ALTER TABLE prestamos ADD COLUMN nombre TEXT")
        cur.execute("ALTER TABLE prestamos ADD COLUMN apellido TEXT")
        conn.commit()
        print(">> Migración aplicada.")
    except Exception as e:
        print(f"Error durante migración: {e}")

    conteo_sql_directo("E1 - Después de Migrar", conn)

    print(">> Intentando Reversión (Rollback)...")
    try:
        # Al revertir, se recrea la columna vieja pero los datos originales ya fueron destruidos
        cur.execute("ALTER TABLE prestamos DROP COLUMN nombre")
        cur.execute("ALTER TABLE prestamos DROP COLUMN apellido")
        cur.execute("ALTER TABLE prestamos ADD COLUMN solicitante_completo TEXT")
        conn.commit()
        print(">> Reversión ejecutada.")
    except Exception as e:
        print(f">> ERROR EN REVERSIÓN: {e}")

    conteo_sql_directo("E1 - Después de Rollback", conn)
    conn.close()

def estrategia_2_expand_contract():
    print("\n=== ESTRATEGIA 2: Patrón Expand/Contract en 3 Pasos (Zero Data Loss) ===")
    inicializar_y_poblar()
    conn = conectar_bd()
    cur = conn.cursor()

    conteo_sql_directo("E2 - Paso 0 (Inicio)", conn)

    # Paso 1: EXPANDIR (Añadir nuevas columnas opcionales)
    print(">> Paso 1: Añadir columnas 'nombre' y 'apellido'...")
    cur.execute("ALTER TABLE prestamos ADD COLUMN nombre TEXT")
    cur.execute("ALTER TABLE prestamos ADD COLUMN apellido TEXT")
    conn.commit()

    # Paso 2: RELLENAR (Data Migration / Backfill)
    print(">> Paso 2: Migrar datos existentes (Data Migration)...")
    cur.execute("SELECT id, solicitante_completo FROM prestamos WHERE solicitante_completo IS NOT NULL")
    filas = cur.fetchall()
    
    for fid, completo in filas:
        partes = completo.split(" ", 1)
        nom = partes[0]
        ape = partes[1] if len(partes) > 1 else ""
        cur.execute("UPDATE prestamos SET nombre = ?, apellido = ? WHERE id = ?", (nom, ape, fid))
    conn.commit()
    conteo_sql_directo("E2 - Paso 2 (Backfill Completado)", conn)

    # Paso 3: CONTRAER (Eliminar columna obsoleta)
    print(">> Paso 3: Eliminar columna antigua 'solicitante_completo'...")
    cur.execute("ALTER TABLE prestamos DROP COLUMN solicitante_completo")
    conn.commit()
    conteo_sql_directo("E2 - Paso 3 (Columna Vieja Eliminada)", conn)

    # Probar Reversibilidad
    print(">> Probando Reversión de la Estrategia 2...")
    cur.execute("ALTER TABLE prestamos ADD COLUMN solicitante_completo TEXT")
    cur.execute("UPDATE prestamos SET solicitante_completo = nombre || ' ' || apellido WHERE nombre IS NOT NULL")
    cur.execute("ALTER TABLE prestamos DROP COLUMN nombre")
    cur.execute("ALTER TABLE prestamos DROP COLUMN apellido")
    conn.commit()
    conteo_sql_directo("E2 - Después de Reversión Exitosa", conn)
    
    conn.close()

if __name__ == "__main__":
    obtener_header()
    estrategia_1_destructiva_directa()
    estrategia_2_expand_contract()