import asyncio
from fastapi import FastAPI

app = FastAPI()

@app.get("/lento")
async def lento():
    await asyncio.sleep(0.5)  # Espera NO bloqueante
    return {"ok": True}