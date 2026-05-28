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
