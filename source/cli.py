# Para darle un toque mas profesional aqui hacemo una interfaz de línea de comandos interactiva para el sistema IAM con RBAC
# Permite gestionar usuarios, roles, recursos y verificar accesos de forma interactiva.

import sys
import os

# Aseguramos que Python encuentre los módulos del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sistemaa_IAM_principal import IAMSystem


#  presentación bonita

def banner():
    print("""
    Simulador IAM con RBAC  de Joan Cobos, Roc Reverté y Daniel Baena         
""")


def ok(msg: str):
    print(f"   {msg}")


def err(msg: str):
    print(f"  ERROR: {msg}")


def info(msg: str):
    print(f"  {msg}")


# menus

MENU_PRINCIPAL = """
  1 Gestión de usuarios
  2 Gestión de roles
  3 Gestión de recursos
  4 Verificar acceso
  5 Informe de usuario
  6 Log de auditoría
  7 Cargar escenario de demo
  0 Salir
"""

MENU_USUARIOS = """
  1 Crear usuario
  2 Eliminar usuario
  3 Asignar rol a usuario
  4 Revocar rol de usuario
  5 Listar usuarios
  0 Volver
"""


def pedir(prompt: str) -> str:
    return input(f" {prompt}: ").strip()

# Submenus

def menu_usuarios(iam: IAMSystem):
    while True:
        print(MENU_USUARIOS)
        op = pedir("Opción")
        if op == "1":
            nombre = pedir("Nombre del nuevo usuario")
            try:
                u = iam.crear_usuario(nombre)
                ok(u.describir())
            except ValueError as e:
                err(str(e))

        elif op == "2":
            nombre = pedir("Nombre del usuario a eliminar")
            if iam.eliminar_usuario(nombre):
                ok(f"Usuario '{nombre}' eliminado.")
            else:
                err(f"Usuario '{nombre}' no encontrado.")

        elif op == "3":
            nombre_u = pedir("Nombre del usuario")
            nombre_r = pedir("Nombre del rol")
            try:
                if iam.asignar_rol_a_usuario(nombre_u, nombre_r):
                    ok(f"Rol '{nombre_r}' asignado a '{nombre_u}'.")
                else:
                    info(f"El usuario ya tenía ese rol.")
            except (KeyError, ValueError) as e:
                err(str(e))

        elif op == "4":
            nombre_u = pedir("Nombre del usuario")
            nombre_r = pedir("Nombre del rol a revocar")
            try:
                if iam.revocar_rol_de_usuario(nombre_u, nombre_r):
                    ok(f"Rol '{nombre_r}' revocado de '{nombre_u}'.")
                else:
                    info(f"El usuario no tenía ese rol.")
            except KeyError as e:
                err(str(e))

        elif op == "5":
            usuarios = iam.listar_usuarios()
            if not usuarios:
                info("No hay usuarios registrados.")
            else:
                print()
                for u in usuarios:
                    print(f"    {u.describir()}")
                print()

        elif op == "0":
            break
        else:
            err("Opción no válida.")

# Main

def main():
    banner()
    iam = IAMSystem("BaCoRe")

    while True:
        print(MENU_PRINCIPAL)
        op = pedir("Opción")
        if op == "1":
            menu_usuarios(iam)
        
        elif op == "0":
            print("\n  Cerrando sistema IAM. Hasta luego.\n")
            break
        else:
            err("Opción no disponible todavía.")


if __name__ == "__main__":
    main()
