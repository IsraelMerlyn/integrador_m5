import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string, session

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-2026")
app.config["DEBUG"] = os.getenv("DEBUG", "False").lower() in ("true", "1")

DB_PATH = os.path.join(os.path.dirname(__file__), "prestamos.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS herramientas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS prestamos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            herramienta_id INTEGER NOT NULL,
            solicitante TEXT NOT NULL,
            dias INTEGER NOT NULL,
            FOREIGN KEY(herramienta_id) REFERENCES herramientas(id)
        )
    """)
    cur.execute("SELECT COUNT(*) FROM herramientas")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO herramientas (nombre, categoria) VALUES (?, ?)",
            [("Taladro Industrial", "Eléctrica"), ("Multímetro Digital", "Electrónica"), ("Cortadora Plasma", "Industrial")]
        )
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/health")
def health():
    return jsonify({
        "status": "healthy",
        "debug_mode": app.config["DEBUG"],
        "environment": "production" if not app.config["DEBUG"] else "development"
    }), 200

@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    role = data.get("role", "user")
    if not username:
        return jsonify({"error": "username es requerido"}), 400
    session["user"] = username
    session["role"] = role
    return jsonify({"message": "Sesión iniciada", "user": username, "role": role}), 200

@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"message": "Sesión cerrada"}), 200

@app.get("/api/prestamos")
def listar_prestamos():
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    solicitante_filter = request.args.get("solicitante", "").strip()

    conn = get_db()
    cur = conn.cursor()

    if solicitante_filter:
        cur.execute("SELECT COUNT(*) FROM prestamos WHERE solicitante LIKE ?", (f"%{solicitante_filter}%",))
        total = cur.fetchone()[0]
        offset = (page - 1) * page_size
        cur.execute("""
            SELECT p.id, p.solicitante, p.dias, h.id as h_id, h.nombre as h_nombre, h.categoria as h_categoria
            FROM prestamos p
            JOIN herramientas h ON p.herramienta_id = h.id
            WHERE p.solicitante LIKE ?
            LIMIT ? OFFSET ?
        """, (f"%{solicitante_filter}%", page_size, offset))
    else:
        cur.execute("SELECT COUNT(*) FROM prestamos")
        total = cur.fetchone()[0]
        offset = (page - 1) * page_size
        cur.execute("""
            SELECT p.id, p.solicitante, p.dias, h.id as h_id, h.nombre as h_nombre, h.categoria as h_categoria
            FROM prestamos p
            JOIN herramientas h ON p.herramienta_id = h.id
            LIMIT ? OFFSET ?
        """, (page_size, offset))

    rows = cur.fetchall()
    conn.close()

    results = [
        {
            "id": r["id"],
            "solicitante": r["solicitante"],
            "dias": r["dias"],
            "herramienta": {
                "id": r["h_id"],
                "nombre": r["h_nombre"],
                "categoria": r["h_categoria"]
            }
        }
        for r in rows
    ]

    return jsonify({
        "count": total,
        "page": page,
        "page_size": page_size,
        "results": results
    }), 200

@app.get("/api/prestamos/<int:prestamo_id>")
def detalle_prestamo(prestamo_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.solicitante, p.dias, h.id as h_id, h.nombre as h_nombre, h.categoria as h_categoria
        FROM prestamos p
        JOIN herramientas h ON p.herramienta_id = h.id
        WHERE p.id = ?
    """, (prestamo_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Préstamo no encontrado"}), 404

    return jsonify({
        "id": row["id"],
        "solicitante": row["solicitante"],
        "dias": row["dias"],
        "herramienta": {
            "id": row["h_id"],
            "nombre": row["h_nombre"],
            "categoria": row["h_categoria"]
        }
    }), 200

@app.post("/api/prestamos")
def crear_prestamo():
    if "user" not in session:
        return jsonify({"error": "Autenticación requerida"}), 401

    data = request.get_json(silent=True) or {}
    herramienta_id = data.get("herramienta_id")
    solicitante = data.get("solicitante")
    dias = data.get("dias")

    if not herramienta_id or not solicitante or not dias:
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    if not isinstance(dias, int) or dias <= 0 or dias > 30:
        return jsonify({"error": "Los días deben ser un entero entre 1 y 30"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM herramientas WHERE id = ?", (herramienta_id,))
    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "Herramienta inexistente"}), 400

    cur.execute(
        "INSERT INTO prestamos (herramienta_id, solicitante, dias) VALUES (?, ?, ?)",
        (herramienta_id, solicitante, dias)
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return jsonify({"id": new_id, "herramienta_id": herramienta_id, "solicitante": solicitante, "dias": dias}), 201

@app.delete("/api/prestamos/<int:prestamo_id>")
def eliminar_prestamo(prestamo_id):
    if "user" not in session:
        return jsonify({"error": "Autenticación requerida"}), 401
    if session.get("role") != "admin":
        return jsonify({"error": "Permisos insuficientes"}), 403

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM prestamos WHERE id = ?", (prestamo_id,))
    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "Préstamo no encontrado"}), 404

    cur.execute("DELETE FROM prestamos WHERE id = ?", (prestamo_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Préstamo eliminado"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)