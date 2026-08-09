import datetime
import platform
import httpx

print("TIMESTAMP Y ENTORNO:")
print(datetime.datetime.now().isoformat(), platform.node(), platform.platform())
print("-" * 60)

BASE_URL = "http://127.0.0.1:8000"

def medir_ssr():
    print("=== OPCIÓN A: SSR (Server-Side Rendering) ===")
    r = httpx.get(f"{BASE_URL}/ssr/prestamos?q=Ana")
    bytes_totales = len(r.content)
    viajes_http = 1
    funciona_sin_js = "Ana Ruiz" in r.text
    print(f"Viajes HTTP requeridos: {viajes_http}")
    print(f"Bytes transferidos: {bytes_totales} bytes")
    print(f"Contenido renderizado sin JS: {'SÍ' if funciona_sin_js else 'NO'}\n")

def medir_csr():
    print("=== OPCIÓN B: CSR (Client-Side Rendering) ===")
    # 1. Traer la cáscara HTML
    r_cascara = httpx.get(f"{BASE_URL}/csr/prestamos")
    # 2. El navegador ejecuta JS y pide los datos a la API
    r_api = httpx.get(f"{BASE_URL}/api/prestamos?q=Ana")
    
    bytes_totales = len(r_cascara.content) + len(r_api.content)
    viajes_http = 2
    funciona_sin_js = "Ana Ruiz" in r_cascara.text  # La cáscara original no trae los datos
    print(f"Viajes HTTP requeridos: {viajes_http} (1 Cáscara HTML + 1 API JSON)")
    print(f"Bytes transferidos: {bytes_totales} bytes ({len(r_cascara.content)} HTML + {len(r_api.content)} JSON)")
    print(f"Contenido renderizado sin JS: {'SÍ' if funciona_sin_js else 'NO'}\n")

if __name__ == "__main__":
    medir_ssr()
    medir_csr()