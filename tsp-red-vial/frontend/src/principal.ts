/**
 * Módulo principal de la aplicación.
 * Coordina la interacción entre el mapa, la API y la interfaz de usuario.
 */

import { GestorMapa } from './mapa';
import {
  cargarRed,
  cargarPuntos,
  evaluarAlgoritmos,
  exportarResultados,
  descargarArchivo,
  verificarConexion,
  obtenerEstado
} from './api_cliente';
import { Punto, SolicitudEvaluacion, NOMBRES_ALGORITMOS } from './tipos';

/**
 * Clase principal que gestiona la aplicación.
 * Maneja el flujo de datos entre interfaz, API y mapa.
 */
class Aplicacion {
  private gestor_mapa: GestorMapa;
  private puntos_cargados: Punto[] = [];
  private estado_conectado: boolean = false;

  /**
   * Inicializa la aplicación y sus componentes.
   * Configura eventos y verifica conexión con el backend.
   */
  constructor() {
    this.gestor_mapa = new GestorMapa('mapa');
    this.configurarEventos();
    this.verificarBackend();
  }

  /**
   * Configura los event listeners de la interfaz.
   * Asocia elementos HTML con sus manejadores de eventos.
   */
  private configurarEventos(): void {
    const botonRed = document.getElementById('btn-cargar-red');
    const botonPuntos = document.getElementById('btn-cargar-puntos');
    const botonEvaluar = document.getElementById('btn-evaluar');
    const botonExportar = document.getElementById('btn-exportar');

    if (botonRed) {
      botonRed.addEventListener('click', () => this.manejarCargarRed());
    }

    if (botonPuntos) {
      botonPuntos.addEventListener('click', () => this.manejarCargarPuntos());
    }

    if (botonEvaluar) {
      botonEvaluar.addEventListener('click', () => this.manejarEvaluar());
    }

    if (botonExportar) {
      botonExportar.addEventListener('click', () => this.manejarExportar());
    }
  }

  /**
   * Verifica la conexión con el backend.
   * Muestra el estado de conexión en la interfaz.
   */
  private async verificarBackend(): Promise<void> {
    try {
      this.estado_conectado = await verificarConexion();
      this.actualizarEstadoConexion(this.estado_conectado);
    } catch {
      this.estado_conectado = false;
      this.actualizarEstadoConexion(false);
    }
  }

  /**
   * Actualiza el indicador visual de conexión.
   * Cambia color y texto según el estado.
   */
  private actualizarEstadoConexion(conectado: boolean): void {
    const indicador = document.getElementById('estado-conexion');
    if (indicador) {
      indicador.textContent = conectado ? 'Conectado' : 'Desconectado';
      indicador.className = conectado ? 'conectado' : 'desconectado';
    }
  }

  /**
   * Maneja la carga de archivo de red vial.
   * Lee el archivo, lo envía al backend y muestra el resultado.
   */
  private async manejarCargarRed(): Promise<void> {
    const input = document.getElementById('archivo-red') as HTMLInputElement;

    if (!input || !input.files || input.files.length === 0) {
      this.mostrarMensaje('Seleccione un archivo GeoJSON', 'error');
      return;
    }

    const archivo = input.files[0];

    if (!archivo.name.endsWith('.geojson')) {
      this.mostrarMensaje('El archivo debe ser GeoJSON', 'error');
      return;
    }

    try {
      this.mostrarCargando(true);

      const resultado = await cargarRed(archivo);

      const contenido = await archivo.text();
      const geojson = JSON.parse(contenido);

      this.gestor_mapa.dibujarRed(geojson);

      this.mostrarMensaje(
        `Red cargada: ${resultado.num_nodos} nodos, ${resultado.num_aristas} aristas`,
        'exito'
      );

      this.actualizarEstadoInterfaz();

    } catch (error) {
      this.mostrarMensaje(`Error cargando red: ${error}`, 'error');
    } finally {
      this.mostrarCargando(false);
    }
  }

