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
