from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)
PRESTAMOS: list[dict] = []

@app.get("/api/prestamos")
def listar():
    return jsonify(PRESTAMOS)

@app.post("/api/prestamos")
def crear():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "JSON invalido o cuerpo vacio"}), 400

    errors = []

    # 1. Validar herramienta_id
    if "herramienta_id" not in data:
        errors.append("falta herramienta_id")
    elif not isinstance(data["herramienta_id"], int) or isinstance(data["herramienta_id"], bool):
        errors.append("herramienta_id debe ser entero")

    # 2. Validar solicitante
    if "solicitante" not in data:
        errors.append("falta solicitante")
    elif not isinstance(data["solicitante"], str):
        errors.append("solicitante debe ser string")
    else:
        if len(data["solicitante"]) < 3 or len(data["solicitante"]) > 60:
            errors.append("solicitante debe tener entre 3 y 60 caracteres")

    # 3. Validar fecha_prestamo
    if "fecha_prestamo" not in data:
        errors.append("falta fecha_prestamo")
    elif isinstance(data["fecha_prestamo"], str):
        try:
            datetime.strptime(data["fecha_prestamo"], "%Y-%m-%d")
        except ValueError:
            errors.append("fecha_prestamo debe tener formato YYYY-MM-DD")
    else:
        errors.append("fecha_prestamo debe ser un string de fecha")

    # 4. Validar dias
    if "dias" not in data:
        errors.append("falta dias")
    elif not isinstance(data["dias"], int) or isinstance(data["dias"], bool):
        errors.append("dias debe ser entero")
    else:
        if data["dias"] <= 0 or data["dias"] > 30:
            errors.append("dias debe ser mayor a 0 y menor o igual a 30")

    if errors:
        return jsonify({"errors": errors}), 400

    PRESTAMOS.append(data)
    return jsonify(data), 201