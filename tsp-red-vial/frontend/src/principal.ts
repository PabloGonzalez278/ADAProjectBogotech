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
import { Punto, SolicitudEvaluacion, NOMBRES_ALGORITMOS, ComparacionAlgoritmos } from './tipos';

/**
 * Clase principal que gestiona la aplicación.
 */
class Aplicacion {
  private gestor_mapa: GestorMapa;
  private puntos_cargados: Punto[] = [];
  private estado_conectado: boolean = false;

  constructor() {
    this.gestor_mapa = new GestorMapa('mapa');
    this.configurarEventos();
    this.verificarBackend();
  }

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

  private async verificarBackend(): Promise<void> {
    this.estado_conectado = await verificarConexion();
    this.actualizarEstadoConexion(this.estado_conectado);
  }

  private actualizarEstadoConexion(conectado: boolean): void {
    const indicador = document.getElementById('estado-conexion');
    if (indicador) {
      indicador.textContent = conectado ? 'Conectado' : 'Desconectado';
      indicador.className = conectado ? 'conectado' : 'desconectado';
    }
  }

  private async manejarCargarRed(): Promise<void> {
    const input = document.getElementById('archivo-red') as HTMLInputElement;
    if (!input || !input.files || input.files.length === 0) {
        this.mostrarMensaje('Seleccione un archivo GeoJSON para la red', 'error');
        return;
    }
    const archivo = input.files[0];
    this.mostrarCargando(true);
    try {
        const resultado = await cargarRed(archivo);
        const geojson = JSON.parse(await archivo.text());
        this.gestor_mapa.dibujarRed(geojson);
        this.mostrarMensaje(`Red cargada: ${resultado.num_nodos} nodos, ${resultado.num_aristas} aristas`, 'exito');
        this.actualizarEstadoInterfaz();
    } catch (error) {
        this.mostrarMensaje(`Error cargando red: ${error}`, 'error');
    } finally {
        this.mostrarCargando(false);
    }
  }

  private async manejarCargarPuntos(): Promise<void> {
    const input = document.getElementById('archivo-puntos') as HTMLInputElement;
    if (!input || !input.files || input.files.length === 0) {
        this.mostrarMensaje('Seleccione un archivo CSV con los puntos', 'error');
        return;
    }
    const archivo = input.files[0];
    this.mostrarCargando(true);
    try {
        const resultado = await cargarPuntos(archivo);
        this.puntos_cargados = resultado.puntos;
        this.gestor_mapa.dibujarPuntos(this.puntos_cargados);
        this.mostrarMensaje(`${resultado.num_puntos} puntos integrados`, 'exito');
        this.actualizarEstadoInterfaz();
    } catch (error) {
        this.mostrarMensaje(`Error cargando puntos: ${error}`, 'error');
    } finally {
        this.mostrarCargando(false);
    }
  }

  private async manejarEvaluar(): Promise<void> {
    const algoritmos = this.obtenerAlgoritmosSeleccionados();
    if (algoritmos.length === 0) {
      this.mostrarMensaje('Seleccione al menos un algoritmo', 'error');
      return;
    }

    this.mostrarCargando(true);
    try {
      const solicitud: SolicitudEvaluacion = { algoritmos, limite_tiempo: 60.0 };
      const resultado = await evaluarAlgoritmos(solicitud);
      
      this.gestor_mapa.limpiarRutas();
      
      const comparacion = resultado.comparacion;
      const promesasDeRutas = [];

      if (comparacion.fuerza_bruta) {
        promesasDeRutas.push(this.gestor_mapa.dibujarRutaDetallada(
          comparacion.fuerza_bruta.ruta,
          this.puntos_cargados,
          'fuerza_bruta',
          comparacion.fuerza_bruta.distancia_total
        ));
      }
      if (comparacion.held_karp) {
        promesasDeRutas.push(this.gestor_mapa.dibujarRutaDetallada(
          comparacion.held_karp.ruta,
          this.puntos_cargados,
          'held_karp',
          comparacion.held_karp.distancia_total
        ));
      }
      if (comparacion.vecino_2opt) {
        promesasDeRutas.push(this.gestor_mapa.dibujarRutaDetallada(
          comparacion.vecino_2opt.ruta,
          this.puntos_cargados,
          '2opt',
          comparacion.vecino_2opt.distancia_total
        ));
      }

      await Promise.all(promesasDeRutas);

      this.mostrarResultados(comparacion);
      this.mostrarMensaje('Algoritmos ejecutados y rutas dibujadas', 'exito');
      this.actualizarEstadoInterfaz();

    } catch (error) {
      this.mostrarMensaje(`Error evaluando algoritmos: ${error}`, 'error');
    } finally {
      this.mostrarCargando(false);
    }
  }

