#Aquí encontramos las clases base de nuestro sistema
# la jerarquia que seguimos en POO es: entidad --> usuario / rol / recurso
# para implementar polimorfismo en cada subclase implementamos su proprio describir() y tipo()

from abc import ABC, abstractmethod

class Entidad(ABC):
    
    # Clase abstracta base para todos los elementos del sistema IAM.
    # Aplicamos POO mediante métodos abstractos.

    def __init__(self, nombre: str):
        # O(1)
        self._nombre = nombre

    @property
    def nombre(self) -> str:
        return self._nombre

    @abstractmethod
    def describir(self) -> str:
        pass

    @abstractmethod
    def tipo(self) -> str:
        pass

    def __repr__(self) -> str:
        return f"{self.tipo()}({self._nombre!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entidad):
            return NotImplemented
        return self._nombre == other._nombre and self.tipo() == other.tipo()

    def __hash__(self) -> int:
        return hash((self._nombre, self.tipo()))


class Usuario(Entidad):
    #  Representa un usuario del sistema.
    # Puede tener uno o más roles asignados.

    def __init__(self, nombre: str):
        super().__init__(nombre)
        # O(1) 
        self._roles: set = set()

    @property
    def roles(self) -> set:
        return frozenset(self._roles)

    def asignar_rol(self, rol: "Rol") -> bool:
        #Asigna un rol al usuario.
        #O(1)
        #Retorna True si se ha añadido, False si ya existía.
        
        if rol in self._roles:
            return False
        self._roles.add(rol)
        return True

    def revocar_rol(self, rol: "Rol") -> bool:
        
        #Revoca un rol del usuario.
        #O(1)

        if rol not in self._roles:
            return False
        self._roles.discard(rol)
        return True

    def describir(self) -> str:
        roles_str = ", ".join(r.nombre for r in self._roles) if self._roles else "ninguno"
        return f"Usuario '{self._nombre}' — roles asignados: [{roles_str}]"

    def tipo(self) -> str:
        return "Usuario"


class Rol(Entidad):
    
    #Representa un rol dentro del sistema RBAC.
    # Soporta herencia de roles: un Rol puede tener un rol padre.
    # Los permisos se almacenan en un set.

    def __init__(self, nombre: str, padre: "Rol | None" = None):
        super().__init__(nombre)
        #O(1) inserción, O(1) búsqueda
        self._permisos: set[str] = set()
        self._padre: Rol | None = padre

    @property
    def padre(self) -> "Rol | None":
        return self._padre

    def establecer_padre(self, padre: "Rol") -> None:
        #Establece herencia de roles.
        #O(1)
        self._padre = padre

    def agregar_permiso(self, permiso: str) -> bool:
        
        #Añade un permiso directo al rol.
        #O(1)
        #Retorna False si el permiso ya existía.

        if permiso in self._permisos:
            return False
        self._permisos.add(permiso)
        return True

    def revocar_permiso(self, permiso: str) -> bool:
        #Elimina un permiso del rol.
        #O(1)

        if permiso not in self._permisos:
            return False
        self._permisos.discard(permiso)
        return True

    def tiene_permiso_directo(self, permiso: str) -> bool:
        
        #Comprueba si el rol tiene el permiso de forma direct.
        # O(1)
        return permiso in self._permisos

    def tiene_permiso(self, permiso: str, visitados: set | None = None) -> bool:
        #Comprueba si el rol tiene el permiso, incluyendo herencia recursiva.
        #O(h·p) ya que h = profundidad de herencia, p = permisos por rol

        if visitados is None:
            visitados = set()

        #Evitar ciclos
        if self._nombre in visitados:
            return False
        visitados.add(self._nombre)

        #O(1)
        if self.tiene_permiso_directo(permiso):
            return True

        # O(h·p)
        if self._padre is not None:
            return self._padre.tiene_permiso(permiso, visitados)

        return False

    def obtener_todos_permisos(self, visitados: set | None = None) -> set[str]:
        
        #Devuelve todos los permisos como un set.
        #O(h·p)
        if visitados is None:
            visitados = set()

        if self._nombre in visitados:
            return set()
        visitados.add(self._nombre)

        permisos = set(self._permisos)

        if self._padre is not None:
            permisos |= self._padre.obtener_todos_permisos(visitados)

        return permisos

    @property
    def permisos_directos(self) -> frozenset:
        return frozenset(self._permisos)

    def describir(self) -> str:
        padre_str = f", hereda de '{self._padre.nombre}'" if self._padre else ""
        permisos_str = ", ".join(sorted(self._permisos)) if self._permisos else "ninguno"
        return f"Rol '{self._nombre}'{padre_str} — permisos directos: [{permisos_str}]"

    def tipo(self) -> str:
        return "Rol"
    

class Recurso(Entidad):
    # Representa un recurso protegido del sistema (archivo, servicio, endpoint...).
    # Cada recurso tiene un nivel de sensibilidad y un set de permisos requeridos.

    NIVELES = {"bajo", "medio", "alto", "critico"}

    def __init__(self, nombre: str, nivel: str = "medio"):
        super().__init__(nombre)
        if nivel not in self.NIVELES:
            raise ValueError(f"Nivel '{nivel}' no válido. Opciones: {self.NIVELES}")
        self._nivel = nivel
        # Set de permisos requeridos para acceder — O(1) consulta
        self._permisos_requeridos: set[str] = set()

    @property
    def nivel(self) -> str:
        return self._nivel

    def agregar_permiso_requerido(self, permiso: str) -> None:
        #O(1)
        self._permisos_requeridos.add(permiso)

    def permisos_requeridos(self) -> frozenset:
        return frozenset(self._permisos_requeridos)

    def describir(self) -> str:
        req_str = ", ".join(sorted(self._permisos_requeridos)) if self._permisos_requeridos else "ninguno"
        return f"Recurso '{self._nombre}' [nivel: {self._nivel}] — permisos requeridos: [{req_str}]"

    def tipo(self) -> str:
        return "Recurso"
