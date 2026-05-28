# Aqui hacemos el análisis empírico de tiempos del sistema
# Mide tiempos medios de las operaciones principales para validar el análisis teórico.
# Genera resultados en consola y exporta datos para gráficas.

import sys
import os
import time
import random
import string
import statistics

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sistemaa_IAM_principal import IAMSystem


def nombre_aleatorio(longitud: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=longitud))


def medir(funcion, repeticiones: int = 1000) -> dict:
    #Ejecuta una función N veces y devuelve estadísticas de tiempo.

    tiempos = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        funcion()
        fin = time.perf_counter()
        tiempos.append((fin - inicio) * 1_000_000)  # microsegundos
    return {
        "min":    round(min(tiempos), 4),
        "max":    round(max(tiempos), 4),
        "media":  round(statistics.mean(tiempos), 4),
        "mediana": round(statistics.median(tiempos), 4),
        "stdev":  round(statistics.stdev(tiempos), 4) if len(tiempos) > 1 else 0,
    }


def tabla(titulo: str, filas: list[tuple]):
    ancho = 70
    print(f"  {titulo}")
    print(f"  {'Operación':<35} {'Media(µs)':>10} {'Mediana(µs)':>12} {'StDev':>8}")
    for nombre, stats in filas:
        print(f"  {nombre:<35} {stats['media']:>10} {stats['mediana']:>12} {stats['stdev']:>8}")

def benchmark_operaciones_basicas():

    # O(1) creación y acceso directo
    iam = IAMSystem("Bench")

    for i in range(500):
        iam.crear_usuario(f"u_{i}")
        iam.crear_rol(f"r_{i}")
        iam.crear_recurso(f"res_{i}")

    filas = []

    # O(1)
    contador = [500]
    def crear_u():
        iam.crear_usuario(f"u_new_{contador[0]}")
        contador[0] += 1
    filas.append(("Crear usuario [O(1)]", medir(crear_u, 200)))

    # O(1)
    filas.append(("Obtener usuario [O(1)]", medir(lambda: iam.obtener_usuario("u_250"), 2000)))

    # O(1)
    cont_r = [500]
    def crear_r():
        iam.crear_rol(f"r_new_{cont_r[0]}")
        cont_r[0] += 1
    filas.append(("Crear rol [O(1)]", medir(crear_r, 200)))

    # O(1)
    rol = iam.obtener_rol("r_0")
    cont_p = [0]
    def agregar_p():
        rol.agregar_permiso(f"perm_{cont_p[0]}")
        cont_p[0] += 1
    filas.append(("Agregar permiso a rol [O(1)]", medir(agregar_p, 500)))

    # O(1)
    rol2 = iam.obtener_rol("r_1")
    rol2.agregar_permiso("test_perm")
    filas.append(("Permiso directo [O(1)]", medir(lambda: rol2.tiene_permiso_directo("test_perm"), 5000)))

    tabla("BENCHMARK 1 — Operaciones bàsicas O(1)", filas)
    
if __name__ == "__main__":
    print("  ANÁLISIS EMPÍRICO DE COMPLEJIDAD — Simulador IAM con RBAC")
    benchmark_operaciones_basicas()
