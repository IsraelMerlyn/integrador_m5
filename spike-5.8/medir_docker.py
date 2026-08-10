import datetime
import platform
import subprocess
import time

def obtener_header():
    print("TIMESTAMP Y ENTORNO:")
    print(datetime.datetime.now().isoformat(), platform.node(), platform.platform())
    print("-" * 65)

def ejecutar_comando_visible(cmd):
    """Ejecuta comandos mostrando la salida en tiempo real en la terminal."""
    t0 = time.perf_counter()
    process = subprocess.run(cmd, shell=True)
    dt = round(time.perf_counter() - t0, 2)
    return process.returncode, dt

def medir_imagenes():
    print("=== MEDICIÓN Y COMPARACIÓN DE IMÁGENES DOCKER ===")
    
    # 1. Compilar Imagen Single-Stage
    print("\n>> [1/4] Compilando Opción A (Single-Stage `python:3.12`)...")
    print("Nota: Descargando imagen base (puede tomar 1-2 min la primera vez)...")
    cmd_build_a = "docker build -f spike-5.8/Dockerfile.single -t app-single:latest spike-5.8/"
    code_a, t_build_a = ejecutar_comando_visible(cmd_build_a)

    # 2. Compilar Imagen Multi-Stage
    print("\n>> [2/4] Compilando Opción B (Multi-Stage `python:3.12-slim`)...")
    cmd_build_b = "docker build -f spike-5.8/Dockerfile -t app-multistage:latest spike-5.8/"
    code_b, t_build_b = ejecutar_comando_visible(cmd_build_b)

    # 3. Obtener Tamaños de Imagen
    print("\n>> [3/4] Calculando tamaños finales de imágenes...")
    res_a = subprocess.run("docker image inspect app-single:latest --format='{{.Size}}'", shell=True, capture_output=True, text=True)
    res_b = subprocess.run("docker image inspect app-multistage:latest --format='{{.Size}}'", shell=True, capture_output=True, text=True)

    size_a = res_a.stdout.strip()
    size_b = res_b.stdout.strip()

    mb_a = round(int(size_a) / (1024 * 1024), 2) if size_a.isdigit() else 0
    mb_b = round(int(size_b) / (1024 * 1024), 2) if size_b.isdigit() else 0

    print("\n" + "=" * 65)
    print("RESULTADOS DE COMPILACIÓN DE IMÁGENES:")
    print(f"  Opción A (Single-Stage): Tamaño = {mb_a} MB | Tiempo Build = {t_build_a}s")
    print(f"  Opción B (Multi-Stage):  Tamaño = {mb_b} MB | Tiempo Build = {t_build_b}s")
    print("=" * 65 + "\n")

    # 4. Probar Arranque en Frío y Healthcheck
    print(">> [4/4] Probando arranque en frío y variables de entorno de Opción B...")
    
    # Detener contenedor previo si existiera
    subprocess.run("docker stop test-app-prod", shell=True, capture_output=True)
    
    cmd_run = (
        "docker run -d --rm --name test-app-prod -p 8000:8000 "
        "-e DEBUG=False -e SECRET_KEY=prod-secret-key app-multistage:latest"
    )
    t0_run = time.perf_counter()
    subprocess.run(cmd_run, shell=True)
    
    time.sleep(2) # Dar tiempo al proceso dentro del contenedor
    res_hc = subprocess.run("curl -s http://127.0.0.1:8000/health", shell=True, capture_output=True, text=True)
    t_cold_start = round(time.perf_counter() - t0_run, 2)

    print(f"Respuesta Healthcheck HTTP: {res_hc.stdout.strip()}")
    print(f"Tiempo de Arranque en Frío: {t_cold_start} segundos")

    # Limpiar contenedor de prueba
    subprocess.run("docker stop test-app-prod", shell=True, capture_output=True)

if __name__ == "__main__":
    obtener_header()
    medir_imagenes()