"""
Cargador optimizado de redes viales desde GeoJSON.
Soporta redes grandes (Bogotá completa) con sistema de cache inteligente.
"""

import networkx as nx
import pickle
import json
from pathlib import Path
from typing import Dict, Tuple, Optional, List
import hashlib
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2


class CargadorRedOptimizado:
    """
    Cargador de redes viales con optimizaciones para grafos grandes.

    Características:
    - Cache con pickle (primera carga lenta, resto instantáneo)
    - Filtrado por área de interés (bbox o puntos)
    - Detección automática de cambios en archivo
    - Cálculo de distancias reales (Haversine)
    """

    def __init__(self, ruta_cache: str = "cache/"):
        self.ruta_cache = Path(ruta_cache)
        self.ruta_cache.mkdir(exist_ok=True)
        self.grafo = None
        self.nodos_coords = None

    def _hash_archivo(self, ruta: str) -> str:
        """Genera hash MD5 del archivo para detectar cambios"""
        with open(ruta, 'rb') as f:
            contenido = f.read()
            return hashlib.md5(contenido).hexdigest()

    def cargar_con_cache(
        self,
        ruta_geojson: str,
        forzar_recarga: bool = False
    ) -> Tuple[nx.Graph, Dict]:
        """
        Carga red con sistema de cache inteligente.

        Primera vez: Lee GeoJSON y guarda en cache (~10-15 seg para Bogotá)
        Siguientes: Carga desde cache (~1-2 seg)

        Args:
            ruta_geojson: Ruta al archivo GeoJSON
            forzar_recarga: Si True, ignora cache y recarga

        Returns:
            Tupla (grafo, diccionario_nodos_coordenadas)
        """
        print(f"\n{'='*60}")
        print(f"🗺️  CARGANDO RED VIAL")
        print(f"{'='*60}")
        print(f"📂 Archivo: {ruta_geojson}")

        # Verificar que archivo existe
        if not Path(ruta_geojson).exists():
            raise FileNotFoundError(f"Archivo no encontrado: {ruta_geojson}")

        # Calcular hash del archivo
        print(f"🔍 Calculando hash del archivo...")
        hash_actual = self._hash_archivo(ruta_geojson)
        nombre_cache = f"red_{hash_actual}.pkl"
        ruta_cache_red = self.ruta_cache / nombre_cache

        # Si existe cache y no se fuerza recarga
        if ruta_cache_red.exists() and not forzar_recarga:
            print(f"✅ Cache encontrado!")
            print(f"⚡ Cargando desde cache...")
            inicio = datetime.now()

            try:
                with open(ruta_cache_red, 'rb') as f:
                    datos_cache = pickle.load(f)

                tiempo = (datetime.now() - inicio).total_seconds()

                print(f"✅ Red cargada desde cache en {tiempo:.2f} segundos")
                print(f"📊 Nodos: {datos_cache['grafo'].number_of_nodes():,}")
                print(f"📊 Aristas: {datos_cache['grafo'].number_of_edges():,}")
                print(f"📅 Fecha cache: {datos_cache.get('timestamp', 'Desconocida')}")

                self.grafo = datos_cache['grafo']
                self.nodos_coords = datos_cache['nodos_coords']

                return self.grafo, self.nodos_coords

            except Exception as e:
                print(f"⚠️  Error al cargar cache: {e}")
                print(f"🔄 Recargando desde GeoJSON...")

        # Si no hay cache, cargar desde GeoJSON
        if ruta_cache_red.exists():
            print(f"🔄 Cache existente pero forzando recarga...")
        else:
            print(f"📭 Cache no encontrado")

        print(f"📖 Cargando desde GeoJSON...")
        grafo, nodos_coords = self._cargar_desde_geojson(ruta_geojson)

        # Guardar en cache
        print(f"\n💾 Guardando en cache para futuras cargas...")
        datos_cache = {
            'grafo': grafo,
            'nodos_coords': nodos_coords,
            'timestamp': datetime.now().isoformat(),
            'hash': hash_actual,
            'archivo_origen': ruta_geojson
        }

        try:
            with open(ruta_cache_red, 'wb') as f:
                pickle.dump(datos_cache, f)

            tamaño_cache = ruta_cache_red.stat().st_size / (1024 * 1024)  # MB
            print(f"✅ Cache guardado: {ruta_cache_red}")
            print(f"📦 Tamaño cache: {tamaño_cache:.1f} MB")
        except Exception as e:
            print(f"⚠️  No se pudo guardar cache: {e}")

        self.grafo = grafo
        self.nodos_coords = nodos_coords

        return grafo, nodos_coords

    def _cargar_desde_geojson(
        self,
        ruta: str
    ) -> Tuple[nx.Graph, Dict]:
        """Carga GeoJSON y crea grafo NetworkX con distancias reales"""

        # Leer archivo JSON
        print(f"\n📖 Paso 1/2: Leyendo archivo GeoJSON...")
        inicio = datetime.now()

        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)

        tiempo_lectura = (datetime.now() - inicio).total_seconds()

        if datos.get('type') != 'FeatureCollection':
            raise ValueError("El archivo debe ser un GeoJSON FeatureCollection")

        num_features = len(datos.get('features', []))
        print(f"✅ GeoJSON leído en {tiempo_lectura:.2f} segundos")
        print(f"📊 Features encontradas: {num_features:,}")

        # Construir grafo
        print(f"\n🔨 Paso 2/2: Construyendo grafo NetworkX...")
        inicio = datetime.now()

        grafo = nx.Graph()
        nodos_coords = {}
        stats = {
            'linestrings': 0,
            'otros_tipos': 0,
            'nodos_creados': 0,
            'aristas_creadas': 0
        }

        for idx, feature in enumerate(datos['features']):
            geometry = feature.get('geometry', {})
            geom_type = geometry.get('type')

            if geom_type != 'LineString':
                stats['otros_tipos'] += 1
                continue

            stats['linestrings'] += 1
            coords = geometry.get('coordinates', [])

            if len(coords) < 2:
                continue

            # Procesar cada segmento de la línea
            for i in range(len(coords) - 1):
                lon1, lat1 = coords[i][0], coords[i][1]
                lon2, lat2 = coords[i + 1][0], coords[i + 1][1]

                # IDs únicos basados en coordenadas (6 decimales = ~10 cm precisión)
                nodo_id_1 = f"n_{lat1:.6f}_{lon1:.6f}"
                nodo_id_2 = f"n_{lat2:.6f}_{lon2:.6f}"

                # Agregar nodos si no existen
                if nodo_id_1 not in nodos_coords:
                    nodos_coords[nodo_id_1] = (lat1, lon1)
                    grafo.add_node(nodo_id_1, lat=lat1, lon=lon1)
                    stats['nodos_creados'] += 1

                if nodo_id_2 not in nodos_coords:
                    nodos_coords[nodo_id_2] = (lat2, lon2)
                    grafo.add_node(nodo_id_2, lat=lat2, lon=lon2)
                    stats['nodos_creados'] += 1

                # Calcular distancia real en metros
                distancia = self._distancia_haversine(lat1, lon1, lat2, lon2)

                # Agregar arista con peso
                grafo.add_edge(
                    nodo_id_1,
                    nodo_id_2,
                    weight=distancia,
                    length=distancia
                )
                stats['aristas_creadas'] += 1

            # Mostrar progreso cada 1000 features
            if (idx + 1) % 1000 == 0:
                print(f"  ⏳ Procesadas {idx + 1:,}/{num_features:,} features...")

        tiempo_construccion = (datetime.now() - inicio).total_seconds()

        print(f"\n{'='*60}")
        print(f"✅ GRAFO CONSTRUIDO EXITOSAMENTE")
        print(f"{'='*60}")
        print(f"⏱️  Tiempo total: {tiempo_construccion:.2f} segundos")
        print(f"📊 LineStrings procesadas: {stats['linestrings']:,}")
        print(f"📊 Otros tipos ignorados: {stats['otros_tipos']:,}")
        print(f"📊 Nodos creados: {stats['nodos_creados']:,}")
        print(f"📊 Aristas creadas: {stats['aristas_creadas']:,}")
        print(f"📊 Nodos finales: {grafo.number_of_nodes():,}")
        print(f"📊 Aristas finales: {grafo.number_of_edges():,}")

        # Verificar conectividad
        if grafo.number_of_nodes() > 0:
            num_componentes = nx.number_connected_components(grafo)
            print(f"🔗 Componentes conectados: {num_componentes}")
            if num_componentes > 1:
                print(f"⚠️  Red tiene múltiples componentes desconectados")

        return grafo, nodos_coords

    def filtrar_por_bbox(
        self,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float
    ) -> Tuple[nx.Graph, Dict]:
        """
        Filtra el grafo para mantener solo nodos dentro del bounding box.

        Args:
            lat_min, lat_max: Rango de latitud
            lon_min, lon_max: Rango de longitud

        Returns:
            Tupla (subgrafo, nodos_filtrados)
        """
        if self.grafo is None:
            raise ValueError("Primero debes cargar una red con cargar_con_cache()")

        print(f"\n✂️  Filtrando por bounding box...")
        print(f"   Latitud: {lat_min:.4f} a {lat_max:.4f}")
        print(f"   Longitud: {lon_min:.4f} a {lon_max:.4f}")

        # Filtrar nodos
        nodos_filtrados = {
            nodo_id: coords
            for nodo_id, coords in self.nodos_coords.items()
            if lat_min <= coords[0] <= lat_max and lon_min <= coords[1] <= lon_max
        }

        # Crear subgrafo
        subgrafo = self.grafo.subgraph(nodos_filtrados.keys()).copy()

        reduccion = 100 * (1 - len(nodos_filtrados) / len(self.nodos_coords))

        print(f"✅ Nodos filtrados: {len(nodos_filtrados):,} de {len(self.nodos_coords):,} ({reduccion:.1f}% reducción)")
        print(f"✅ Aristas filtradas: {subgrafo.number_of_edges():,} de {self.grafo.number_of_edges():,}")

        return subgrafo, nodos_filtrados

    def filtrar_por_puntos(
        self,
        puntos: List[Tuple[float, float]],
        margen_km: float = 2.0
    ) -> Tuple[nx.Graph, Dict]:
        """
        Filtra el grafo para mantener solo el área alrededor de los puntos.
        Útil para reducir tamaño cuando solo necesitas un subconjunto.

        Args:
            puntos: Lista de tuplas (lat, lon)
            margen_km: Margen en kilómetros alrededor de los puntos

        Returns:
            Tupla (subgrafo, nodos_filtrados)
        """
        if self.grafo is None:
            raise ValueError("Primero debes cargar una red con cargar_con_cache()")

        print(f"\n✂️  Filtrando red por {len(puntos)} puntos de interés...")
        print(f"   Margen: {margen_km} km")

        # Calcular bbox que contiene todos los puntos + margen
        lats = [p[0] for p in puntos]
        lons = [p[1] for p in puntos]

        # Aproximación: 1 grado ≈ 111 km
        margen_grados = margen_km / 111.0

        lat_min = min(lats) - margen_grados
        lat_max = max(lats) + margen_grados
        lon_min = min(lons) - margen_grados
        lon_max = max(lons) + margen_grados

        return self.filtrar_por_bbox(lat_min, lat_max, lon_min, lon_max)

    @staticmethod
    def _distancia_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcula la distancia en metros entre dos puntos usando la fórmula de Haversine.

        Args:
            lat1, lon1: Coordenadas del primer punto
            lat2, lon2: Coordenadas del segundo punto

        Returns:
            Distancia en metros
        """
        R = 6371000  # Radio de la Tierra en metros

        # Convertir a radianes
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Diferencias
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Fórmula de Haversine
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        distancia = R * c

        return distancia

    def obtener_bbox(self) -> Dict[str, float]:
        """Obtiene el bounding box de la red cargada"""
        if self.nodos_coords is None or len(self.nodos_coords) == 0:
            return None

        lats = [coords[0] for coords in self.nodos_coords.values()]
        lons = [coords[1] for coords in self.nodos_coords.values()]

        return {
            'lat_min': min(lats),
            'lat_max': max(lats),
            'lon_min': min(lons),
            'lon_max': max(lons),
            'centro_lat': (min(lats) + max(lats)) / 2,
            'centro_lon': (min(lons) + max(lons)) / 2
        }


# Función de conveniencia para carga simple
def cargar_red_simple(ruta_geojson: str) -> Tuple[nx.Graph, Dict]:
    """
    Función simple para cargar una red sin opciones avanzadas.

    Args:
        ruta_geojson: Ruta al archivo GeoJSON

    Returns:
        Tupla (grafo, diccionario_coordenadas)
    """
    cargador = CargadorRedOptimizado()
    return cargador.cargar_con_cache(ruta_geojson)

