#Pruebas unitarias del sistema IAM con RBAC
#Lo hacemos para poder comprobar el comportamiento correcto de todas las funcionalidades principales.
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(file)))

from entities import Usuario, Rol, Recurso
from sistemaa_IAM_principal import IAMSystem


class TestEntidades(unittest.TestCase):

    def test_usuario_creacion(self):
        u = Usuario("alice")
        self.assertEqual(u.nombre, "alice")
        self.assertEqual(u.tipo(), "Usuario")
        self.assertEqual(len(u.roles), 0)

    def test_rol_creacion(self):
        r = Rol("admin")
        self.assertEqual(r.nombre, "admin")
        self.assertIsNone(r.padre)

    def test_rol_agregar_permiso(self):
        r = Rol("dev")
        self.assertTrue(r.agregar_permiso("leer_codigo"))
        self.assertFalse(r.agregar_permiso("leer_codigo"))  # duplicado

    def test_rol_revocar_permiso(self):
        r = Rol("dev")
        r.agregar_permiso("leer_codigo")
        self.assertTrue(r.revocar_permiso("leer_codigo"))
        self.assertFalse(r.revocar_permiso("leer_codigo"))  # ya no existe

    def test_recurso_nivel_invalido(self):
        with self.assertRaises(ValueError):
            Recurso("archivo", nivel="secretisimo")

    def test_recurso_nivel_valido(self):
        rec = Recurso("bd", nivel="critico")
        self.assertEqual(rec.nivel, "critico")

class TestHerenciaRoles(unittest.TestCase):

    def setUp(self):
        self.empleado = Rol("empleado")
        self.developer = Rol("developer", padre=self.empleado)
        self.admin = Rol("admin", padre=self.developer)

        self.empleado.agregar_permiso("leer_informes")
        self.developer.agregar_permiso("leer_codigo")
        self.developer.agregar_permiso("escribir_codigo")
        self.admin.agregar_permiso("gestionar_usuarios")

    def test_permiso_directo(self):
        self.assertTrue(self.developer.tiene_permiso_directo("leer_codigo"))
        self.assertFalse(self.developer.tiene_permiso_directo("leer_informes"))

    def test_permiso_heredado_un_nivel(self):
        # developer hereda de empleado
        self.assertTrue(self.developer.tiene_permiso("leer_informes"))

    def test_permiso_heredado_dos_niveles(self):
        # admin hereda de developer que hereda de empleado
        self.assertTrue(self.admin.tiene_permiso("leer_informes"))
        self.assertTrue(self.admin.tiene_permiso("leer_codigo"))
        self.assertTrue(self.admin.tiene_permiso("gestionar_usuarios"))

    def test_permiso_no_existente(self):
        self.assertFalse(self.empleado.tiene_permiso("acceso_total"))

    def test_obtener_todos_permisos(self):
        todos = self.admin.obtener_todos_permisos()
        self.assertIn("leer_informes", todos)
        self.assertIn("leer_codigo", todos)
        self.assertIn("escribir_codigo", todos)
        self.assertIn("gestionar_usuarios", todos)
        self.assertEqual(len(todos), 4)

    def test_sin_ciclos_infinitos(self):
        # El sistema no debe entrar en bucle si hay un ciclo en los roles.
        r1 = Rol("r1")
        r2 = Rol("r2", padre=r1)
        r1._padre = r2
        # No deberia de lanzar RecursionError
        resultado = r1.tiene_permiso("algo")
        self.assertFalse(resultado)