  private async manejarExportar(): Promise<void> {
    this.mostrarCargando(true);
    try {
      const blob = await exportarResultados('geojson');
      descargarArchivo(blob, `resultados_tsp_${new Date().toISOString()}.geojson`);
      this.mostrarMensaje('Resultados exportados exitosamente', 'exito');
    } catch (error) {
      this.mostrarMensaje(`Error exportando: ${error}`, 'error');
    } finally {
      this.mostrarCargando(false);
    }
  }

  private obtenerAlgoritmosSeleccionados(): string[] {
    const seleccionados: string[] = [];
    document.querySelectorAll('.checkbox-algoritmo:checked').forEach(el => {
      seleccionados.push((el as HTMLInputElement).value);
    });
    return seleccionados;
  }

  private mostrarResultados(comparacion: ComparacionAlgoritmos): void {
    const contenedor = document.getElementById('resultados');
    if (!contenedor) return;

    const resultados = [comparacion.fuerza_bruta, comparacion.held_karp, comparacion.vecino_2opt].filter(r => r != null);
    if (resultados.length === 0) {
      contenedor.style.display = 'none';
      return;
    }

    const mejorResultado = resultados.reduce((mejor, actual) => actual!.distancia_total < mejor!.distancia_total ? actual : mejor);

    let html = `
      <div class="resumen-resultados">
        Mejor ruta encontrada: 
        <strong>${(mejorResultado!.distancia_total / 1000).toFixed(2)} km</strong> 
        con ${NOMBRES_ALGORITMOS[mejorResultado!.algoritmo]}
      </div>
      <table class="tabla-resultados">
        <tr>
          <th>Algoritmo</th>
          <th>Distancia (km)</th>
          <th>Tiempo (s)</th>
          <th>Óptimo
            <span class="tooltip">
              &#9432;
              <span class="tooltiptext">Indica si el algoritmo garantiza la mejor ruta posible.</span>
            </span>
          </th>
        </tr>`;

    resultados.forEach(r => {
      if (!r) return;
      const esMejor = r.algoritmo === mejorResultado!.algoritmo;
      const optimoIcono = r.es_optimo 
        ? `<span class="tooltip">&#9989;<span class="tooltiptext">Garantiza la solución óptima.</span></span>`
        : `<span class="tooltip">&#10060;<span class="tooltiptext">Es una aproximación, no garantiza la ruta más corta.</span></span>`;

      html += `
        <tr class="${esMejor ? 'fila-mejor' : ''}">
          <td>${NOMBRES_ALGORITMOS[r.algoritmo]}</td>
          <td>${(r.distancia_total / 1000).toFixed(2)}</td>
          <td>${r.tiempo_ejecucion.toFixed(4)}</td>
          <td style="text-align: center;">${optimoIcono}</td>
        </tr>`;
    });

    html += '</table>';
    contenedor.innerHTML = html;
    contenedor.style.display = 'block';
  }

  private mostrarMensaje(texto: string, tipo: 'exito' | 'error' | 'info'): void {
    const contenedor = document.getElementById('mensajes');
    if (!contenedor) return;
    const mensaje = document.createElement('div');
    mensaje.className = `mensaje mensaje-${tipo}`;
    mensaje.textContent = texto;
    contenedor.appendChild(mensaje);
    setTimeout(() => mensaje.remove(), 5000);
  }

  private mostrarCargando(mostrar: boolean): void {
    const spinner = document.getElementById('spinner');
    if (spinner) spinner.style.display = mostrar ? 'flex' : 'none';
  }

  private async actualizarEstadoInterfaz(): Promise<void> {
    try {
      const estado = await obtenerEstado();
      (document.getElementById('btn-cargar-puntos') as HTMLButtonElement).disabled = !estado.red_cargada;
      (document.getElementById('btn-evaluar') as HTMLButtonElement).disabled = !estado.puntos_cargados;
      (document.getElementById('btn-exportar') as HTMLButtonElement).disabled = estado.algoritmos_ejecutados.length === 0;
    } catch {
      console.error('Error actualizando estado de interfaz');
    }
  }
}

document.addEventListener('DOMContentLoaded', () => new Aplicacion());
