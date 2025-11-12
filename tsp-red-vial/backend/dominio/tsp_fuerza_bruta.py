"""
Implementación del algoritmo de Fuerza Bruta para el TSP.
Explora todas las permutaciones posibles para encontrar la ruta óptima garantizada.
Complejidad: O(n!)
"""

import itertools
import numpy as np
from typing import List, Tuple
from datetime import datetime


def tsp_fuerza_bruta(
    matriz_distancias: np.ndarray,
    mostrar_progreso: bool = False
) -> Tuple[List[int], float, dict]:
    """
    Resuelve el TSP usando fuerza bruta.
    Prueba todas las permutaciones posibles y selecciona la de menor costo.

    Este método garantiza encontrar la solución óptima pero es extremadamente lento
    para más de 10-11 ciudades debido a su complejidad factorial.

    Args:
        matriz_distancias: Matriz NxN con distancias entre puntos
        mostrar_progreso: Si True, muestra el progreso del cálculo

    Returns:
        Tupla (ruta_optima, distancia_optima, estadisticas)
        donde ruta_optima es una lista de índices [0, ..., n-1, 0]

    Raises:
        ValueError: Si la matriz es inválida o demasiado grande
    """
    n = len(matriz_distancias)

    if n < 2:
        raise ValueError("Se necesitan al menos 2 puntos para TSP")

    if n > 11:
        raise ValueError(
            f"Fuerza bruta no es práctico para {n} puntos. "
            f"Tiempo estimado: años. Máximo recomendado: 11 puntos"
        )

    if mostrar_progreso:
        import math
        num_permutaciones = math.factorial(n - 1)
        print(f"\nIniciando TSP Fuerza Bruta")
        print(f"Puntos: {n}")
        print(f"Permutaciones a evaluar: {num_permutaciones:,}")

    inicio = datetime.now()

    ciudades = list(range(1, n))

    mejor_ruta = None
    mejor_distancia = float('inf')
    permutaciones_evaluadas = 0

    for permutacion in itertools.permutations(ciudades):
        ruta_actual = [0] + list(permutacion) + [0]

        distancia_actual = calcular_distancia_ruta(ruta_actual, matriz_distancias)

        if distancia_actual < mejor_distancia:
            mejor_distancia = distancia_actual
            mejor_ruta = ruta_actual

        permutaciones_evaluadas += 1

        if mostrar_progreso and permutaciones_evaluadas % 10000 == 0:
            progreso = (permutaciones_evaluadas / num_permutaciones) * 100
            print(f"  Progreso: {permutaciones_evaluadas:,}/{num_permutaciones:,} "
                  f"({progreso:.1f}%) - Mejor hasta ahora: {mejor_distancia:.2f}m")

    tiempo_total = (datetime.now() - inicio).total_seconds()

    estadisticas = {
        'num_puntos': n,
        'permutaciones_evaluadas': permutaciones_evaluadas,
        'tiempo_segundos': tiempo_total,
        'permutaciones_por_segundo': permutaciones_evaluadas / tiempo_total if tiempo_total > 0 else 0
    }

    if mostrar_progreso:
        print(f"\nFuerza Bruta completado:")
        print(f"  Tiempo: {tiempo_total:.3f} segundos")
        print(f"  Permutaciones/seg: {estadisticas['permutaciones_por_segundo']:,.0f}")
        print(f"  Distancia óptima: {mejor_distancia:.2f} metros")
        print(f"  Ruta óptima: {mejor_ruta}")

    return mejor_ruta, mejor_distancia, estadisticas


def calcular_distancia_ruta(ruta: List[int], matriz: np.ndarray) -> float:
    """
    Calcula la distancia total de una ruta dada.
    Suma las distancias entre puntos consecutivos en la ruta.

    Args:
        ruta: Lista de índices representando el orden de visita
        matriz: Matriz de distancias

    Returns:
        Distancia total de la ruta en metros
    """
    distancia_total = 0.0

    for i in range(len(ruta) - 1):
        ciudad_actual = ruta[i]
        ciudad_siguiente = ruta[i + 1]
        distancia_total += matriz[ciudad_actual][ciudad_siguiente]

    return distancia_total


def estimar_tiempo_ejecucion(num_puntos: int) -> dict:
    """
    Estima el tiempo de ejecución para un número dado de puntos.
    Basado en benchmarks típicos de ~1 millón de permutaciones/segundo.

    Args:
        num_puntos: Número de puntos del problema

    Returns:
        Diccionario con estimaciones de tiempo en diferentes unidades
    """
    import math

    if num_puntos < 2:
        return {'es_factible': False, 'razon': 'Mínimo 2 puntos requeridos'}

    num_permutaciones = math.factorial(num_puntos - 1)

    permutaciones_por_segundo = 1_000_000

    segundos = num_permutaciones / permutaciones_por_segundo

    if segundos < 1:
        return {
            'es_factible': True,
            'permutaciones': num_permutaciones,
            'tiempo_segundos': segundos,
            'tiempo_legible': f"{segundos*1000:.0f} milisegundos"
        }
    elif segundos < 60:
        return {
            'es_factible': True,
            'permutaciones': num_permutaciones,
            'tiempo_segundos': segundos,
            'tiempo_legible': f"{segundos:.1f} segundos"
        }
    elif segundos < 3600:
        return {
            'es_factible': num_puntos <= 11,
            'permutaciones': num_permutaciones,
            'tiempo_segundos': segundos,
            'tiempo_legible': f"{segundos/60:.1f} minutos"
        }
    elif segundos < 86400:
        return {
            'es_factible': False,
            'permutaciones': num_permutaciones,
            'tiempo_segundos': segundos,
            'tiempo_legible': f"{segundos/3600:.1f} horas"
        }
    elif segundos < 31536000:
        return {
            'es_factible': False,
            'permutaciones': num_permutaciones,
            'tiempo_segundos': segundos,
            'tiempo_legible': f"{segundos/86400:.1f} días"
        }
    else:
        return {
            'es_factible': False,
            'permutaciones': num_permutaciones,
            'tiempo_segundos': segundos,
            'tiempo_legible': f"{segundos/31536000:.1f} años"
        }


def verificar_solucion(
    ruta: List[int],
    matriz: np.ndarray
) -> Tuple[bool, List[str]]:
    """
    Verifica que una solución TSP sea válida.
    Comprueba que la ruta sea un ciclo hamiltoniano válido.

    Args:
        ruta: Ruta a verificar
        matriz: Matriz de distancias

    Returns:
        Tupla (es_valida, lista_errores)
    """
    errores = []
    n = len(matriz)

    if len(ruta) != n + 1:
        errores.append(f"Longitud incorrecta: esperado {n+1}, obtenido {len(ruta)}")

    if ruta[0] != 0:
        errores.append(f"La ruta debe empezar en 0, empieza en {ruta[0]}")

    if ruta[-1] != 0:
        errores.append(f"La ruta debe terminar en 0, termina en {ruta[-1]}")

    ciudades_visitadas = set(ruta[:-1])
    if len(ciudades_visitadas) != n:
        errores.append(f"No se visitaron todas las ciudades: {len(ciudades_visitadas)}/{n}")

    if ciudades_visitadas != set(range(n)):
        faltantes = set(range(n)) - ciudades_visitadas
        errores.append(f"Ciudades faltantes: {faltantes}")

    for i in range(len(ruta) - 1):
        if ruta[i] < 0 or ruta[i] >= n:
            errores.append(f"Índice fuera de rango en posición {i}: {ruta[i]}")

    return len(errores) == 0, errores

