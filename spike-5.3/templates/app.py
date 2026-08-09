from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# Datos de prueba del recurso
PRESTAMOS = [
    {"id": 1, "herramienta": "Taladro Industrial", "solicitante": "Ana Ruiz", "dias": 3},
    {"id": 2, "herramienta": "Multímetro Digital", "solicitante": "Carlos Gómez", "dias": 5},
    {"id": 3, "herramienta": "Cortadora de Plasma", "solicitante": "Ana Ruiz", "dias": 1},
]

# --- OPCIÓN A: SSR (Renderizado en Servidor con Jinja2) ---
TEMPLATE_SSR = """
<!DOCTYPE html>
<html>
<head><title>Préstamos - SSR</title></head>
<body>
    <h1>Lista de Préstamos (SSR)</h1>
    <form method="GET" action="/ssr/prestamos">
        <input type="text" name="q" value="{{ q }}" placeholder="Buscar solicitante...">
        <button type="submit">Filtrar</button>
    </form>
    <ul id="lista">
        {% for p in prestamos %}
            <li><strong>{{ p.solicitante }}</strong>: {{ p.herramienta }} ({{ p.dias }} días)</li>
        {% else %}
            <li>No se encontraron registros.</li>
        {% endfor %}
    </ul>
</body>
</html>
"""

@app.get("/ssr/prestamos")
def ssr_prestamos():
    q = request.args.get("q", "").lower()
    resultado = [p for p in PRESTAMOS if q in p["solicitante"].lower()] if q else PRESTAMOS
    return render_template_string(TEMPLATE_SSR, prestamos=resultado, q=q)


# --- OPCIÓN B: CSR (Cáscara HTML + Fetch API a Endpoint JSON) ---
TEMPLATE_CSR = """
<!DOCTYPE html>
<html>
<head><title>Préstamos - CSR</title></head>
<body>
    <h1>Lista de Préstamos (CSR)</h1>
    <input type="text" id="q" placeholder="Buscar solicitante...">
    <ul id="lista"><!-- Se llena mediante JS --></ul>

    <script>
        async function cargar() {
            const q = document.getElementById("q").value;
            const r = await fetch("/api/prestamos?q=" + encodeURIComponent(q));
            const datos = await r.json();
            const lista = document.getElementById("lista");
            // Vulnerabilidad potencial XSS si se usara innerHTML sin sanitizar
            lista.innerHTML = datos.map(p => 
                `<li><strong>${p.solicitante}</strong>: ${p.herramienta} (${p.dias} días)</li>`
            ).join("");
        }
        document.getElementById("q").addEventListener("input", cargar);
        cargar();
    </script>
</body>
</html>
"""

@app.get("/csr/prestamos")
def csr_prestamos():
    return render_template_string(TEMPLATE_CSR)

@app.get("/api/prestamos")
def api_prestamos():
    q = request.args.get("q", "").lower()
    resultado = [p for p in PRESTAMOS if q in p["solicitante"].lower()] if q else PRESTAMOS
    return jsonify(resultado)