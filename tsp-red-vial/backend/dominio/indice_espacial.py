"""
Módulo de índice espacial para búsqueda eficiente de aristas cercanas.
Implementación simplificada sin requerir rtree (compatible con Windows).
"""
from typing import Tuple, List, Optional
import networkx as nx
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points


def distancia_punto_a_linea(punto: Point, linea: LineString) -> float:
    """
    Calcula la distancia perpendicular de un punto a una línea.

    Args:
        punto: Punto de Shapely
        linea: LineString de Shapely

    Returns:
        Distancia en las mismas unidades que las coordenadas
    """
    return punto.distance(linea)


def encontrar_arista_mas_cercana(
    punto: Tuple[float, float],
    grafo: nx.Graph,
    nodos_coords: dict
) -> Tuple[Tuple, Tuple, float, Point]:
    """
    Encuentra la arista más cercana a un punto dado.
    Implementación sin rtree usando búsqueda lineal (adecuado para grafos pequeños/medianos).

    Args:
        punto: Tupla (latitud, longitud)
        grafo: Grafo de NetworkX
        nodos_coords: Diccionario {nodo_id: (lat, lon)}

    Returns:
        Tupla (nodo_u, nodo_v, distancia, punto_proyectado)
    """
    punto_shapely = Point(punto[1], punto[0])  # Shapely usa (lon, lat)

    mejor_arista = None
    mejor_distancia = float('inf')
    mejor_proyeccion = None

    # Buscar en todas las aristas (fuerza bruta)
    for u, v in grafo.edges():
        # Obtener coordenadas de los nodos
        coord_u = nodos_coords[u]
        coord_v = nodos_coords[v]

        # Crear LineString (Shapely usa lon, lat)
        linea = LineString([
            (coord_u[1], coord_u[0]),  # (lon, lat)
            (coord_v[1], coord_v[0])
        ])

        # Calcular distancia
        distancia = distancia_punto_a_linea(punto_shapely, linea)

        # Si es la mejor hasta ahora, guardar
        if distancia < mejor_distancia:
            mejor_distancia = distancia
            mejor_arista = (u, v)

            # Calcular punto de proyección
            punto_proyectado = linea.interpolate(linea.project(punto_shapely))
            mejor_proyeccion = punto_proyectado

    return mejor_arista[0], mejor_arista[1], mejor_distancia, mejor_proyeccion


def crear_indice_espacial_simple(grafo: nx.Graph, nodos_coords: dict) -> dict:
    """
    Crea un índice espacial simple (estructura de datos auxiliar).
    Para grafos grandes, esto podría optimizarse con una grilla espacial.

    Args:
        grafo: Grafo de NetworkX
        nodos_coords: Diccionario {nodo_id: (lat, lon)}

    Returns:
        Diccionario con información del índice (bbox, stats, etc.)
    """
    if not nodos_coords:
        return {'bbox': None, 'num_aristas': 0}

    # Calcular bounding box
    lats = [coord[0] for coord in nodos_coords.values()]
    lons = [coord[1] for coord in nodos_coords.values()]

    bbox = {
        'min_lat': min(lats),
        'max_lat': max(lats),
        'min_lon': min(lons),
        'max_lon': max(lons)
    }

    return {
        'bbox': bbox,
        'num_nodos': len(nodos_coords),
        'num_aristas': grafo.number_of_edges()
    }


# Implementación alternativa con rtree (opcional, si se instala)
def encontrar_arista_mas_cercana_rtree(
    punto: Tuple[float, float],
    grafo: nx.Graph,
    nodos_coords: dict,
    rtree_index
) -> Tuple[Tuple, Tuple, float, Point]:
    """
    Versión con rtree para grafos muy grandes (requiere librería rtree instalada).
    Esta función es opcional y solo se usaría si rtree está disponible.
    """
    try:
        from rtree import index
        # Implementación con rtree...
        # (Por ahora usamos la versión simple)
        return encontrar_arista_mas_cercana(punto, grafo, nodos_coords)
    except ImportError:
        # Si rtree no está disponible, usar la versión simple
        return encontrar_arista_mas_cercana(punto, grafo, nodos_coords)
