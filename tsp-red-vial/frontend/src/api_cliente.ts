/**
 * Cliente HTTP para comunicación con la API del backend.
 * Proporciona funciones para realizar peticiones a todos los endpoints.
 */

import {
  EstadoSistema,
  ComparacionAlgoritmos,
  SolicitudEvaluacion,
  RespuestaError
} from './tipos';

/**
 * URL base de la API del backend.
 * Se obtiene de la configuración del servidor Vite.
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Maneja errores HTTP de forma consistente.
 * Extrae información del error y la formatea para mostrar al usuario.
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
 * Retorna información sobre red, puntos y algoritmos ejecutados.
 */
export async function obtenerEstado(): Promise<EstadoSistema> {
  const response = await fetch(`${API_BASE_URL}/api/estado`);

  if (!response.ok) {
    await manejarError(response);
  }

  return await response.json();
}

/**
 * Carga un archivo de red vial en formato GeoJSON.
 * Envía el archivo al backend para procesamiento.
 */
export async function cargarRed(archivo: File): Promise<any> {
  const formData = new FormData();
  formData.append('archivo', archivo);

  const response = await fetch(`${API_BASE_URL}/api/cargar-red`, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    await manejarError(response);
  }

  return await response.json();
}

/**
 * Carga un archivo de puntos de interés en formato CSV.
 * Los puntos se integran automáticamente en la red vial.
 */
export async function cargarPuntos(archivo: File): Promise<any> {
  const formData = new FormData();
  formData.append('archivo', archivo);

  const response = await fetch(`${API_BASE_URL}/api/cargar-puntos`, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    await manejarError(response);
  }

  return await response.json();
}

/**
 * Ejecuta los algoritmos TSP especificados.
 * Retorna los resultados de todos los algoritmos solicitados.
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
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(solicitud)
  });

  if (!response.ok) {
    await manejarError(response);
  }

  return await response.json();
}

/**
 * Descarga los resultados en formato GeoJSON.
 * Retorna un blob que puede guardarse como archivo.
 */
export async function exportarResultados(formato: string = 'geojson'): Promise<Blob> {
  const response = await fetch(
    `${API_BASE_URL}/api/exportar?formato=${formato}`
  );

  if (!response.ok) {
    await manejarError(response);
  }

  return await response.blob();
}

/**
 * Descarga un archivo blob con el nombre especificado.
 * Crea un enlace temporal y lo activa para iniciar la descarga.
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
 * Realiza una petición al endpoint de health check.
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

