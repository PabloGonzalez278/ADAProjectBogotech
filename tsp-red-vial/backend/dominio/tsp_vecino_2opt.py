"""
Implementación del algoritmo 2-Opt para el TSP.
Heurística de optimización local que mejora iterativamente una solución inicial.
Complejidad: O(n² × k) donde k es el número de iteraciones
"""

import numpy as np
from typing import List, Tuple
from datetime import datetime


def tsp_vecino_mas_cercano(matriz: np.ndarray, inicio: int = 0) -> List[int]:
    """
    Construye una solución inicial usando el algoritmo del vecino más cercano.
    En cada paso, visita la ciudad no visitada más cercana.

    Args:
        matriz: Matriz de distancias NxN
        inicio: Índice de la ciudad inicial

    Returns:
        Lista representando la ruta [inicio, ..., inicio]
    """
    n = len(matriz)
    visitados = {inicio}
    ruta = [inicio]
    actual = inicio

    for _ in range(n - 1):
        distancia_minima = float('inf')
        siguiente = None

        for ciudad in range(n):
            if ciudad not in visitados:
                distancia = matriz[actual][ciudad]
                if distancia < distancia_minima:
                    distancia_minima = distancia
                    siguiente = ciudad

        if siguiente is not None:
            ruta.append(siguiente)
            visitados.add(siguiente)
            actual = siguiente

    ruta.append(inicio)
    return ruta


def calcular_distancia_ruta(ruta: List[int], matriz: np.ndarray) -> float:
    """Calcula la distancia total de una ruta"""
    distancia = 0.0
    for i in range(len(ruta) - 1):
        distancia += matriz[ruta[i]][ruta[i + 1]]
    return distancia


def intercambiar_2opt(ruta: List[int], i: int, j: int) -> List[int]:
    """
    Realiza un intercambio 2-opt invirtiendo el segmento entre i y j.
    Esta operación elimina dos aristas y añade dos nuevas.

    Args:
        ruta: Ruta actual
        i: Índice inicial del segmento a invertir
        j: Índice final del segmento a invertir

    Returns:
        Nueva ruta con el segmento invertido
    """
    nueva_ruta = ruta[:i] + ruta[i:j+1][::-1] + ruta[j+1:]
    return nueva_ruta


def optimizar_2opt(
    ruta: List[int],
    matriz: np.ndarray,
    max_iteraciones: int = 1000,
    mostrar_progreso: bool = False
) -> Tuple[List[int], int]:
    """
    Optimiza una ruta usando el algoritmo 2-Opt.
    Busca intercambios que mejoren la distancia total.

    Args:
        ruta: Ruta inicial
        matriz: Matriz de distancias
        max_iteraciones: Número máximo de iteraciones sin mejora
        mostrar_progreso: Si True, muestra el progreso

    Returns:
        Tupla (ruta_mejorada, num_mejoras)
    """
    mejor_ruta = ruta.copy()
    mejor_distancia = calcular_distancia_ruta(mejor_ruta, matriz)

    mejoras_totales = 0
    iteraciones_sin_mejora = 0

    while iteraciones_sin_mejora < max_iteraciones:
        mejorado = False

        for i in range(1, len(mejor_ruta) - 2):
            for j in range(i + 1, len(mejor_ruta) - 1):
                nueva_ruta = intercambiar_2opt(mejor_ruta, i, j)
                nueva_distancia = calcular_distancia_ruta(nueva_ruta, matriz)

                if nueva_distancia < mejor_distancia:
                    mejor_ruta = nueva_ruta
                    mejor_distancia = nueva_distancia
                    mejoras_totales += 1
                    mejorado = True
                    iteraciones_sin_mejora = 0

                    if mostrar_progreso and mejoras_totales % 10 == 0:
                        print(f"  Mejora {mejoras_totales}: {mejor_distancia:.2f}m")

                    break
            if mejorado:
                break

        if not mejorado:
            iteraciones_sin_mejora += 1

    return mejor_ruta, mejoras_totales


def tsp_2opt(
    matriz_distancias: np.ndarray,
    solucion_inicial: List[int] = None,
    max_iteraciones: int = 1000,
    mostrar_progreso: bool = False
) -> Tuple[List[int], float, dict]:
    """
    Resuelve el TSP usando el algoritmo 2-Opt.
    Combina una solución inicial greedy con optimización local.

    Args:
        matriz_distancias: Matriz NxN de distancias
        solucion_inicial: Ruta inicial opcional
        max_iteraciones: Máximo de iteraciones sin mejora
        mostrar_progreso: Si True, muestra el progreso

    Returns:
        Tupla (ruta_optima, distancia, estadisticas)
    """
    n = len(matriz_distancias)

    if n < 2:
        raise ValueError("Se necesitan al menos 2 puntos")

    if mostrar_progreso:
        print(f"\nIniciando TSP 2-Opt")
        print(f"Puntos: {n}")

    inicio = datetime.now()

    if solucion_inicial is None:
        if mostrar_progreso:
            print("Generando solución inicial (vecino más cercano)...")
        ruta_inicial = tsp_vecino_mas_cercano(matriz_distancias)
    else:
        ruta_inicial = solucion_inicial

    distancia_inicial = calcular_distancia_ruta(ruta_inicial, matriz_distancias)

    if mostrar_progreso:
        print(f"Distancia inicial: {distancia_inicial:.2f}m")
        print(f"Optimizando con 2-Opt...")

    ruta_final, num_mejoras = optimizar_2opt(
        ruta_inicial,
        matriz_distancias,
        max_iteraciones,
        mostrar_progreso
    )

    distancia_final = calcular_distancia_ruta(ruta_final, matriz_distancias)

    tiempo_total = (datetime.now() - inicio).total_seconds()

    mejora_porcentual = ((distancia_inicial - distancia_final) / distancia_inicial) * 100

    estadisticas = {
        'num_puntos': n,
        'distancia_inicial': distancia_inicial,
        'distancia_final': distancia_final,
        'num_mejoras': num_mejoras,
        'mejora_porcentual': mejora_porcentual,
        'tiempo_segundos': tiempo_total
    }

    if mostrar_progreso:
        print(f"\n2-Opt completado:")
        print(f"  Tiempo: {tiempo_total:.3f} segundos")
        print(f"  Mejoras aplicadas: {num_mejoras}")
        print(f"  Distancia inicial: {distancia_inicial:.2f}m")
        print(f"  Distancia final: {distancia_final:.2f}m")
        print(f"  Mejora: {mejora_porcentual:.2f}%")
        print(f"  Ruta: {ruta_final}")

    return ruta_final, distancia_final, estadisticas

