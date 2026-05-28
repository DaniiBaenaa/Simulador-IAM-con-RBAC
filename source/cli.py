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


def pedir(prompt: str) -> str:
    return input(f" {prompt}: ").strip()


# Main

def main():
    banner()
    iam = IAMSystem("BaCoRe")

    while True:
        print(MENU_PRINCIPAL)
        op = pedir("Opción")

        if op == "0":
            print("\n  Cerrando sistema IAM. Hasta luego.\n")
            break
        else:
            err("Opción no disponible todavía.")


if __name__ == "__main__":
    main()
