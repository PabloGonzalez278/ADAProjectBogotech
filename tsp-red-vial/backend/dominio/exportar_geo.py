"""
Módulo para exportar resultados a formatos geográficos.
Convierte rutas TSP y redes viales a GeoJSON y WKT para visualización y análisis.
"""

import json
import networkx as nx
from typing import List, Dict, Tuple
from shapely.geometry import Point, LineString, mapping


def red_a_geojson(
    grafo: nx.Graph,
    nodos_coords: Dict[str, Tuple[float, float]]
) -> dict:
    """
    Convierte una red vial NetworkX a formato GeoJSON.
    Genera un FeatureCollection con las aristas como LineStrings.

    Args:
        grafo: Grafo de NetworkX
        nodos_coords: Diccionario {nodo_id: (lat, lon)}

    Returns:
        Diccionario GeoJSON con las aristas de la red
    """
    features = []

    for u, v, data in grafo.edges(data=True):
        if u not in nodos_coords or v not in nodos_coords:
            continue

        coord_u = nodos_coords[u]
        coord_v = nodos_coords[v]

        linea = LineString([
            (coord_u[1], coord_u[0]),
            (coord_v[1], coord_v[0])
        ])

        feature = {
            'type': 'Feature',
            'properties': {
                'nodo_inicio': u,
                'nodo_fin': v,
                'distancia': data.get('weight', 0.0),
                'tipo': 'arista_red'
            },
            'geometry': mapping(linea)
        }

        features.append(feature)

    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }

    return geojson


def ruta_a_geojson(
    ruta: List[int],
    puntos_coords: List[Tuple[float, float]],
    puntos_nombres: List[str],
    nombre_algoritmo: str,
    distancia_total: float,
    grafo: nx.Graph = None,
    nodos_puntos: List[str] = None,
    nodos_coords: Dict[str, Tuple[float, float]] = None
) -> dict:
    """
    Convierte una ruta TSP a formato GeoJSON.
    Puede generar tanto la línea directa como el camino detallado sobre la red.

    Args:
        ruta: Lista de índices de puntos en orden de visita
        puntos_coords: Coordenadas de los puntos
        puntos_nombres: Nombres de los puntos
        nombre_algoritmo: Nombre del algoritmo usado
        distancia_total: Distancia total de la ruta
        grafo: Opcional, grafo para camino detallado
        nodos_puntos: Opcional, nodos correspondientes a puntos
        nodos_coords: Opcional, coordenadas de todos los nodos

    Returns:
        Diccionario GeoJSON con la ruta
    """
    features = []

    for i in range(len(ruta) - 1):
        idx_actual = ruta[i]
        idx_siguiente = ruta[i + 1]

        if grafo is not None and nodos_puntos is not None and nodos_coords is not None:
            try:
                from .rutas_mas_cortas import obtener_camino_detallado

                camino_detallado = obtener_camino_detallado(
                    grafo,
                    nodos_puntos[idx_actual],
                    nodos_puntos[idx_siguiente],
                    nodos_coords
                )

                coords_linea = []
                for nodo in camino_detallado['camino']:
                    if nodo in nodos_coords:
                        coord = nodos_coords[nodo]
                        coords_linea.append((coord[1], coord[0]))

                linea = LineString(coords_linea)

            except:
                coord_actual = puntos_coords[idx_actual]
                coord_siguiente = puntos_coords[idx_siguiente]
                linea = LineString([
                    (coord_actual[1], coord_actual[0]),
                    (coord_siguiente[1], coord_siguiente[0])
                ])
        else:
            coord_actual = puntos_coords[idx_actual]
            coord_siguiente = puntos_coords[idx_siguiente]
            linea = LineString([
                (coord_actual[1], coord_actual[0]),
                (coord_siguiente[1], coord_siguiente[0])
            ])

        feature = {
            'type': 'Feature',
            'properties': {
                'desde': puntos_nombres[idx_actual] if idx_actual < len(puntos_nombres) else f"Punto {idx_actual}",
                'hacia': puntos_nombres[idx_siguiente] if idx_siguiente < len(puntos_nombres) else f"Punto {idx_siguiente}",
                'segmento': i + 1,
                'algoritmo': nombre_algoritmo,
                'tipo': 'ruta_tsp'
            },
            'geometry': mapping(linea)
        }

        features.append(feature)

    for i, idx in enumerate(ruta[:-1]):
        coord = puntos_coords[idx]
        punto = Point(coord[1], coord[0])

        feature = {
            'type': 'Feature',
            'properties': {
                'nombre': puntos_nombres[idx] if idx < len(puntos_nombres) else f"Punto {idx}",
                'orden_visita': i + 1,
                'algoritmo': nombre_algoritmo,
                'tipo': 'punto_tsp'
            },
            'geometry': mapping(punto)
        }

        features.append(feature)

    geojson = {
        'type': 'FeatureCollection',
        'properties': {
            'algoritmo': nombre_algoritmo,
            'distancia_total': distancia_total,
            'num_puntos': len(ruta) - 1
        },
        'features': features
    }

    return geojson


