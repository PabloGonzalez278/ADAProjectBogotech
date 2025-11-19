/**
 * Cliente HTTP para comunicación con la API del backend.
 * Proporciona funciones para realizar peticiones a todos los endpoints.
 */

import {
  EstadoSistema,
  ComparacionAlgoritmos,
  SolicitudEvaluacion,
  RespuestaError,
  RutaDetallada
} from './tipos';

/**
 * URL base de la API del backend.
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Maneja errores HTTP de forma consistente.
 */
async function manejarError(response: Response): Promise<never> {
  let errorData: RespuestaError;
  try {
    errorData = await response.json();
  } catch {
    errorData = {
      error: 'Error del servidor',
      codigo: response.status,
      detalle: response.statusText,
      timestamp: new Date().toISOString()
    };
  }
  throw new Error(errorData.detalle || errorData.error);
}

/**
 * Obtiene el estado actual del sistema.
 */
export async function obtenerEstado(): Promise<EstadoSistema> {
  const response = await fetch(`${API_BASE_URL}/api/estado`);
  if (!response.ok) await manejarError(response);
  return await response.json();
}

/**
 * Carga un archivo de red vial en formato GeoJSON.
 */
export async function cargarRed(archivo: File): Promise<any> {
  const formData = new FormData();
  formData.append('archivo', archivo);
  const response = await fetch(`${API_BASE_URL}/api/cargar-red`, {
    method: 'POST',
    body: formData
  });
  if (!response.ok) await manejarError(response);
  return await response.json();
}

/**
 * Carga un archivo de puntos de interés en formato CSV.
 */
export async function cargarPuntos(archivo: File): Promise<any> {
  const formData = new FormData();
  formData.append('archivo', archivo);
  const response = await fetch(`${API_BASE_URL}/api/cargar-puntos`, {
    method: 'POST',
    body: formData
  });
  if (!response.ok) await manejarError(response);
  return await response.json();
}

/**
 * Ejecuta los algoritmos TSP especificados.
 */
export async function evaluarAlgoritmos(
  solicitud: SolicitudEvaluacion
): Promise<{
  mensaje: string;
  comparacion: ComparacionAlgoritmos;
  mejor_resultado: any;
  mas_rapido: any;
}> {
  const response = await fetch(`${API_BASE_URL}/api/evaluar-algoritmos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(solicitud)
  });
  if (!response.ok) await manejarError(response);
  return await response.json();
}

/**
 * Obtiene la ruta detallada (coordenadas) entre dos puntos.
 */
export async function obtenerRutaDetallada(punto_idx_origen: number, punto_idx_destino: number): Promise<RutaDetallada> {
    const response = await fetch(`${API_BASE_URL}/api/ruta-detallada?punto_idx_origen=${punto_idx_origen}&punto_idx_destino=${punto_idx_destino}`);
    if (!response.ok) {
        await manejarError(response);
    }
    return await response.json();
}

/**
 * Descarga los resultados en formato GeoJSON.
 */
export async function exportarResultados(formato: string = 'geojson'): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/api/exportar?formato=${formato}`);
  if (!response.ok) await manejarError(response);
  return await response.blob();
}

/**
 * Descarga un archivo blob con el nombre especificado.
 */
export function descargarArchivo(blob: Blob, nombreArchivo: string): void {
  const url = window.URL.createObjectURL(blob);
  const enlace = document.createElement('a');
  enlace.href = url;
  enlace.download = nombreArchivo;
  document.body.appendChild(enlace);
  enlace.click();
  document.body.removeChild(enlace);
  window.URL.revokeObjectURL(url);
}

/**
 * Verifica que el backend esté disponible.
 */
export async function verificarConexion(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000)
    });
    return response.ok;
  } catch {
    return false;
  }
}
