#Este es nuestro programa principal del IAM con RBAC que queremos llevar a cabo.
#Gestiona usuarios, roles y recursos
#También verifica el acceso con herencia recursiva

from entities import Entidad, Usuario, Rol, Recurso
import time

class IAMSystem:
    
    #  Sistema central de gestión de identidades y accesos, el IAM.
    # Almacena usuarios, roles y recursos en diccionarios con tablas hash — O(1) acceso.
    # Coordina la verificación de permisos con soporte de herencia de roles.
    

    def __init__(self, nombre_empresa: str = "Empresa"):
        self._nombre_empresa = nombre_empresa
        #O(1)
        self._usuarios: dict[str, Usuario] = {}
        self._roles: dict[str, Rol] = {}
        self._recursos: dict[str, Recurso] = {}
        self._log_auditoria: list[dict] = []

    # GESTIÓ DE USUARIOS

    def crear_usuario(self, nombre: str) -> Usuario:
        #Crea y registra un nuevo usuario.
        #O(1)
        
        if nombre in self._usuarios:
            raise ValueError(f"El usuario '{nombre}' ya existe.")
        u = Usuario(nombre)
        self._usuarios[nombre] = u
        self._registrar_evento("CREAR_USUARIO", f"Usuario '{nombre}' creado.")
        return u

    def obtener_usuario(self, nombre: str) -> Usuario:
        #O(1)
        if nombre not in self._usuarios:
            raise KeyError(f"Usuario '{nombre}' no encontrado.")
        return self._usuarios[nombre]

    def eliminar_usuario(self, nombre: str) -> bool:
        # Elimina un usuario del sistema.
        #O(1)

        if nombre not in self._usuarios:
            return False
        del self._usuarios[nombre]
        self._registrar_evento("ELIMINAR_USUARIO", f"Usuario '{nombre}' eliminado.")
        return True

    def listar_usuarios(self) -> list[Usuario]:
        #O(n)
        return list(self._usuarios.values())


    # GESTIÓN DE ROLES

    def crear_rol(self, nombre: str, padre_nombre: str | None = None) -> Rol:
        #Crea un rol, opcionalmente heredando de otro.
        #O(1)

        if nombre in self._roles:
            raise ValueError(f"El rol '{nombre}' ya existe.")
        padre = None
        if padre_nombre:
            if padre_nombre not in self._roles:
                raise KeyError(f"Rol padre '{padre_nombre}' no encontrado.")
            padre = self._roles[padre_nombre]
        r = Rol(nombre, padre)
        self._roles[nombre] = r
        herencia_str = f" (hereda de '{padre_nombre}')" if padre_nombre else ""
        self._registrar_evento("CREAR_ROL", f"Rol '{nombre}'{herencia_str} creado.")
        return r

    def obtener_rol(self, nombre: str) -> Rol:
        #O(1)
        if nombre not in self._roles:
            raise KeyError(f"Rol '{nombre}' no encontrado.")
        return self._roles[nombre]

    def listar_roles(self) -> list[Rol]:
        # O(n)
        return list(self._roles.values())

    # GESTIÓN DE RECURSOS

    def crear_recurso(self, nombre: str, nivel: str = "medio") -> Recurso:
       
        #Registra un recurso protegido.
        #O(1)

        if nombre in self._recursos:
            raise ValueError(f"El recurso '{nombre}' ya existe.")
        rec = Recurso(nombre, nivel)
        self._recursos[nombre] = rec
        self._registrar_evento("CREAR_RECURSO", f"Recurso '{nombre}' [nivel:{nivel}] creado.")
        return rec

    def obtener_recurso(self, nombre: str) -> Recurso:
        #O(1)
        if nombre not in self._recursos:
            raise KeyError(f"Recurso '{nombre}' no encontrado.")
        return self._recursos[nombre]

    def listar_recursos(self) -> list[Recurso]:
        #O(n)
        return list(self._recursos.values())

    # ROLES Y PERMISOS

    def asignar_rol_a_usuario(self, nombre_usuario: str, nombre_rol: str) -> bool:

        #Asigna un rol existente a un usuario existente.
        #O(1)
        
        u = self.obtener_usuario(nombre_usuario)
        r = self.obtener_rol(nombre_rol)
        resultado = u.asignar_rol(r)
        if resultado:
            self._registrar_evento(
                "ASIGNAR_ROL",
                f"Rol '{nombre_rol}' asignado a usuario '{nombre_usuario}'."
            )
        return resultado

    def revocar_rol_de_usuario(self, nombre_usuario: str, nombre_rol: str) -> bool:
        #O(1)
        u = self.obtener_usuario(nombre_usuario)
        r = self.obtener_rol(nombre_rol)
        resultado = u.revocar_rol(r)
        if resultado:
            self._registrar_evento(
                "REVOCAR_ROL",
                f"Rol '{nombre_rol}' revocado de usuario '{nombre_usuario}'."
            )
        return resultado

    def agregar_permiso_a_rol(self, nombre_rol: str, permiso: str) -> bool:
        #O(1)
        r = self.obtener_rol(nombre_rol)
        resultado = r.agregar_permiso(permiso)
        if resultado:
            self._registrar_evento(
                "AGREGAR_PERMISO",
                f"Permiso '{permiso}' añadido al rol '{nombre_rol}'."
            )
        return resultado

    def agregar_permiso_requerido_a_recurso(self, nombre_recurso: str, permiso: str) -> None:
        #O(1)
        rec = self.obtener_recurso(nombre_recurso)
        rec.agregar_permiso_requerido(permiso)

    # VERIFICACIÓN DE ACCESO

    def verificar_acceso(self, nombre_usuario: str, nombre_recurso: str) -> bool:

        #Verifica si un usuario puede acceder a un recurso.
        #Proceso: coge los permisos requeridos por el recurso, leugo para cada rol del usuario, comprueba recursivamente si tiene
        # cada permiso  — O(r·h·p) donde:
        #  r = número de roles del usuario
        #  h = profundidad de herencia de cada rol
        #  p = permisos requeridos por el recurso

        # O(r·h·p)
        
        try:
            u = self.obtener_usuario(nombre_usuario)
            rec = self.obtener_recurso(nombre_recurso)
        except KeyError as e:
            self._registrar_evento("ACCESO_ERROR", str(e))
            return False

        permisos_requeridos = rec.permisos_requeridos()

        # Si el recurso no requiere ningún permiso, acceso libre
        if not permisos_requeridos:
            self._registrar_evento(
                "ACCESO_CONCEDIDO",
                f"'{nombre_usuario}' -> '{nombre_recurso}' (sin restricciones)"
            )
            return True

        # recogemos todos los permisos del usuario
        permisos_usuario = self._obtener_permisos_usuario(u)

        # Comprobamos si el usuario tiene TODOS los permisos requeridos
        tiene_acceso = permisos_requeridos.issubset(permisos_usuario)

        evento = "ACCESO_CONCEDIDO" if tiene_acceso else "ACCESO_DENEGADO"
        self._registrar_evento(
            evento,
            f"'{nombre_usuario}' -> '{nombre_recurso}' | "
            f"requerido: {sorted(permisos_requeridos)} | "
            f"disponible: {sorted(permisos_usuario)}"
        )
        return tiene_acceso

    def _obtener_permisos_usuario(self, usuario: Usuario) -> set[str]:
        
        #Agrega todos los permisos de todos los roles del usuario.
        #O(r·h·p)
        
        permisos = set()
        for rol in usuario.roles:
            # Llamada recursiva dentro de Rol.obtener_todos_permisos
            permisos |= rol.obtener_todos_permisos()
        return permisos

    def informe_usuario(self, nombre_usuario: str) -> dict:
        
        #Genera un informe completo de permisos y accesos de un usuario.
        # O(r·h·p + R) donde R = número total de recursos

        u = self.obtener_usuario(nombre_usuario)
        permisos = self._obtener_permisos_usuario(u)

        recursos_accesibles = []
        recursos_denegados = []
        for nombre_rec, rec in self._recursos.items():
            req = rec.permisos_requeridos()
            if not req or req.issubset(permisos):
                recursos_accesibles.append(nombre_rec)
            else:
                recursos_denegados.append(nombre_rec)

        return {
            "usuario": nombre_usuario,
            "roles": [r.nombre for r in u.roles],
            "permisos_efectivos": sorted(permisos),
            "recursos_accesibles": sorted(recursos_accesibles),
            "recursos_denegados": sorted(recursos_denegados),
        }

    # AUDITORÍA

    def _registrar_evento(self, tipo: str, detalle: str) -> None:

        #Registra un evento en el log de auditoría.
        # O(1) amortizado (append en lista)

        self._log_auditoria.append({
            "timestamp": time.time(),
            "tipo": tipo,
            "detalle": detalle,
        })

    def obtener_log(self, filtro_tipo: str | None = None) -> list[dict]:
        # Devuelve el log, opcionalmente filtrado por tipo de evento.
        # O(n)

        if filtro_tipo is None:
            return list(self._log_auditoria)
        return [e for e in self._log_auditoria if e["tipo"] == filtro_tipo]

    def imprimir_log(self, n_ultimos: int | None = None) -> None:
        # Imprime los últimos n eventos del log.
        log = self._log_auditoria if n_ultimos is None else self._log_auditoria[-n_ultimos:]
        print(f"  LOG DE AUDITORÍA — {self._nombre_empresa}")
        for e in log:
            ts = time.strftime("%H:%M:%S", time.localtime(e["timestamp"]))
            print(f"  [{ts}] [{e['tipo']:20s}] {e['detalle']}")