def guardar_geojson(geojson: dict, ruta_archivo: str) -> None:
    """
    Guarda un diccionario GeoJSON en un archivo.

    Args:
        geojson: Diccionario GeoJSON
        ruta_archivo: Ruta donde guardar el archivo
    """
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)


def red_a_wkt(
    grafo: nx.Graph,
    nodos_coords: Dict[str, Tuple[float, float]]
) -> str:
    """
    Convierte una red vial a formato WKT.
    Genera un MULTILINESTRING con todas las aristas.

    Args:
        grafo: Grafo de NetworkX
        nodos_coords: Diccionario de coordenadas

    Returns:
        String en formato WKT
    """
    lineas = []

    for u, v in grafo.edges():
        if u in nodos_coords and v in nodos_coords:
            coord_u = nodos_coords[u]
            coord_v = nodos_coords[v]

            linea_wkt = f"({coord_u[1]} {coord_u[0]}, {coord_v[1]} {coord_v[0]})"
            lineas.append(linea_wkt)

    wkt = f"MULTILINESTRING({', '.join(lineas)})"
    return wkt


def ruta_a_wkt(
    ruta: List[int],
    puntos_coords: List[Tuple[float, float]]
) -> str:
    """
    Convierte una ruta TSP a formato WKT.
    Genera un LINESTRING con la secuencia de puntos.

    Args:
        ruta: Lista de índices de puntos
        puntos_coords: Coordenadas de los puntos

    Returns:
        String en formato WKT
    """
    coords_wkt = []

    for idx in ruta:
        coord = puntos_coords[idx]
        coords_wkt.append(f"{coord[1]} {coord[0]}")

    wkt = f"LINESTRING({', '.join(coords_wkt)})"
    return wkt


def exportar_comparacion_algoritmos(
    resultados: dict,
    puntos_coords: List[Tuple[float, float]],
    puntos_nombres: List[str],
    ruta_archivo: str
) -> None:
    """
    Exporta la comparación de múltiples algoritmos a un único archivo GeoJSON.
    Asigna colores diferentes a cada algoritmo para visualización.

    Args:
        resultados: Dict {nombre_algoritmo: (ruta, distancia, stats)}
        puntos_coords: Coordenadas de los puntos
        puntos_nombres: Nombres de los puntos
        ruta_archivo: Ruta del archivo de salida
    """
    todas_features = []

    colores = {
        'fuerza_bruta': '#FF0000',
        'held_karp': '#00FF00',
        '2opt': '#FFA500',
        'vecino_2opt': '#FFA500'
    }

    for nombre_alg, (ruta, distancia, _) in resultados.items():
        geojson_ruta = ruta_a_geojson(
            ruta,
            puntos_coords,
            puntos_nombres,
            nombre_alg,
            distancia
        )

        color = colores.get(nombre_alg, '#0000FF')

        for feature in geojson_ruta['features']:
            feature['properties']['color'] = color
            feature['properties']['stroke'] = color
            feature['properties']['stroke-width'] = 3
            todas_features.append(feature)

    geojson_final = {
        'type': 'FeatureCollection',
        'features': todas_features
    }

    guardar_geojson(geojson_final, ruta_archivo)

