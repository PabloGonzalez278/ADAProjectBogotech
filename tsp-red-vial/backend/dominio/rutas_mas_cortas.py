"""
Módulo para cálculo de rutas más cortas sobre redes viales.
Utiliza NetworkX para encontrar caminos óptimos entre puntos y construir matrices de distancias.
"""

import networkx as nx
from typing import List, Tuple, Dict, Optional
import numpy as np
from datetime import datetime


def calcular_camino_mas_corto(
    grafo: nx.Graph,
    nodo_origen: str,
    nodo_destino: str,
    peso: str = 'weight'
) -> Tuple[List[str], float]:
    """
    Calcula el camino más corto entre dos nodos usando el algoritmo de Dijkstra.
    Retorna la secuencia de nodos y la distancia total del camino.

    Args:
        grafo: Grafo de NetworkX representando la red vial
        nodo_origen: ID del nodo de inicio
        nodo_destino: ID del nodo de destino
        peso: Nombre del atributo de arista que contiene el peso

    Returns:
        Tupla (camino, distancia) donde camino es lista de IDs de nodos

    Raises:
        nx.NetworkXNoPath: Si no existe camino entre los nodos
        nx.NodeNotFound: Si alguno de los nodos no existe en el grafo
    """
    try:
        camino = nx.shortest_path(grafo, nodo_origen, nodo_destino, weight=peso)
        distancia = nx.shortest_path_length(grafo, nodo_origen, nodo_destino, weight=peso)
        return camino, distancia
    except nx.NetworkXNoPath:
        raise ValueError(f"No existe camino entre {nodo_origen} y {nodo_destino}")
    except nx.NodeNotFound as e:
        raise ValueError(f"Nodo no encontrado en el grafo: {e}")


def calcular_matriz_distancias(
    grafo: nx.Graph,
    puntos: List[Tuple[float, float]],
    nodos_coords: Dict[str, Tuple[float, float]],
    nodos_puntos: List[str],
    mostrar_progreso: bool = True
) -> np.ndarray:
    """
    Calcula la matriz de distancias NxN entre todos los pares de puntos.
    Usa el camino más corto sobre la red vial para cada par.

    Args:
        grafo: Grafo de NetworkX con la red vial
        puntos: Lista de coordenadas (lat, lon) de los puntos
        nodos_coords: Diccionario {nodo_id: (lat, lon)}
        nodos_puntos: Lista de IDs de nodos correspondientes a cada punto
        mostrar_progreso: Si True, imprime el progreso del cálculo

    Returns:
        Matriz numpy NxN con las distancias en metros

    Raises:
        ValueError: Si el número de puntos y nodos no coincide
    """
    n = len(puntos)

    if len(nodos_puntos) != n:
        raise ValueError(f"El número de puntos ({n}) no coincide con nodos ({len(nodos_puntos)})")

    if mostrar_progreso:
        print(f"\nCalculando matriz de distancias para {n} puntos...")
        print(f"Total de pares a calcular: {n * (n - 1) // 2}")

    matriz = np.zeros((n, n))

    inicio = datetime.now()
    pares_calculados = 0
    total_pares = n * (n - 1) // 2

    for i in range(n):
        for j in range(i + 1, n):
            try:
                _, distancia = calcular_camino_mas_corto(
                    grafo,
                    nodos_puntos[i],
                    nodos_puntos[j]
                )

                matriz[i][j] = distancia
                matriz[j][i] = distancia

                pares_calculados += 1

                if mostrar_progreso and pares_calculados % 10 == 0:
                    progreso = (pares_calculados / total_pares) * 100
                    print(f"  Progreso: {pares_calculados}/{total_pares} pares ({progreso:.1f}%)")

            except ValueError as e:
                raise ValueError(f"Error calculando distancia entre puntos {i} y {j}: {e}")

    tiempo_total = (datetime.now() - inicio).total_seconds()

    if mostrar_progreso:
        print(f"\nMatriz de distancias calculada en {tiempo_total:.2f} segundos")
        print(f"Distancia promedio: {np.mean(matriz[matriz > 0]):.2f} metros")
        print(f"Distancia máxima: {np.max(matriz):.2f} metros")
        print(f"Distancia mínima (no cero): {np.min(matriz[matriz > 0]):.2f} metros")

    return matriz


