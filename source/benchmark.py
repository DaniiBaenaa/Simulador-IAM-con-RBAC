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

def benchmark_herencia_roles():

    #O(h·p)
    #Medimos cómo escala el tiempo con la profundidad de herencia h.

    print("  BENCHMARK 2 — O(h·p)")
    print(f"  {'Profundidad h':<20} {'Permisos p':<15} {'Media(µs)':>10} {'Mediana(µs)':>12}")

    permisos_por_rol = 5

    for h in [1, 2, 5, 10, 20, 50]:
        iam = IAMSystem("HerenciaBench")
        roles_cadena = []
        padre = None
        for i in range(h):
            nombre_r = f"rol_h{h}_nivel{i}"
            r = iam.crear_rol(nombre_r, padre_nombre=padre)
            for j in range(permisos_por_rol):
                r.agregar_permiso(f"perm_h{h}_n{i}_p{j}")
            padre = nombre_r
            roles_cadena.append(nombre_r)

        # El permiso que buscamos está en el nivel raíz (peor caso)
        permiso_raiz = f"perm_h{h}_n0_p0"
        rol_hoja = iam.obtener_rol(roles_cadena[-1])

        stats = medir(lambda: rol_hoja.tiene_permiso(permiso_raiz), repeticiones=1000)
        print(f"  {h:<20} {permisos_por_rol:<15} {stats['media']:>10} {stats['mediana']:>12}")

    print(f"{'═'*70}")

def benchmark_verificar_acceso():

    #verificar_acceso() con distintos números de roles por usuario
    # O(r·h·p)

    print("  BENCHMARK 3 — verificar_acceso() escalado con roles por usuario O(r·h·p)")
    print(f"  {'Roles/usuario r':<20} {'Media(µs)':>10} {'Mediana(µs)':>12} {'StDev':>8}")

    for r_count in [1, 2, 5, 10, 20]:
        iam = IAMSystem("AccesoBench")

        # Creamos r_count roles simples
        for i in range(r_count):
            rol = iam.crearrol(f"rol{i}")
            for j in range(3):
                rol.agregarpermiso(f"perm{i}_{j}")

        u = iam.crear_usuario("tester")
        for i in range(r_count):
            iam.asignar_rol_ausuario("tester", f"rol{i}")

        # Recurso que requiere 1 permiso
        rec = iam.crear_recurso("recurso_test")
        iam.agregar_permiso_requerido_a_recurso("recursotest", f"perm{r_count-1}_0")

        stats = medir(lambda: iam.verificar_acceso("tester", "recurso_test"), repeticiones=500)
        print(f"  {r_count:<20} {stats['media']:>10} {stats['mediana']:>12} {stats['stdev']:>8}")

    print(f"{'═'*70}")

def benchmark_log_auditoria():

    #Log de auditoría — append O(1) amortizado, lectura O(n)
    iam = IAMSystem("LogBench")

    # Llenamos el log con eventos
    for i in range(10_000):
        iam._registrarevento("TEST", f"evento{i}")

    filas = []
    filas.append(("Registrar evento [O(1)]",
                  medir(lambda: iam._registrar_evento("TEST", "x"), 5000)))
    filas.append(("Obtener log completo [O(n=10k)]",
                  medir(lambda: iam.obtener_log(), 200)))
    filas.append(("Obtener log filtrado [O(n)]",
                  medir(lambda: iam.obtener_log("ACCESO_DENEGADO"), 200)))

    tabla("BENCHMARK 4 — Log de auditoría", filas)

if name == "main":
    print("  ANÁLISIS EMPÍRICO DE COMPLEJIDAD — Simulador IAM con RBAC")
    benchmark_operaciones_basicas()
    benchmark_herencia_roles()
    benchmark_verificar_acceso()
    benchmark_log_auditoria()

    print("  Benchmark completado.\n")

