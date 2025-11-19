/**
 * Módulo de gestión del mapa interactivo usando Leaflet.
 * Maneja la visualización de la red vial, puntos y rutas TSP.
 */

import * as L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {
  GeoJSONFeatureCollection,
  CONFIG_MAPA_DEFAULT,
  COLORES_ALGORITMOS,
  Punto
} from './tipos';
import { obtenerRutaDetallada } from './api_cliente';

/**
 * Clase principal para gestión del mapa.
 * Encapsula toda la funcionalidad relacionada con Leaflet.
 */
export class GestorMapa {
  private mapa: L.Map;
  private capaRed?: L.LayerGroup;
  private capaPuntos?: L.LayerGroup;
  private capaRutas?: L.LayerGroup;

  /**
   * Inicializa el mapa en el contenedor especificado.
   */
  constructor(contenedorId: string) {
    this.mapa = L.map(contenedorId).setView(
      CONFIG_MAPA_DEFAULT.centro,
      CONFIG_MAPA_DEFAULT.zoom
    );

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: CONFIG_MAPA_DEFAULT.zoom_max,
      minZoom: CONFIG_MAPA_DEFAULT.zoom_min
    }).addTo(this.mapa);

    this.capaRed = L.layerGroup().addTo(this.mapa);
    this.capaPuntos = L.layerGroup().addTo(this.mapa);
    this.capaRutas = L.layerGroup().addTo(this.mapa);
  }

  /**
   * Dibuja la red vial en el mapa.
   */
  dibujarRed(geojson: GeoJSONFeatureCollection): void {
    if (this.capaRed) {
      this.capaRed.clearLayers();
      L.geoJSON(geojson as any, {
        style: () => ({ color: '#0066CC', weight: 2, opacity: 0.6 })
      }).addTo(this.capaRed);
    }
    this.ajustarVista(geojson);
  }

  /**
   * Dibuja los puntos de interés en el mapa con un color más visible.
   */
  dibujarPuntos(puntos: Punto[]): void {
    if (!this.capaPuntos) return;
    this.capaPuntos.clearLayers();

    puntos.forEach(punto => {
      const marcador = L.circleMarker([punto.latitud, punto.longitud], {
        radius: 8,
        fillColor: '#D90429', // Rojo más intenso
        color: '#FFFFFF',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.9
      }).bindPopup(`<b>${punto.nombre}</b><br>ID: ${punto.id}`);
      
      marcador.addTo(this.capaPuntos);
    });
  }

  /**
   * Dibuja una ruta TSP detallada en el mapa, segmento por segmento.
   */
  async dibujarRutaDetallada(
    rutaIndices: number[],
    puntos: Punto[],
    algoritmo: string,
    distanciaTotal: number
  ): Promise<void> {
    if (!this.capaRutas) return;

    const color = COLORES_ALGORITMOS[algoritmo] || '#0000FF';

    for (let i = 0; i < rutaIndices.length - 1; i++) {
      const idxOrigen = rutaIndices[i];
      const idxDestino = rutaIndices[i + 1];

      try {
        const rutaDetallada = await obtenerRutaDetallada(idxOrigen, idxDestino);
        if (rutaDetallada.camino_coords && rutaDetallada.camino_coords.length > 0) {
          const coordenadasLinea = rutaDetallada.camino_coords.map(c => [c[0], c[1]] as [number, number]);
          
          L.polyline(coordenadasLinea, {
            color: color,
            weight: 5,
            opacity: 0.75
          }).addTo(this.capaRutas);
        }
      } catch (error) {
        console.error(`Error obteniendo ruta detallada para ${algoritmo} entre ${idxOrigen} y ${idxDestino}:`, error);
        // Dibuja una línea recta como fallback si la API falla
        const p1 = puntos[idxOrigen];
        const p2 = puntos[idxDestino];
        L.polyline([[p1.latitud, p1.longitud], [p2.latitud, p2.longitud]], {
          color: color,
          weight: 5,
          opacity: 0.75,
          dashArray: '10, 10' // Línea punteada para indicar error/fallback
        }).addTo(this.capaRutas);
      }
    }

    // Dibuja los números de visita sobre los puntos
    this.dibujarNumerosDeVisita(rutaIndices, puntos, color);
  }

  /**
   * Dibuja los números de orden de visita sobre cada punto de la ruta.
   */
  private dibujarNumerosDeVisita(rutaIndices: number[], puntos: Punto[], color: string): void {
    if (!this.capaRutas) return;

    rutaIndices.slice(0, -1).forEach((idx, i) => {
      const punto = puntos[idx];
      const numero = i + 1;
      
      const iconoNumero = L.divIcon({
        html: `<div style="background-color: ${color}; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: bold; border: 2px solid white;">${numero}</div>`,
        className: 'numero-visita-icono',
        iconSize: [24, 24]
      });

      L.marker([punto.latitud, punto.longitud], { icon: iconoNumero, zIndexOffset: 1000 }).addTo(this.capaRutas);
    });
  }

  /**
   * Limpia todas las capas del mapa.
   */
  limpiarTodo(): void {
    this.capaRed?.clearLayers();
    this.capaPuntos?.clearLayers();
    this.capaRutas?.clearLayers();
  }

  limpiarRutas(): void {
    this.capaRutas?.clearLayers();
  }

  private ajustarVista(geojson: GeoJSONFeatureCollection): void {
    const capa = L.geoJSON(geojson as any);
    if (capa.getBounds().isValid()) {
      this.mapa.fitBounds(capa.getBounds(), { padding: [50, 50] });
    }
  }
}
