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

MENU_ROLES = """
  1 Crear rol
  2 Añadir permiso a rol
  3 Revocar permiso de rol
  4 Ver detalle de rol
  5 Listar roles
  0 Volver
"""

MENU_RECURSOS = """
  1 Crear recurso
  2 Añadir permiso requerido a recurso
  3 Listar recursos
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

def menu_roles(iam: IAMSystem):
    while True:
        print(MENU_ROLES)
        op = pedir("Opción")

        if op == "1":
            nombre = pedir("Nombre del nuevo rol")
            padre = pedir("Nombre del rol padre (Enter para ninguno)")
            try:
                r = iam.crear_rol(nombre, padre if padre else None)
                ok(r.describir())
            except (ValueError, KeyError) as e:
                err(str(e))

        elif op == "2":
            nombre_r = pedir("Nombre del rol")
            permiso = pedir("Permiso a añadir")
            try:
                if iam.agregar_permiso_a_rol(nombre_r, permiso):
                    ok(f"Permiso '{permiso}' añadido al rol '{nombre_r}'.")
                else:
                    info("El rol ya tenía ese permiso.")
            except KeyError as e:
                err(str(e))

        elif op == "3":
            nombre_r = pedir("Nombre del rol")
            permiso = pedir("Permiso a revocar")
            try:
                r = iam.obtener_rol(nombre_r)
                if r.revocar_permiso(permiso):
                    ok(f"Permiso '{permiso}' revocado del rol '{nombre_r}'.")
                else:
                    info("El rol no tenía ese permiso.")
            except KeyError as e:
                err(str(e))

        elif op == "4":
            nombre_r = pedir("Nombre del rol")
            try:
                r = iam.obtener_rol(nombre_r)
                print()
                print(f"    {r.describir()}")
                todos = r.obtener_todos_permisos()
                heredados = todos - r.permisos_directos
                if heredados:
                    print(f"    Permisos heredados: [{', '.join(sorted(heredados))}]")
                print(f"    Permisos efectivos totales: [{', '.join(sorted(todos))}]")
                print()
            except KeyError as e:
                err(str(e))

        elif op == "5":
            roles = iam.listar_roles()
            if not roles:
                info("No hay roles registrados.")
            else:
                print()
                for r in roles:
                    print(f"    {r.describir()}")
                print()

        elif op == "0":
            break
        else:
            err("Opción no válida.")

def menu_recursos(iam: IAMSystem):
    while True:
        print(MENU_RECURSOS)
        op = pedir("Opción")

        if op == "1":
            nombre = pedir("Nombre del recurso")
            nivel = pedir("Nivel de sensibilidad (bajo/medio/alto/critico)")
            try:
                rec = iam.crear_recurso(nombre, nivel)
                ok(rec.describir())
            except (ValueError, KeyError) as e:
                err(str(e))

        elif op == "2":
            nombre_rec = pedir("Nombre del recurso")
            permiso = pedir("Permiso requerido")
            try:
                iam.agregar_permiso_requerido_a_recurso(nombre_rec, permiso)
                ok(f"Permiso '{permiso}' añadido como requerido en '{nombre_rec}'.")
            except KeyError as e:
                err(str(e))

        elif op == "3":
            recursos = iam.listar_recursos()
            if not recursos:
                info("No hay recursos registrados.")
            else:
                print()
                for rec in recursos:
                    print(f"    {rec.describir()}")
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

        elif op == "2":
            menu_roles(iam)
        
        elif op == "3":
            menu_recursos(iam)

        elif op == "4":
            nombre_u = pedir("Nombre del usuario")
            nombre_rec = pedir("Nombre del recurso")
            resultado = iam.verificar_acceso(nombre_u, nombre_rec)
            if resultado:
                ok(f" CONCEDIDO — '{nombre_u}' puede acceder a '{nombre_rec}'")
            else:
                print(f"  DENEGADO — '{nombre_u}' no tiene permisos para '{nombre_rec}'")

        elif op == "5":
            nombre_u = pedir("Nombre del usuario")
            try:
                informe = iam.informe_usuario(nombre_u)
                print(f"  INFORME: {informe['usuario']}")
                print(f"  Roles asignados     : {', '.join(informe['roles']) or 'ninguno'}")
                print(f"  Permisos efectivos  : {', '.join(informe['permisos_efectivos']) or 'ninguno'}")
                print(f"  Recursos accesibles : {', '.join(informe['recursos_accesibles']) or 'ninguno'}")
                print(f"  Recursos denegados  : {', '.join(informe['recursos_denegados']) or 'ninguno'}")
            except KeyError as e:
                err(str(e))

        elif op == "6":
            filtro = pedir("Filtrar por tipo de evento (Enter para todos)")
            iam.imprimir_log(filtro_tipo=filtro if filtro else None)
        
        elif op == "0":
            print("\n  Cerrando sistema IAM. Hasta luego.\n")
            break
        else:
            err("Opción no disponible todavía.")


if __name__ == "__main__":
    main()
