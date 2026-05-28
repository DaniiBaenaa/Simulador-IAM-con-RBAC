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


if __name__ == "__main__":
    print("  ANÁLISIS EMPÍRICO DE COMPLEJIDAD — Simulador IAM con RBAC")
