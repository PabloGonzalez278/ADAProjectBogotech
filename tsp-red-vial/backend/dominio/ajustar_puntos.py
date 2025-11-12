"""
Módulo para integrar puntos de interés en la red vial.
Proyecta puntos sobre las aristas más cercanas y divide la red según sea necesario.
"""

import networkx as nx
from shapely.geometry import Point, LineString
from typing import Tuple, List, Dict
from .indice_espacial import encontrar_arista_mas_cercana


def proyectar_punto_en_arista(
    punto: Tuple[float, float],
    coord_u: Tuple[float, float],
    coord_v: Tuple[float, float]
) -> Tuple[Point, float]:
    """
    Proyecta un punto sobre una arista y calcula la posición relativa.
    Encuentra el punto más cercano en la línea que conecta dos nodos.

    Args:
        punto: Coordenadas (lat, lon) del punto a proyectar
        coord_u: Coordenadas del primer nodo de la arista
        coord_v: Coordenadas del segundo nodo de la arista

    Returns:
        Tupla (punto_proyectado, ratio) donde ratio está en [0, 1]
        y representa la posición en la arista
    """
    punto_shapely = Point(punto[1], punto[0])

    linea = LineString([
        (coord_u[1], coord_u[0]),
        (coord_v[1], coord_v[0])
    ])

    distancia_en_linea = linea.project(punto_shapely)

    punto_proyectado = linea.interpolate(distancia_en_linea)

    longitud_total = linea.length
    ratio = distancia_en_linea / longitud_total if longitud_total > 0 else 0.0

    return punto_proyectado, ratio


def calcular_distancia_desde_inicio_arista(
    coord_u: Tuple[float, float],
    coord_v: Tuple[float, float],
    punto_proyectado: Point
) -> Tuple[float, float]:
    """
    Calcula las distancias del punto proyectado a ambos extremos de la arista.
    Usa la fórmula de Haversine para distancias reales.

    Args:
        coord_u: Coordenadas del primer nodo
        coord_v: Coordenadas del segundo nodo
        punto_proyectado: Punto proyectado en la línea

    Returns:
        Tupla (distancia_u_a_punto, distancia_punto_a_v) en metros
    """
    from math import radians, sin, cos, sqrt, atan2

    def haversine(lat1, lon1, lat2, lon2):
        """Calcula distancia entre dos coordenadas usando Haversine"""
        R = 6371000

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return R * c

    lat_punto = punto_proyectado.y
    lon_punto = punto_proyectado.x

    distancia_u_a_punto = haversine(coord_u[0], coord_u[1], lat_punto, lon_punto)
    distancia_punto_a_v = haversine(lat_punto, lon_punto, coord_v[0], coord_v[1])

    return distancia_u_a_punto, distancia_punto_a_v


def dividir_arista(
    grafo: nx.Graph,
    nodo_u: str,
    nodo_v: str,
    nuevo_nodo_id: str,
    coord_nuevo_nodo: Tuple[float, float],
    dist_u_a_nuevo: float,
    dist_nuevo_a_v: float
) -> None:
    """
    Divide una arista existente insertando un nuevo nodo.
    Elimina la arista original y crea dos nuevas aristas con pesos ajustados.

    Args:
        grafo: Grafo de NetworkX a modificar
        nodo_u: ID del primer nodo de la arista original
        nodo_v: ID del segundo nodo de la arista original
        nuevo_nodo_id: ID para el nuevo nodo
        coord_nuevo_nodo: Coordenadas (lat, lon) del nuevo nodo
        dist_u_a_nuevo: Distancia de u al nuevo nodo en metros
        dist_nuevo_a_v: Distancia del nuevo nodo a v en metros
    """
    if not grafo.has_edge(nodo_u, nodo_v):
        raise ValueError(f"La arista ({nodo_u}, {nodo_v}) no existe en el grafo")

    atributos_originales = grafo[nodo_u][nodo_v].copy()

    grafo.remove_edge(nodo_u, nodo_v)

    grafo.add_node(
        nuevo_nodo_id,
        lat=coord_nuevo_nodo[0],
        lon=coord_nuevo_nodo[1]
    )

    grafo.add_edge(
        nodo_u,
        nuevo_nodo_id,
        weight=dist_u_a_nuevo,
        length=dist_u_a_nuevo,
        **{k: v for k, v in atributos_originales.items() if k not in ['weight', 'length']}
    )

    grafo.add_edge(
        nuevo_nodo_id,
        nodo_v,
        weight=dist_nuevo_a_v,
        length=dist_nuevo_a_v,
        **{k: v for k, v in atributos_originales.items() if k not in ['weight', 'length']}
    )


