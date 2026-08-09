from datetime import date
from fastapi import FastAPI
from pydantic import BaseModel, Field

class PrestamoIn(BaseModel):
    herramienta_id: int
    solicitante: str = Field(min_length=3, max_length=60)
    fecha_prestamo: date
    dias: int = Field(gt=0, le=30)

    model_config = {"extra": "forbid"}  # Rechaza campos no declarados (ej. admin: True)

app = FastAPI(title="API Prestamos FastAPI")
PRESTAMOS: list[dict] = []

@app.get("/api/prestamos")
def listar():
    return PRESTAMOS

@app.post("/api/prestamos", status_code=201)
def crear(p: PrestamoIn):
    data = p.model_dump(mode="json")
    PRESTAMOS.append(data)
    return PRESTAMOS[-1]