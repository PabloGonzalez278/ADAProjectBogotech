"""
Implementación del algoritmo de Held-Karp para el TSP.
Usa programación dinámica con memoización para encontrar la solución óptima.
Complejidad: O(n² × 2^n) tiempo, O(n × 2^n) espacio
"""

import numpy as np
from typing import List, Tuple, Dict
from datetime import datetime


def tsp_held_karp(
    matriz_distancias: np.ndarray,
    mostrar_progreso: bool = False
) -> Tuple[List[int], float, dict]:
    """
    Resuelve el TSP usando el algoritmo de Held-Karp.
    Usa programación dinámica para encontrar la solución óptima de forma más eficiente
    que fuerza bruta, aunque sigue siendo exponencial.

    Args:
        matriz_distancias: Matriz NxN de distancias
        mostrar_progreso: Si True, muestra el progreso

    Returns:
        Tupla (ruta_optima, distancia_optima, estadisticas)

    Raises:
        ValueError: Si la matriz es inválida o el problema es demasiado grande
    """
    n = len(matriz_distancias)

    if n < 2:
        raise ValueError("Se necesitan al menos 2 puntos")

    if n > 22:
        raise ValueError(
            f"Held-Karp no es práctico para {n} puntos. "
            f"Uso de memoria estimado: >10 GB. Máximo recomendado: 20 puntos"
        )

    if mostrar_progreso:
        print(f"\nIniciando TSP Held-Karp")
        print(f"Puntos: {n}")
        print(f"Subproblemas estimados: {n * (2 ** (n-1)):,}")

    inicio = datetime.now()

    memo = {}

    for k in range(1, n):
        memo[(1 << k, k)] = (matriz_distancias[0][k], [0, k])

    subproblemas_resueltos = n - 1

    for subset_size in range(2, n):
        if mostrar_progreso:
            print(f"  Procesando subconjuntos de tamaño {subset_size}...")

        for subset in generar_subconjuntos(n, subset_size):
            # Obtener los índices de los bits activos en subset
            bits_activos = [i for i in range(n) if (subset >> i) & 1]

            for k in bits_activos:
                prev_subset = subset & ~(1 << k)

                mejor_dist = float('inf')
                mejor_prev = None

                # Obtener bits activos de prev_subset
                prev_bits = [i for i in range(n) if (prev_subset >> i) & 1]

                for m in prev_bits:
                    if (prev_subset, m) in memo:
                        dist_prev, _ = memo[(prev_subset, m)]
                        dist_total = dist_prev + matriz_distancias[m][k]

                        if dist_total < mejor_dist:
                            mejor_dist = dist_total
                            mejor_prev = m

                if mejor_prev is not None:
                    prev_camino = memo[(prev_subset, mejor_prev)][1]
                    memo[(subset, k)] = (mejor_dist, prev_camino + [k])
                    subproblemas_resueltos += 1

    todos = (1 << n) - 2
    mejor_dist_final = float('inf')
    mejor_k_final = None

    for k in range(1, n):
        if (todos, k) in memo:
            dist, _ = memo[(todos, k)]
            dist_total = dist + matriz_distancias[k][0]

            if dist_total < mejor_dist_final:
                mejor_dist_final = dist_total
                mejor_k_final = k

    if mejor_k_final is None:
        raise ValueError("No se pudo encontrar una solución válida")

    ruta_optima = memo[(todos, mejor_k_final)][1] + [0]

    tiempo_total = (datetime.now() - inicio).total_seconds()

    estadisticas = {
        'num_puntos': n,
        'subproblemas_resueltos': subproblemas_resueltos,
        'memoria_usada_mb': len(memo) * 100 / (1024 * 1024),
        'tiempo_segundos': tiempo_total,
        'subproblemas_por_segundo': subproblemas_resueltos / tiempo_total if tiempo_total > 0 else 0
    }

    if mostrar_progreso:
        print(f"\nHeld-Karp completado:")
        print(f"  Tiempo: {tiempo_total:.3f} segundos")
        print(f"  Subproblemas resueltos: {subproblemas_resueltos:,}")
        print(f"  Subproblemas/seg: {estadisticas['subproblemas_por_segundo']:,.0f}")
        print(f"  Distancia óptima: {mejor_dist_final:.2f} metros")
        print(f"  Ruta óptima: {ruta_optima}")

    return ruta_optima, mejor_dist_final, estadisticas


def generar_subconjuntos(n: int, size: int):
    """
    Genera todos los subconjuntos de tamaño dado usando representación de bits.
    Los subconjuntos representan conjuntos de ciudades visitadas.

    Args:
        n: Número total de elementos
        size: Tamaño de los subconjuntos

    Yields:
        Enteros que representan subconjuntos en formato bitmask
    """
    subset = (1 << size) - 1
    limit = 1 << n

    while subset < limit:
        if bin(subset).count('1') == size and not (subset & 1):
            yield subset

        c = subset & -subset
        r = subset + c
        subset = (((r ^ subset) >> 2) // c) | r


def estimar_recursos_held_karp(num_puntos: int) -> dict:
    """
    Estima recursos necesarios para ejecutar Held-Karp.
    Calcula tiempo estimado y memoria requerida.

    Args:
        num_puntos: Número de puntos del problema

    Returns:
        Diccionario con estimaciones de recursos
    """
    if num_puntos < 2:
        return {'es_factible': False, 'razon': 'Mínimo 2 puntos requeridos'}

    num_subproblemas = num_puntos * (2 ** (num_puntos - 1))

    bytes_por_subproblema = 100
    memoria_mb = (num_subproblemas * bytes_por_subproblema) / (1024 * 1024)

    subproblemas_por_segundo = 100_000
    tiempo_segundos = num_subproblemas / subproblemas_por_segundo

    if memoria_mb > 10000:
        return {
            'es_factible': False,
            'razon': f'Requiere {memoria_mb/1024:.1f} GB de memoria',
            'subproblemas': num_subproblemas,
            'memoria_mb': memoria_mb
        }

    if tiempo_segundos < 1:
        tiempo_legible = f"{tiempo_segundos*1000:.0f} milisegundos"
    elif tiempo_segundos < 60:
        tiempo_legible = f"{tiempo_segundos:.1f} segundos"
    elif tiempo_segundos < 3600:
        tiempo_legible = f"{tiempo_segundos/60:.1f} minutos"
    else:
        tiempo_legible = f"{tiempo_segundos/3600:.1f} horas"

    return {
        'es_factible': num_puntos <= 20,
        'subproblemas': num_subproblemas,
        'memoria_mb': memoria_mb,
        'tiempo_segundos': tiempo_segundos,
        'tiempo_legible': tiempo_legible
    }


def extraer_bit(numero: int, posicion: int) -> bool:
    """Extrae el bit en la posición dada de un número"""
    return (numero >> posicion) & 1 == 1


def activar_bit(numero: int, posicion: int) -> int:
    """Activa el bit en la posición dada"""
    return numero | (1 << posicion)


def desactivar_bit(numero: int, posicion: int) -> int:
    """Desactiva el bit en la posición dada"""
    return numero & ~(1 << posicion)