  /**
   * Maneja la carga de archivo de puntos de interés.
   * Procesa el CSV, envía al backend e integra en la red.
   */
  private async manejarCargarPuntos(): Promise<void> {
    const input = document.getElementById('archivo-puntos') as HTMLInputElement;

    if (!input || !input.files || input.files.length === 0) {
      this.mostrarMensaje('Seleccione un archivo CSV', 'error');
      return;
    }

    const archivo = input.files[0];

    if (!archivo.name.endsWith('.csv')) {
      this.mostrarMensaje('El archivo debe ser CSV', 'error');
      return;
    }

    try {
      this.mostrarCargando(true);

      const resultado = await cargarPuntos(archivo);

      this.puntos_cargados = resultado.puntos;

      this.gestor_mapa.dibujarPuntos(this.puntos_cargados);

      this.mostrarMensaje(
        `${resultado.num_puntos} puntos integrados exitosamente`,
        'exito'
      );

      this.actualizarEstadoInterfaz();

    } catch (error) {
      this.mostrarMensaje(`Error cargando puntos: ${error}`, 'error');
    } finally {
      this.mostrarCargando(false);
    }
  }

  /**
   * Maneja la evaluación de algoritmos TSP.
   * Obtiene algoritmos seleccionados, ejecuta y muestra resultados.
   */
  private async manejarEvaluar(): Promise<void> {
    const algoritmos = this.obtenerAlgoritmosSeleccionados();

    if (algoritmos.length === 0) {
      this.mostrarMensaje('Seleccione al menos un algoritmo', 'error');
      return;
    }

    try {
      this.mostrarCargando(true);

      const solicitud: SolicitudEvaluacion = {
        algoritmos: algoritmos,
        limite_tiempo: 60.0
      };

      const resultado = await evaluarAlgoritmos(solicitud);

      this.gestor_mapa.limpiarRutas();

      const comparacion = resultado.comparacion;

      if (comparacion.fuerza_bruta) {
        this.gestor_mapa.dibujarRuta(
          comparacion.fuerza_bruta.ruta,
          this.puntos_cargados,
          'fuerza_bruta',
          comparacion.fuerza_bruta.distancia_total
        );
      }

      if (comparacion.held_karp) {
        this.gestor_mapa.dibujarRuta(
          comparacion.held_karp.ruta,
          this.puntos_cargados,
          'held_karp',
          comparacion.held_karp.distancia_total
        );
      }

      if (comparacion.vecino_2opt) {
        this.gestor_mapa.dibujarRuta(
          comparacion.vecino_2opt.ruta,
          this.puntos_cargados,
          '2opt',
          comparacion.vecino_2opt.distancia_total
        );
      }

      this.mostrarResultados(comparacion);

      this.mostrarMensaje('Algoritmos ejecutados exitosamente', 'exito');

    } catch (error) {
      this.mostrarMensaje(`Error evaluando algoritmos: ${error}`, 'error');
    } finally {
      this.mostrarCargando(false);
    }
  }

  /**
   * Maneja la exportación de resultados.
   * Descarga los resultados en formato GeoJSON.
   */
  private async manejarExportar(): Promise<void> {
    try {
      this.mostrarCargando(true);

      const blob = await exportarResultados('geojson');

      const fecha = new Date().toISOString().split('T')[0];
      const nombreArchivo = `resultados_tsp_${fecha}.geojson`;

      descargarArchivo(blob, nombreArchivo);

      this.mostrarMensaje('Resultados exportados exitosamente', 'exito');

    } catch (error) {
      this.mostrarMensaje(`Error exportando: ${error}`, 'error');
    } finally {
      this.mostrarCargando(false);
    }
  }

  /**
   * Obtiene los algoritmos seleccionados en la interfaz.
   * Lee los checkboxes marcados por el usuario.
   */
  private obtenerAlgoritmosSeleccionados(): string[] {
    const algoritmos: string[] = [];

    const checkboxes = document.querySelectorAll('.checkbox-algoritmo:checked');
    checkboxes.forEach((checkbox) => {
      const valor = (checkbox as HTMLInputElement).value;
      algoritmos.push(valor);
    });

    return algoritmos;
  }