def integrar_punto_en_red(
    grafo: nx.Graph,
    nodos_coords: Dict[str, Tuple[float, float]],
    punto: Tuple[float, float],
    punto_id: int,
    nombre_punto: str = "",
    umbral_distancia: float = 100.0
) -> Tuple[str, float]:
    """
    Integra un punto de interés en la red vial.
    Encuentra la arista más cercana, proyecta el punto sobre ella, y divide la arista.

    Args:
        grafo: Grafo de NetworkX representando la red
        nodos_coords: Diccionario {nodo_id: (lat, lon)}
        punto: Coordenadas (lat, lon) del punto a integrar
        punto_id: ID único para el punto
        nombre_punto: Nombre descriptivo del punto
        umbral_distancia: Distancia máxima en metros para considerar una arista

    Returns:
        Tupla (id_nodo_creado, distancia_a_arista) en metros

    Raises:
        ValueError: Si no se encuentra una arista cercana o si hay errores en la integración
    """
    nodo_u, nodo_v, distancia_a_arista, punto_proyectado = encontrar_arista_mas_cercana(
        punto,
        grafo,
        nodos_coords
    )

    if distancia_a_arista > umbral_distancia:
        raise ValueError(
            f"Punto demasiado lejos de la red. "
            f"Distancia: {distancia_a_arista:.2f}m, Umbral: {umbral_distancia}m"
        )

    coord_nuevo_nodo = (punto_proyectado.y, punto_proyectado.x)

    nuevo_nodo_id = f"punto_{punto_id}"

    if nuevo_nodo_id in grafo.nodes():
        contador = 1
        while f"{nuevo_nodo_id}_{contador}" in grafo.nodes():
            contador += 1
        nuevo_nodo_id = f"{nuevo_nodo_id}_{contador}"

    coord_u = nodos_coords[nodo_u]
    coord_v = nodos_coords[nodo_v]

    dist_u_a_nuevo, dist_nuevo_a_v = calcular_distancia_desde_inicio_arista(
        coord_u,
        coord_v,
        punto_proyectado
    )

    dividir_arista(
        grafo,
        nodo_u,
        nodo_v,
        nuevo_nodo_id,
        coord_nuevo_nodo,
        dist_u_a_nuevo,
        dist_nuevo_a_v
    )

    nodos_coords[nuevo_nodo_id] = coord_nuevo_nodo

    return nuevo_nodo_id, distancia_a_arista


def integrar_multiples_puntos(
    grafo: nx.Graph,
    nodos_coords: Dict[str, Tuple[float, float]],
    puntos: List[Tuple[int, float, float, str]],
    umbral_distancia: float = 100.0,
    mostrar_progreso: bool = True
) -> Dict[int, Tuple[str, float]]:
    """
    Integra múltiples puntos de interés en la red vial.
    Procesa los puntos secuencialmente, actualizando la red después de cada integración.

    Args:
        grafo: Grafo de NetworkX
        nodos_coords: Diccionario de coordenadas
        puntos: Lista de tuplas (id, lat, lon, nombre)
        umbral_distancia: Distancia máxima permitida en metros
        mostrar_progreso: Si True, imprime el progreso

    Returns:
        Diccionario {punto_id: (nodo_id_creado, distancia_proyeccion)}

    Raises:
        ValueError: Si algún punto no puede ser integrado
    """
    if mostrar_progreso:
        print(f"\nIntegrando {len(puntos)} puntos en la red vial...")
        print(f"Umbral de distancia: {umbral_distancia} metros")

    resultados = {}
    puntos_exitosos = 0
    puntos_fallidos = 0

    for idx, (punto_id, lat, lon, nombre) in enumerate(puntos, 1):
        try:
            nodo_creado, distancia = integrar_punto_en_red(
                grafo,
                nodos_coords,
                (lat, lon),
                punto_id,
                nombre,
                umbral_distancia
            )

            resultados[punto_id] = (nodo_creado, distancia)
            puntos_exitosos += 1

            if mostrar_progreso:
                print(f"  [{idx}/{len(puntos)}] Punto '{nombre}' integrado como '{nodo_creado}' "
                      f"(distancia: {distancia:.2f}m)")

        except ValueError as e:
            puntos_fallidos += 1
            if mostrar_progreso:
                print(f"  [{idx}/{len(puntos)}] ERROR: Punto '{nombre}' falló: {e}")

            raise ValueError(f"Error integrando punto {nombre}: {e}")

    if mostrar_progreso:
        print(f"\nResultado:")
        print(f"  Exitosos: {puntos_exitosos}/{len(puntos)}")
        print(f"  Fallidos: {puntos_fallidos}/{len(puntos)}")
        print(f"  Nodos totales en red: {grafo.number_of_nodes()}")
        print(f"  Aristas totales en red: {grafo.number_of_edges()}")

    return resultados


def validar_integracion(
    grafo: nx.Graph,
    nodos_coords: Dict[str, Tuple[float, float]],
    nodos_puntos: List[str]
) -> Tuple[bool, List[str]]:
    """
    Valida que los puntos integrados estén correctamente conectados en la red.
    Verifica que todos los nodos existan y sean alcanzables.

    Args:
        grafo: Grafo de NetworkX
        nodos_coords: Diccionario de coordenadas
        nodos_puntos: Lista de IDs de nodos que representan puntos

    Returns:
        Tupla (es_valido, lista_de_errores)
    """
    errores = []

    for nodo in nodos_puntos:
        if nodo not in grafo.nodes():
            errores.append(f"Nodo {nodo} no existe en el grafo")
            continue

        if nodo not in nodos_coords:
            errores.append(f"Nodo {nodo} no tiene coordenadas registradas")
            continue

        if grafo.degree(nodo) == 0:
            errores.append(f"Nodo {nodo} está aislado (grado 0)")

    if not errores:
        for i, nodo_i in enumerate(nodos_puntos):
            for j, nodo_j in enumerate(nodos_puntos[i+1:], start=i+1):
                try:
                    if not nx.has_path(grafo, nodo_i, nodo_j):
                        errores.append(
                            f"No existe camino entre {nodo_i} y {nodo_j}"
                        )
                except nx.NetworkXError as e:
                    errores.append(f"Error verificando conectividad: {e}")

    es_valido = len(errores) == 0

    return es_valido, errores

