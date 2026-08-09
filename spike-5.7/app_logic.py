class ServicioPrestamos:
    def __init__(self, bug_flags=None):
        # Permite inyectar 5 fallos (mutaciones) a propósito para evaluar las pruebas
        self.bug_flags = bug_flags or {}

    def validar_prestamo(self, dias: int, solicitante: str) -> bool:
        # FALLO INYECTADO 1: Omite la validación de días negativos si la bandera está activa
        if self.bug_flags.get("bug1_validacion_bypassed"):
            if not solicitante:
                return False
            return True  # Acepta días <= 0 erróneamente

        if not solicitante or len(solicitante) < 3:
            return False
        if dias <= 0 or dias > 30:
            return False
        return True

    def verificar_permiso(self, rol: str, dueno_recurso: str, usuario_actual: str) -> bool:
        # FALLO INYECTADO 2: Falla de RBAC (permite a cualquier usuario acceder a recursos ajenos)
        if self.bug_flags.get("bug2_rbac_flaw"):
            return True  # Ignora la comprobación de rol y dueño

        if rol == "admin":
            return True
        return dueno_recurso == usuario_actual

    def calcular_fecha_devolucion(self, dia_inicio: int, dias: int) -> int:
        # FALLO INYECTADO 3: Error de lógica de negocio (resta en lugar de sumar)
        if self.bug_flags.get("bug3_calculo_erroneo"):
            return dia_inicio - dias

        return dia_inicio + dias

    def filtrar_prestamos(self, prestamos: list[dict], usuario_consulta: str) -> list[dict]:
        # FALLO INYECTADO 4: Error de filtrado (devuelve todos los préstamos sin filtrar)
        if self.bug_flags.get("bug4_filtro_roto"):
            return prestamos

        return [p for p in prestamos if p["solicitante"] == usuario_consulta]

    def crear_prestamo_endpoint(self, payload: dict, rol_usuario: str, usuario_actual: str):
        # FALLO INYECTADO 5: Devuelve HTTP 200 en lugar de HTTP 400 cuando los datos son inválidos
        es_valido = self.validar_prestamo(payload.get("dias", 0), payload.get("solicitante", ""))
        if not es_valido:
            if self.bug_flags.get("bug5_status_code_malo"):
                return 200, {"error": "Datos inválidos"}  # Código de estado erróneo
            return 400, {"error": "Datos inválidos"}

        tiene_permiso = self.verificar_permiso(rol_usuario, payload.get("solicitante"), usuario_actual)
        if not tiene_permiso:
            return 403, {"error": "Sin autorización"}

        fecha_dev = self.calcular_fecha_devolucion(10, payload["dias"])
        return 201, {"ok": True, "dia_devolucion": fecha_dev}