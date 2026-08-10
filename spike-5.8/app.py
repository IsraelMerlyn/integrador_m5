import os
from flask import Flask, jsonify

app = Flask(__name__)

# Lectura estricta de variables de entorno
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-insegura")

app.config["SECRET_KEY"] = SECRET_KEY

@app.get("/health")
def healthcheck():
    return jsonify({
        "status": "healthy",
        "debug_mode": DEBUG,
        "environment": "production" if not DEBUG else "development"
    }), 200

@app.get("/api/recurso")
def listar():
    return jsonify([{"id": 1, "estado": "operativo_en_contenedor"}]), 200