def verificar_matriz_simetrica(matriz: np.ndarray, tolerancia: float = 1e-6) -> bool:
    """
    Verifica que la matriz de distancias sea simétrica.
    Esto es esencial para el correcto funcionamiento de los algoritmos TSP.

    Args:
        matriz: Matriz a verificar
        tolerancia: Tolerancia para considerar dos valores como iguales

    Returns:
        True si la matriz es simétrica, False en caso contrario
    """
    if matriz.shape[0] != matriz.shape[1]:
        return False

    return np.allclose(matriz, matriz.T, atol=tolerancia)


def verificar_desigualdad_triangular(
    matriz: np.ndarray,
    tolerancia: float = 1.0
) -> Tuple[bool, List[Tuple[int, int, int]]]:
    """
    Verifica que la matriz satisfaga la desigualdad triangular.
    Esto es importante para garantizar propiedades de los algoritmos TSP.

    La desigualdad triangular establece que para cualesquiera i, j, k:
    matriz[i][k] <= matriz[i][j] + matriz[j][k]

    Args:
        matriz: Matriz de distancias
        tolerancia: Margen de error permitido en metros

    Returns:
        Tupla (es_valida, violaciones) donde violaciones es lista de (i, j, k)
        que violan la desigualdad
    """
    n = matriz.shape[0]
    violaciones = []

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            for k in range(n):
                if k == i or k == j:
                    continue

                distancia_directa = matriz[i][k]
                distancia_via_j = matriz[i][j] + matriz[j][k]

                if distancia_directa > distancia_via_j + tolerancia:
                    violaciones.append((i, j, k))

    return len(violaciones) == 0, violaciones


def optimizar_matriz_floyd_warshall(
    grafo: nx.Graph,
    nodos: List[str]
) -> np.ndarray:
    """
    Calcula la matriz de distancias usando Floyd-Warshall.
    Más eficiente que Dijkstra para grafos densos o cuando se necesitan
    todas las distancias entre todos los pares.

    Args:
        grafo: Grafo de NetworkX
        nodos: Lista de IDs de nodos para los cuales calcular distancias

    Returns:
        Matriz numpy con las distancias más cortas
    """
    print("\nCalculando matriz con algoritmo de Floyd-Warshall...")
    inicio = datetime.now()

    subgrafo = grafo.subgraph(nodos).copy()

    distancias_dict = dict(nx.all_pairs_dijkstra_path_length(subgrafo))

    n = len(nodos)
    matriz = np.zeros((n, n))

    nodo_a_indice = {nodo: i for i, nodo in enumerate(nodos)}

    for i, nodo_i in enumerate(nodos):
        for j, nodo_j in enumerate(nodos):
            if i == j:
                matriz[i][j] = 0.0
            elif nodo_j in distancias_dict.get(nodo_i, {}):
                matriz[i][j] = distancias_dict[nodo_i][nodo_j]
            else:
                matriz[i][j] = float('inf')

    tiempo_total = (datetime.now() - inicio).total_seconds()
    print(f"Matriz calculada en {tiempo_total:.2f} segundos")

    return matriz


def obtener_camino_detallado(
    grafo: nx.Graph,
    nodo_origen: str,
    nodo_destino: str,
    nodos_coords: Dict[str, Tuple[float, float]]
) -> Dict:
    """
    Obtiene información detallada del camino más corto entre dos nodos.
    Incluye la ruta, distancia, y coordenadas de cada nodo en el camino.

    Args:
        grafo: Grafo de NetworkX
        nodo_origen: Nodo de inicio
        nodo_destino: Nodo de destino
        nodos_coords: Diccionario con coordenadas de nodos

    Returns:
        Diccionario con información completa del camino
    """
    camino, distancia_total = calcular_camino_mas_corto(grafo, nodo_origen, nodo_destino)

    segmentos = []
    distancia_acumulada = 0.0

    for i in range(len(camino) - 1):
        nodo_actual = camino[i]
        nodo_siguiente = camino[i + 1]

        peso_arista = grafo[nodo_actual][nodo_siguiente].get('weight', 0.0)
        distancia_acumulada += peso_arista

        segmento = {
            'desde': nodo_actual,
            'hacia': nodo_siguiente,
            'coords_desde': nodos_coords.get(nodo_actual),
            'coords_hacia': nodos_coords.get(nodo_siguiente),
            'distancia_segmento': peso_arista,
            'distancia_acumulada': distancia_acumulada
        }
        segmentos.append(segmento)

    return {
        'camino': camino,
        'num_nodos': len(camino),
        'distancia_total': distancia_total,
        'segmentos': segmentos,
        'coords_inicio': nodos_coords.get(nodo_origen),
        'coords_fin': nodos_coords.get(nodo_destino)
    }

