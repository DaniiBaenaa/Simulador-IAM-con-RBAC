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
