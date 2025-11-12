/**
 * Definiciones de tipos TypeScript para el cliente del sistema TSP.
 * Define las interfaces que corresponden a los modelos del backend.
 */

/**
 * Representa un punto de interés en el mapa.
 * Corresponde al modelo Punto del backend.
 */
export interface Punto {
  id: number;
  latitud: number;
  longitud: number;
  nombre: string;
}

/**
 * Información sobre la red vial cargada.
 * Contiene estadísticas y metadatos de la red.
 * (Actualmente no usada - disponible para futuras expansiones)
 */
/*
export interface InfoRed {
  num_nodos: number;
  num_aristas: number;
  bbox?: {
    lat_min: number;
    lat_max: number;
    lon_min: number;
    lon_max: number;
  };
  puntos_integrados?: number[];
  timestamp_carga?: string;
}
*/

/**
 * Resultado de la ejecución de un algoritmo TSP.
 * Incluye la ruta encontrada y métricas de rendimiento.
 */
export interface ResultadoTSP {
  algoritmo: string;
  ruta: number[];
  distancia_total: number;
  tiempo_ejecucion: number;
  num_puntos: number;
  es_optimo: boolean;
}

/**
 * Comparación de resultados de múltiples algoritmos.
 * Permite analizar el rendimiento relativo de cada enfoque.
 */
export interface ComparacionAlgoritmos {
  fuerza_bruta?: ResultadoTSP;
  held_karp?: ResultadoTSP;
  vecino_2opt?: ResultadoTSP;
  num_puntos: number;
  timestamp: string;
}

/**
 * Solicitud para evaluar algoritmos TSP.
 * Especifica qué algoritmos ejecutar.
 */
export interface SolicitudEvaluacion {
  algoritmos: string[];
  limite_tiempo?: number;
}

/**
 * Respuesta de error estándar de la API.
 * Proporciona información detallada sobre errores.
 */
export interface RespuestaError {
  error: string;
  codigo: number;
  detalle?: string;
  timestamp: string;
}

/**
 * Estado actual del sistema.
 * Refleja el estado de la red, puntos y algoritmos ejecutados.
 */
export interface EstadoSistema {
  red_cargada: boolean;
  puntos_cargados: boolean;
  num_nodos: number;
  num_aristas: number;
  num_puntos: number;
  algoritmos_ejecutados: string[];
  timestamp: string;
}

/**
 * Feature GeoJSON genérico.
 * Representa un elemento geográfico en el mapa.
 */
export interface GeoJSONFeature {
  type: 'Feature';
  properties: Record<string, any>;
  geometry: {
    type: string;
    coordinates: any;
  };
}

/**
 * FeatureCollection GeoJSON.
 * Colección de features geográficos.
 */
export interface GeoJSONFeatureCollection {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
  properties?: Record<string, any>;
}

/**
 * Colores asignados a cada algoritmo para visualización.
 * Facilita la distinción visual de rutas en el mapa.
 */
export const COLORES_ALGORITMOS: Record<string, string> = {
  fuerza_bruta: '#FF0000',
  held_karp: '#00FF00',
  '2opt': '#FFA500',
  vecino_2opt: '#FFA500'
};

/**
 * Nombres legibles de algoritmos.
 * Convierte nombres técnicos a nombres para mostrar al usuario.
 */
export const NOMBRES_ALGORITMOS: Record<string, string> = {
  fuerza_bruta: 'Fuerza Bruta',
  held_karp: 'Held-Karp',
  '2opt': '2-Opt',
  vecino_2opt: '2-Opt'
};

/**
 * Configuración del mapa Leaflet.
 * Define parámetros de visualización del mapa.
 */
export interface ConfigMapa {
  centro: [number, number];
  zoom: number;
  zoom_min: number;
  zoom_max: number;
}

/**
 * Configuración por defecto del mapa centrado en Bogotá.
 */
export const CONFIG_MAPA_DEFAULT: ConfigMapa = {
  centro: [4.6486, -74.0978],
  zoom: 13,
  zoom_min: 10,
  zoom_max: 18
};

