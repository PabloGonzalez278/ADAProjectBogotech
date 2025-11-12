"""
Modelos de datos para el sistema de optimización de rutas TSP.
Define las estructuras de datos utilizando Pydantic para validación y serialización.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Dict, Optional
from datetime import datetime


class Punto(BaseModel):
    """
    Representa un punto de interés en el mapa.
    Contiene las coordenadas geográficas y metadatos asociados.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "latitud": 4.6486,
                "longitud": -74.0978,
                "nombre": "Plaza de Bolívar"
            }
        }
    )

    id: int = Field(..., description="Identificador único del punto")
    latitud: float = Field(..., ge=-90, le=90, description="Latitud en grados decimales")
    longitud: float = Field(..., ge=-180, le=180, description="Longitud en grados decimales")
    nombre: str = Field(..., min_length=1, description="Nombre descriptivo del punto")

    @field_validator('latitud', 'longitud', mode='before')
    @classmethod
    def validar_coordenadas(cls, v):
        """Valida que las coordenadas sean números válidos"""
        if not isinstance(v, (int, float)):
            raise ValueError("La coordenada debe ser un número")
        return float(v)



class InfoRed(BaseModel):
    """
    Metadatos sobre la red vial cargada.
    Proporciona información estadística y geográfica de la red.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "num_nodos": 5000,
                "num_aristas": 10000,
                "bbox": {
                    "lat_min": 4.60,
                    "lat_max": 4.70,
                    "lon_min": -74.10,
                    "lon_max": -74.05
                },
                "puntos_integrados": [1, 2, 3, 4, 5],
                "timestamp_carga": "2025-01-11T10:30:00"
            }
        }
    )

    num_nodos: int = Field(..., description="Número de nodos en el grafo")
    num_aristas: int = Field(..., description="Número de aristas en el grafo")
    bbox: Optional[Dict[str, float]] = Field(None, description="Bounding box de la red")
    puntos_integrados: List[int] = Field(default_factory=list, description="IDs de puntos integrados")
    timestamp_carga: Optional[str] = Field(None, description="Fecha y hora de carga")


class ResultadoTSP(BaseModel):
    """
    Almacena el resultado de ejecutar un algoritmo TSP.
    Incluye la ruta óptima encontrada, métricas de rendimiento y metadatos.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "algoritmo": "held_karp",
                "ruta": [0, 2, 1, 3, 4, 0],
                "distancia_total": 12458.5,
                "tiempo_ejecucion": 0.045,
                "num_puntos": 5,
                "es_optimo": True
            }
        }
    )

    algoritmo: str = Field(..., description="Nombre del algoritmo utilizado")
    ruta: List[int] = Field(..., description="Secuencia de IDs de puntos en el orden de visita")
    distancia_total: float = Field(..., ge=0, description="Distancia total de la ruta en metros")
    tiempo_ejecucion: float = Field(..., ge=0, description="Tiempo de ejecución en segundos")
    num_puntos: int = Field(..., gt=0, description="Número de puntos en el problema")
    es_optimo: bool = Field(..., description="Indica si la solución es óptima garantizada")

    @field_validator('ruta')
    @classmethod
    def validar_ruta(cls, v):
        """Valida que la ruta sea un ciclo hamiltoniano válido"""
        if len(v) < 2:
            raise ValueError("La ruta debe contener al menos 2 puntos")
        if v[0] != v[-1]:
            raise ValueError("La ruta debe ser un ciclo (empezar y terminar en el mismo punto)")
        return v



