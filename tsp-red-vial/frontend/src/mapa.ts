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
   * Configura el mapa base con OpenStreetMap y controles.
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
   * Procesa un GeoJSON y renderiza las calles como líneas.
   */
  dibujarRed(geojson: GeoJSONFeatureCollection): void {
    if (this.capaRed) {
      this.capaRed.clearLayers();
    }

    const capa = L.geoJSON(geojson as any, {
      style: () => ({
        color: '#0066CC',
        weight: 2,
        opacity: 0.6
      }),
      onEachFeature: (feature, layer) => {
        if (feature.properties) {
          const props = feature.properties;
          const contenido = `
            <div class="popup-red">
              <strong>Arista de Red</strong><br>
              ${props.nodo_inicio || ''} → ${props.nodo_fin || ''}<br>
              Distancia: ${props.distancia ? props.distancia.toFixed(2) : 'N/A'} m
            </div>
          `;
          layer.bindPopup(contenido);
        }
      }
    });

    if (this.capaRed) {
      capa.addTo(this.capaRed);
    }

    this.ajustarVista(geojson);
  }

  /**
   * Dibuja los puntos de interés en el mapa.
   * Muestra marcadores con información de cada punto.
   */
  dibujarPuntos(puntos: Punto[]): void {
    if (this.capaPuntos) {
      this.capaPuntos.clearLayers();
    }

    puntos.forEach(punto => {
      const marcador = L.circleMarker([punto.latitud, punto.longitud], {
        radius: 8,
        fillColor: '#FF6B6B',
        color: '#FFFFFF',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.8
      });

      const contenido = `
        <div class="popup-punto">
          <strong>${punto.nombre}</strong><br>
          ID: ${punto.id}<br>
          Lat: ${punto.latitud.toFixed(6)}<br>
          Lon: ${punto.longitud.toFixed(6)}
        </div>
      `;

      marcador.bindPopup(contenido);

      if (this.capaPuntos) {
        marcador.addTo(this.capaPuntos);
      }
    });
  }

  /**
   * Dibuja una ruta TSP en el mapa.
   * Visualiza el camino entre puntos con el color del algoritmo.
   */
  dibujarRuta(
    ruta: number[],
    puntos: Punto[],
    algoritmo: string,
    distancia: number
  ): void {
    if (!this.capaRutas) {
      return;
    }

    const color = COLORES_ALGORITMOS[algoritmo] || '#0000FF';
    const coordenadas: [number, number][] = [];

    for (const idx of ruta) {
      if (idx < puntos.length) {
        const punto = puntos[idx];
        coordenadas.push([punto.latitud, punto.longitud]);
      }
    }

    if (coordenadas.length < 2) {
      return;
    }

    const linea = L.polyline(coordenadas, {
      color: color,
      weight: 4,
      opacity: 0.7,
      dashArray: algoritmo === '2opt' ? '10, 5' : undefined
    });

    const contenido = `
      <div class="popup-ruta">
        <strong>Ruta ${algoritmo}</strong><br>
        Distancia: ${distancia.toFixed(2)} m<br>
        Puntos: ${ruta.length - 1}
      </div>
    `;

    linea.bindPopup(contenido);
    linea.addTo(this.capaRutas);

    ruta.slice(0, -1).forEach((idx, i) => {
      if (idx < puntos.length) {
        const punto = puntos[idx];
        const marcador = L.circleMarker([punto.latitud, punto.longitud], {
          radius: 6,
          fillColor: color,
          color: '#FFFFFF',
          weight: 2,
          opacity: 1,
          fillOpacity: 1
        });

        const label = L.divIcon({
          className: 'numero-visita',
          html: `<div style="background: ${color}; color: white; 
                 border-radius: 50%; width: 20px; height: 20px; 
                 display: flex; align-items: center; justify-content: center;
                 font-weight: bold; font-size: 12px;">${i + 1}</div>`,
          iconSize: [20, 20]
        });

        const marcadorNumero = L.marker([punto.latitud, punto.longitud], {
          icon: label
        });

        if (this.capaRutas) {
          marcador.addTo(this.capaRutas);
          marcadorNumero.addTo(this.capaRutas);
        }
      }
    });
  }

  /**
   * Limpia todas las rutas del mapa.
   * Útil antes de mostrar nuevos resultados.
   */
  limpiarRutas(): void {
    if (this.capaRutas) {
      this.capaRutas.clearLayers();
    }
  }

  /**
   * Limpia todos los elementos del mapa.
   * Remueve red, puntos y rutas.
   */
  limpiarTodo(): void {
    if (this.capaRed) {
      this.capaRed.clearLayers();
    }
    if (this.capaPuntos) {
      this.capaPuntos.clearLayers();
    }
    if (this.capaRutas) {
      this.capaRutas.clearLayers();
    }
  }

  /**
   * Ajusta la vista del mapa para mostrar todo el contenido.
   * Calcula el bounding box y hace zoom apropiado.
   */
  private ajustarVista(geojson: GeoJSONFeatureCollection): void {
    const capa = L.geoJSON(geojson as any);
    const bounds = capa.getBounds();

    if (bounds.isValid()) {
      this.mapa.fitBounds(bounds, { padding: [50, 50] });
    }
  }

  /**
   * Centra el mapa en una coordenada específica.
   * Útil para enfocar puntos de interés.
   */
  centrarEn(lat: number, lon: number, zoom?: number): void {
    this.mapa.setView([lat, lon], zoom || CONFIG_MAPA_DEFAULT.zoom);
  }

  /**
   * Obtiene la instancia del mapa Leaflet.
   * Permite acceso directo a la API de Leaflet si es necesario.
   */
  obtenerMapa(): L.Map {
    return this.mapa;
  }
}

