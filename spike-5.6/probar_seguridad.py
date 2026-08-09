import datetime
import platform
import time
import jwt

SECRET_KEY = "clave-secreta-integrador-m5"

def obtener_header():
    print("TIMESTAMP Y ENTORNO:")
    print(datetime.datetime.now().isoformat(), platform.node(), platform.platform())
    print("-" * 65)

# --- ALMACENES DE ESTADO SIMULADOS ---
SESIONES_SERVIDOR = {}  # {session_id: {"user": str, "role": str}}
BLACKLIST_JWT = set()   # Lista negra de tokens revocados

def crear_sesion(usuario, rol):
    session_id = f"sess_{usuario}_{int(time.time())}"
    SESIONES_SERVIDOR[session_id] = {"user": usuario, "role": rol}
    return session_id

def destruir_sesion(session_id):
    SESIONES_SERVIDOR.pop(session_id, None)

def crear_jwt(usuario, rol, exp_segundos=300):
    payload = {
        "sub": usuario,
        "role": rol,
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=exp_segundos)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# --- CONTROLADORES DE RUTAS Y SEGURIDAD ---
def evaluar_acceso_sesion(session_id, requiere_admin=False):
    if not session_id or session_id not in SESIONES_SERVIDOR:
        return 401, "Unauthorized: Sesión inválida o inexistente"
    
    usuario_info = SESIONES_SERVIDOR[session_id]
    if requiere_admin and usuario_info["role"] != "admin":
        return 403, "Forbidden: Permisos insuficientes"
    
    return 200, f"OK: Bienvenido {usuario_info['user']}"

def evaluar_acceso_jwt(token, requiere_admin=False, usar_blacklist=False):
    if not token:
        return 401, "Unauthorized: Token ausente"
    
    if usar_blacklist and token in BLACKLIST_JWT:
        return 401, "Unauthorized: Token revocado en lista negra"

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if requiere_admin and payload.get("role") != "admin":
            return 403, "Forbidden: Permisos insuficientes"
        return 200, f"OK: Bienvenido {payload.get('sub')}"
    except jwt.ExpiredSignatureError:
        return 401, "Unauthorized: Token expirado"
    except jwt.InvalidTokenError:
        return 401, "Unauthorized: Firma de token manipulada/inválida"

# --- BATERÍA DE 7 PRUEBAS ---
def ejecutar_bateria_pruebas():
    print("=== BATERÍA DE 7 CASOS DE SEGURIDAD Y AUTORIZACIÓN ===")
    
    # Pre-crear credenciales válidas (Usuario estándar y Admin)
    sess_std = crear_sesion("ana_ruiz", "user")
    jwt_std = crear_jwt("ana_ruiz", "user", exp_segundos=10)
    
    jwt_expirado = crear_jwt("carlos_gomez", "user", exp_segundos=-10)
    jwt_manipulado = jwt_std[:-5] + "XXXXX"

    casos = [
        ("1. Sin Credencial", None, None, False),
        ("2. Credencial Válida (Usuario)", sess_std, jwt_std, False),
        ("3. Acceso a Recurso Admin (RBAC)", sess_std, jwt_std, True),
        ("4. Token Firmado Manipulado", None, jwt_manipulado, False),
        ("5. Token Firmado Expirado", None, jwt_expirado, False),
    ]

    print(f"{'Caso de Prueba':<35} | {'Sesión (Stateful)':<18} | {'JWT (Stateless)':<18}")
    print("-" * 77)

    for nombre, s_id, j_tok, req_admin in casos:
        status_s, _ = evaluar_acceso_sesion(s_id, requiere_admin=req_admin)
        status_j, _ = evaluar_acceso_jwt(j_tok, requiere_admin=req_admin)
        print(f"{nombre:<35} | HTTP {status_s:<13} | HTTP {status_j:<13}")

    # Caso 6: Medicion de Revocacion tras Logout
    print("\n--- CASO 6: MEDICIÓN DE TIEMPO DE REVOCACIÓN TRAS LOGOUT ---")
    destruir_sesion(sess_std)
    status_s_post, _ = evaluar_acceso_sesion(sess_std)
    
    # JWT Sin Lista Negra (Stateless puro)
    status_j_stateless, _ = evaluar_acceso_jwt(jwt_std, usar_blacklist=False)
    
    # JWT Con Lista Negra
    BLACKLIST_JWT.add(jwt_std)
    status_j_stateful, _ = evaluar_acceso_jwt(jwt_std, usar_blacklist=True)

    print(f"Sesión tras Logout: HTTP {status_s_post} (Revocación Instantánea: 0 segundos)")
    print(f"JWT Stateless tras Logout: HTTP {status_j_stateless} (Token SIGUE VÁLIDO hasta su expiración)")
    print(f"JWT con Blacklist tras Logout: HTTP {status_j_stateful} (Requiere estado en servidor para revocar)")

    # Caso 7: Riesgo de Almacenamiento en Cliente (XSS vs HttpOnly)
    print("\n--- CASO 7: VECTOR DE ALMACENAMIENTO EN CLIENTE (XSS vs CSRF) ---")
    print("  - JWT en localStorage: Vulnerable a lecturas exfiltradas por XSS (script inyectado).")
    print("  - Sesión / JWT en Cookie HttpOnly + SameSite=Strict: Protegido contra XSS, requiere anti-CSRF token.")

if __name__ == "__main__":
    obtener_header()
    ejecutar_bateria_pruebas()