class ComparacionAlgoritmos(BaseModel):
    """
    Agrupa los resultados de múltiples algoritmos TSP para comparación.
    Permite analizar el rendimiento relativo de diferentes enfoques.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "num_puntos": 10,
                "fuerza_bruta": None,
                "held_karp": {
                    "algoritmo": "held_karp",
                    "ruta": [0, 2, 1, 3, 4, 0],
                    "distancia_total": 12458.5,
                    "tiempo_ejecucion": 0.045,
                    "num_puntos": 5,
                    "es_optimo": True
                },
                "vecino_2opt": {
                    "algoritmo": "2opt",
                    "ruta": [0, 1, 2, 3, 4, 0],
                    "distancia_total": 12892.3,
                    "tiempo_ejecucion": 0.012,
                    "num_puntos": 5,
                    "es_optimo": False
                }
            }
        }
    )

    fuerza_bruta: Optional[ResultadoTSP] = Field(None, description="Resultado de fuerza bruta")
    held_karp: Optional[ResultadoTSP] = Field(None, description="Resultado de Held-Karp")
    vecino_2opt: Optional[ResultadoTSP] = Field(None, description="Resultado de 2-Opt")
    num_puntos: int = Field(..., gt=0, description="Número de puntos del problema")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Timestamp de la comparación")

    def obtener_mejor_resultado(self) -> Optional[ResultadoTSP]:
        """
        Retorna el resultado con menor distancia total.
        Útil para identificar el algoritmo que encontró la mejor solución.
        """
        resultados = [r for r in [self.fuerza_bruta, self.held_karp, self.vecino_2opt] if r is not None]
        if not resultados:
            return None
        return min(resultados, key=lambda r: r.distancia_total)

    def obtener_mas_rapido(self) -> Optional[ResultadoTSP]:
        """
        Retorna el resultado que se ejecutó más rápido.
        Útil para análisis de rendimiento temporal.
        """
        resultados = [r for r in [self.fuerza_bruta, self.held_karp, self.vecino_2opt] if r is not None]
        if not resultados:
            return None
        return min(resultados, key=lambda r: r.tiempo_ejecucion)



class MatrizDistancias(BaseModel):
    """
    Representa la matriz de distancias entre puntos.
    Almacena las distancias calculadas sobre la red vial.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "matriz": [
                    [0.0, 150.5, 230.8],
                    [150.5, 0.0, 180.2],
                    [230.8, 180.2, 0.0]
                ],
                "puntos_ids": [1, 2, 3],
                "dimension": 3
            }
        }
    )

    matriz: List[List[float]] = Field(..., description="Matriz NxN de distancias")
    puntos_ids: List[int] = Field(..., description="IDs de los puntos correspondientes")
    dimension: int = Field(..., gt=0, description="Dimensión de la matriz (N)")

    @field_validator('matriz')
    @classmethod
    def validar_matriz(cls, v):
        """Valida que la matriz sea cuadrada y simétrica"""
        if not v:
            raise ValueError("La matriz no puede estar vacía")

        n = len(v)
        for fila in v:
            if len(fila) != n:
                raise ValueError("La matriz debe ser cuadrada")

        return v

    def obtener_distancia(self, i: int, j: int) -> float:
        """
        Obtiene la distancia entre dos puntos por sus índices.
        Valida que los índices estén dentro del rango válido.
        """
        if i < 0 or i >= self.dimension or j < 0 or j >= self.dimension:
            raise IndexError(f"Índices fuera de rango: ({i}, {j})")
        return self.matriz[i][j]


class SolicitudCargaRed(BaseModel):
    """
    Modelo para la solicitud de carga de red vial.
    Define los parámetros necesarios para cargar un archivo GeoJSON.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ruta_archivo": "datos/bogota_centro.geojson",
                "forzar_recarga": False
            }
        }
    )

    ruta_archivo: str = Field(..., description="Ruta al archivo GeoJSON")
    forzar_recarga: bool = Field(default=False, description="Forzar recarga ignorando cache")


class SolicitudCargaPuntos(BaseModel):
    """
    Modelo para la solicitud de carga de puntos de interés.
    Define los parámetros para cargar un archivo CSV de puntos.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ruta_archivo": "datos/puntos_ejemplo.csv",
                "integrar_a_red": True
            }
        }
    )

    ruta_archivo: str = Field(..., description="Ruta al archivo CSV de puntos")
    integrar_a_red: bool = Field(default=True, description="Integrar puntos automáticamente a la red")


class SolicitudEvaluacion(BaseModel):
    """
    Modelo para la solicitud de evaluación de algoritmos TSP.
    Especifica qué algoritmos ejecutar y sus parámetros.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "algoritmos": ["held_karp", "2opt"],
                "limite_tiempo": 60.0
            }
        }
    )

    algoritmos: List[str] = Field(
        default=["fuerza_bruta", "held_karp", "2opt"],
        description="Lista de algoritmos a ejecutar"
    )
    limite_tiempo: Optional[float] = Field(
        default=60.0,
        description="Límite de tiempo en segundos por algoritmo"
    )

    @field_validator('algoritmos')
    @classmethod
    def validar_algoritmos(cls, v):
        """Valida que los algoritmos especificados sean válidos"""
        algoritmos_validos = {"fuerza_bruta", "held_karp", "2opt"}
        for alg in v:
            if alg not in algoritmos_validos:
                raise ValueError(f"Algoritmo inválido: {alg}. Válidos: {algoritmos_validos}")
        return v


class RespuestaError(BaseModel):
    """
    Modelo estándar para respuestas de error de la API.
    Proporciona información detallada sobre errores ocurridos.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "Archivo no encontrado",
                "codigo": 404,
                "detalle": "El archivo datos/red.geojson no existe",
                "timestamp": "2025-01-11T10:30:00"
            }
        }
    )

    error: str = Field(..., description="Mensaje de error")
    codigo: int = Field(..., description="Código de error HTTP")
    detalle: Optional[str] = Field(None, description="Detalle adicional del error")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