  /**
   * Muestra los resultados en la interfaz.
   * Crea una tabla comparativa de los algoritmos ejecutados.
   */
  private mostrarResultados(comparacion: any): void {
    const contenedor = document.getElementById('resultados');
    if (!contenedor) return;

    let html = '<h3>Resultados</h3><table class="tabla-resultados">';
    html += '<tr><th>Algoritmo</th><th>Distancia (m)</th><th>Tiempo (s)</th><th>Óptimo</th></tr>';

    if (comparacion.fuerza_bruta) {
      const r = comparacion.fuerza_bruta;
      html += `<tr>
        <td>${NOMBRES_ALGORITMOS['fuerza_bruta']}</td>
        <td>${r.distancia_total.toFixed(2)}</td>
        <td>${r.tiempo_ejecucion.toFixed(3)}</td>
        <td>${r.es_optimo ? 'Sí' : 'No'}</td>
      </tr>`;
    }

    if (comparacion.held_karp) {
      const r = comparacion.held_karp;
      html += `<tr>
        <td>${NOMBRES_ALGORITMOS['held_karp']}</td>
        <td>${r.distancia_total.toFixed(2)}</td>
        <td>${r.tiempo_ejecucion.toFixed(3)}</td>
        <td>${r.es_optimo ? 'Sí' : 'No'}</td>
      </tr>`;
    }

    if (comparacion.vecino_2opt) {
      const r = comparacion.vecino_2opt;
      html += `<tr>
        <td>${NOMBRES_ALGORITMOS['2opt']}</td>
        <td>${r.distancia_total.toFixed(2)}</td>
        <td>${r.tiempo_ejecucion.toFixed(3)}</td>
        <td>${r.es_optimo ? 'Sí' : 'No'}</td>
      </tr>`;
    }

    html += '</table>';
    contenedor.innerHTML = html;
    contenedor.style.display = 'block';
  }

  /**
   * Muestra un mensaje al usuario.
   * Puede ser de tipo exito, error o info.
   */
  private mostrarMensaje(texto: string, tipo: 'exito' | 'error' | 'info'): void {
    const contenedor = document.getElementById('mensajes');
    if (!contenedor) return;

    const mensaje = document.createElement('div');
    mensaje.className = `mensaje mensaje-${tipo}`;
    mensaje.textContent = texto;

    contenedor.appendChild(mensaje);

    setTimeout(() => {
      mensaje.remove();
    }, 5000);
  }

  /**
   * Muestra u oculta el indicador de carga.
   * Proporciona feedback visual durante operaciones largas.
   */
  private mostrarCargando(mostrar: boolean): void {
    const spinner = document.getElementById('spinner');
    if (spinner) {
      spinner.style.display = mostrar ? 'block' : 'none';
    }
  }

  /**
   * Actualiza el estado de la interfaz según datos del backend.
   * Habilita/deshabilita botones según el estado del sistema.
   */
  private async actualizarEstadoInterfaz(): Promise<void> {
    try {
      const estado = await obtenerEstado();

      const btnPuntos = document.getElementById('btn-cargar-puntos') as HTMLButtonElement;
      const btnEvaluar = document.getElementById('btn-evaluar') as HTMLButtonElement;
      const btnExportar = document.getElementById('btn-exportar') as HTMLButtonElement;

      if (btnPuntos) {
        btnPuntos.disabled = !estado.red_cargada;
      }

      if (btnEvaluar) {
        btnEvaluar.disabled = !estado.puntos_cargados;
      }

      if (btnExportar) {
        btnExportar.disabled = estado.algoritmos_ejecutados.length === 0;
      }
    } catch {
      console.error('Error actualizando estado de interfaz');
    }
  }
}

/**
 * Inicializa la aplicación cuando el DOM está listo.
 * Punto de entrada principal del frontend.
 */
document.addEventListener('DOMContentLoaded', () => {
  new Aplicacion();
});