class TestIAMSystem(unittest.TestCase):

    def setUp(self):
        self.iam = IAMSystem("Test Corp")

    def test_crear_usuario_duplicado(self):
        self.iam.crear_usuario("alice")
        with self.assertRaises(ValueError):
            self.iam.crear_usuario("alice")

    def test_obtener_usuario_inexistente(self):
        with self.assertRaises(KeyError):
            self.iam.obtener_usuario("nadie")

    def test_eliminar_usuario(self):
        self.iam.crear_usuario("bob")
        self.assertTrue(self.iam.eliminar_usuario("bob"))
        self.assertFalse(self.iam.eliminar_usuario("bob"))

    def test_crear_rol_con_herencia(self):
        self.iam.crear_rol("base")
        self.iam.crear_rol("avanzado", padre_nombre="base")
        r = self.iam.obtener_rol("avanzado")
        self.assertIsNotNone(r.padre)
        self.assertEqual(r.padre.nombre, "base")

    def test_verificar_acceso_concedido(self):
        self.iam.crear_rol("viewer")
        self.iam.agregar_permiso_a_rol("viewer", "leer")
        self.iam.crear_usuario("carol")
        self.iam.asignar_rol_a_usuario("carol", "viewer")
        self.iam.crear_recurso("doc", nivel="bajo")
        self.iam.agregar_permiso_requerido_a_recurso("doc", "leer")
        self.assertTrue(self.iam.verificar_acceso("carol", "doc"))

    def test_verificar_acceso_denegado(self):
        self.iam.crear_rol("viewer")
        self.iam.agregar_permiso_a_rol("viewer", "leer")
        self.iam.crear_usuario("dave")
        self.iam.asignar_rol_a_usuario("dave", "viewer")
        self.iam.crear_recurso("secreto", nivel="alto")
        self.iam.agregar_permiso_requerido_a_recurso("secreto", "escribir")
        self.assertFalse(self.iam.verificar_acceso("dave", "secreto"))

    def test_verificar_acceso_por_herencia(self):
        #Aqui tenemos un admin que hereda de developer puede acceder a recursos de developer.
        self.iam.crear_rol("developer")
        self.iam.agregar_permiso_a_rol("developer", "leer_codigo")
        self.iam.crear_rol("admin", padre_nombre="developer")
        self.iam.agregar_permiso_a_rol("admin", "gestionar_usuarios")

        self.iam.crear_usuario("superuser")
        self.iam.asignar_rol_a_usuario("superuser", "admin")

        self.iam.crear_recurso("repo", nivel="medio")
        self.iam.agregar_permiso_requerido_a_recurso("repo", "leer_codigo")

        # admin hereda leer_codigo de developer -> acceso concedido
        self.assertTrue(self.iam.verificar_acceso("superuser", "repo"))

    def test_recurso_sin_permisos_requeridos(self):
        """Un recurso sin permisos requeridos es accesible por todos."""
        self.iam.crear_usuario("anonimo")
        self.iam.crear_recurso("publico", nivel="bajo")
        self.assertTrue(self.iam.verificar_acceso("anonimo", "publico"))

    def test_informe_usuario(self):
        self.iam.crear_rol("emp")
        self.iam.agregar_permiso_a_rol("emp", "leer_informes")
        self.iam.crear_usuario("eve")
        self.iam.asignar_rol_a_usuario("eve", "emp")
        self.iam.crear_recurso("informe", nivel="bajo")
        self.iam.agregar_permiso_requerido_a_recurso("informe", "leer_informes")

        informe = self.iam.informe_usuario("eve")
        self.assertIn("leer_informes", informe["permisos_efectivos"])
        self.assertIn("informe", informe["recursos_accesibles"])

    def test_log_auditoria(self):
        self.iam.crear_usuario("frank")
        log = self.iam.obtener_log()
        self.assertTrue(any(e["tipo"] == "CREAR_USUARIO" for e in log))

    def test_revocar_rol(self):
        self.iam.crear_rol("role_x")
        self.iam.agregar_permiso_a_rol("role_x", "perm_x")
        self.iam.crear_usuario("grace")
        self.iam.asignar_rol_a_usuario("grace", "role_x")
        self.iam.crear_recurso("res_x", nivel="bajo")
        self.iam.agregar_permiso_requerido_a_recurso("res_x", "perm_x")

        self.assertTrue(self.iam.verificar_acceso("grace", "res_x"))
        self.iam.revocar_rol_de_usuario("grace", "role_x")
        self.assertFalse(self.iam.verificar_acceso("grace", "res_x"))
