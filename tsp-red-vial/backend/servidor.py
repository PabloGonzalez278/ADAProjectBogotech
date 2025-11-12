"""
Servidor FastAPI para el sistema de optimización de rutas TSP.
Proporciona endpoints REST para cargar datos, ejecutar algoritmos y exportar resultados.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import csv
from pathlib import Path
from datetime import datetime

from dominio.modelos import (
    Punto, ResultadoTSP, ComparacionAlgoritmos,
    SolicitudEvaluacion
)
from dominio.cargador_red import CargadorRedOptimizado
from dominio.rutas_mas_cortas import calcular_matriz_distancias
from dominio.ajustar_puntos import integrar_multiples_puntos, validar_integracion
from dominio.tsp_fuerza_bruta import tsp_fuerza_bruta
from dominio.tsp_held_karp import tsp_held_karp
from dominio.tsp_vecino_2opt import tsp_2opt
from dominio.exportar_geo import exportar_comparacion_algoritmos
from configuracion import config

app = FastAPI(
    title=config.API_TITULO,
    version=config.API_VERSION,
    description=config.API_DESCRIPCION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGENES,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

estado_sistema = {
    'red_cargada': False,
    'puntos_cargados': False,
    'grafo': None,
    'nodos_coords': None,
    'puntos': [],
    'nodos_puntos': [],
    'matriz_distancias': None,
    'resultados_tsp': {}
}


@app.get("/")
async def raiz():
    """Endpoint raíz con información de la API"""
    return {
        "nombre": config.API_TITULO,
        "version": config.API_VERSION,
        "descripcion": config.API_DESCRIPCION,
        "endpoints": {
            "cargar_red": "POST /api/cargar-red",
            "cargar_puntos": "POST /api/cargar-puntos",
            "evaluar": "POST /api/evaluar-algoritmos",
            "exportar": "GET /api/exportar",
            "estado": "GET /api/estado"
        }
    }


@app.get("/api/estado")
async def obtener_estado():
    """Retorna el estado actual del sistema"""
    return {
        "red_cargada": estado_sistema['red_cargada'],
        "puntos_cargados": estado_sistema['puntos_cargados'],
        "num_nodos": estado_sistema['grafo'].number_of_nodes() if estado_sistema['grafo'] else 0,
        "num_aristas": estado_sistema['grafo'].number_of_edges() if estado_sistema['grafo'] else 0,
        "num_puntos": len(estado_sistema['puntos']),
        "algoritmos_ejecutados": list(estado_sistema['resultados_tsp'].keys()),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/cargar-red")
async def cargar_red(archivo: UploadFile = File(...)):
    """
    Carga una red vial desde un archivo GeoJSON.
    Procesa el archivo y construye el grafo de NetworkX.
    """
    try:
        if not archivo.filename.endswith('.geojson'):
            raise HTTPException(400, "El archivo debe ser GeoJSON")

        ruta_temporal = Path(f"temp_{archivo.filename}")

        with open(ruta_temporal, 'wb') as f:
            contenido = await archivo.read()
            f.write(contenido)

        cargador = CargadorRedOptimizado(ruta_cache="cache")

        grafo, nodos_coords = cargador.cargar_con_cache(
            str(ruta_temporal),
            forzar_recarga=False
        )

        estado_sistema['grafo'] = grafo
        estado_sistema['nodos_coords'] = nodos_coords
        estado_sistema['red_cargada'] = True

        ruta_temporal.unlink()

        bbox = cargador.obtener_bbox()

        return {
            "mensaje": "Red cargada exitosamente",
            "num_nodos": grafo.number_of_nodes(),
            "num_aristas": grafo.number_of_edges(),
            "bbox": bbox,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(500, f"Error cargando red: {str(e)}")


@app.post("/api/cargar-puntos")
async def cargar_puntos(archivo: UploadFile = File(...)):
    """
    Carga puntos de interés desde un archivo CSV.
    Integra los puntos automáticamente en la red vial.
    """
    try:
        if not estado_sistema['red_cargada']:
            raise HTTPException(400, "Primero debe cargar una red vial")

        if not archivo.filename.endswith('.csv'):
            raise HTTPException(400, "El archivo debe ser CSV")

        contenido = await archivo.read()
        lineas = contenido.decode('utf-8').splitlines()

        lector = csv.DictReader(lineas)
        puntos_data = []

        for fila in lector:
            punto = (
                int(fila['id']),
                float(fila['latitud']),
                float(fila['longitud']),
                fila.get('nombre', f"Punto {fila['id']}")
            )
            puntos_data.append(punto)

        if len(puntos_data) < 2:
            raise HTTPException(400, "Se necesitan al menos 2 puntos")

        print(f"\n[DEBUG] Integrando {len(puntos_data)} puntos...")
        print(f"[DEBUG] Grafo tiene {estado_sistema['grafo'].number_of_nodes()} nodos")
        print(f"[DEBUG] Diccionario tiene {len(estado_sistema['nodos_coords'])} coordenadas")

        resultados_integracion = integrar_multiples_puntos(
            estado_sistema['grafo'],
            estado_sistema['nodos_coords'],
            puntos_data,
            umbral_distancia=500.0,  # Aumentado de 100 a 500 metros
            mostrar_progreso=True
        )

        estado_sistema['puntos'] = [
            Punto(id=p[0], latitud=p[1], longitud=p[2], nombre=p[3])
            for p in puntos_data
        ]

        estado_sistema['nodos_puntos'] = [
            resultados_integracion[p[0]][0] for p in puntos_data
        ]

        estado_sistema['puntos_cargados'] = True

        es_valido, errores = validar_integracion(
            estado_sistema['grafo'],
            estado_sistema['nodos_coords'],
            estado_sistema['nodos_puntos']
        )

        if not es_valido:
            raise HTTPException(500, f"Validación falló: {errores}")

        return {
            "mensaje": "Puntos integrados exitosamente",
            "num_puntos": len(puntos_data),
            "puntos": [p.model_dump() for p in estado_sistema['puntos']],
            "validacion": "OK",
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detallado = traceback.format_exc()
        print(f"\n[ERROR] Error cargando puntos:\n{error_detallado}")
        raise HTTPException(500, f"Error cargando puntos: {str(e)}")


@app.post("/api/evaluar-algoritmos")
async def evaluar_algoritmos(solicitud: SolicitudEvaluacion):
    """
    Ejecuta los algoritmos TSP solicitados y retorna los resultados.
    Calcula la matriz de distancias y ejecuta los algoritmos especificados.
    """
    try:
        if not estado_sistema['puntos_cargados']:
            raise HTTPException(400, "Primero debe cargar puntos")

        print("\nCalculando matriz de distancias...")

        puntos_coords = [
            (p.latitud, p.longitud) for p in estado_sistema['puntos']
        ]

        matriz = calcular_matriz_distancias(
            estado_sistema['grafo'],
            puntos_coords,
            estado_sistema['nodos_coords'],
            estado_sistema['nodos_puntos'],
            mostrar_progreso=True
        )

        estado_sistema['matriz_distancias'] = matriz

        resultados = {}

        if 'fuerza_bruta' in solicitud.algoritmos:
            if len(estado_sistema['puntos']) <= config.MAX_PUNTOS_FUERZA_BRUTA:
                print("\nEjecutando Fuerza Bruta...")
                ruta, distancia, stats = tsp_fuerza_bruta(matriz, mostrar_progreso=True)

                resultados['fuerza_bruta'] = ResultadoTSP(
                    algoritmo="fuerza_bruta",
                    ruta=ruta,
                    distancia_total=distancia,
                    tiempo_ejecucion=stats['tiempo_segundos'],
                    num_puntos=len(estado_sistema['puntos']),
                    es_optimo=True
                )
            else:
                print(f"\nFuerza Bruta omitido: {len(estado_sistema['puntos'])} puntos > límite de {config.MAX_PUNTOS_FUERZA_BRUTA}")

        if 'held_karp' in solicitud.algoritmos:
            if len(estado_sistema['puntos']) <= config.MAX_PUNTOS_HELD_KARP:
                print("\nEjecutando Held-Karp...")
                ruta, distancia, stats = tsp_held_karp(matriz, mostrar_progreso=True)

                resultados['held_karp'] = ResultadoTSP(
                    algoritmo="held_karp",
                    ruta=ruta,
                    distancia_total=distancia,
                    tiempo_ejecucion=stats['tiempo_segundos'],
                    num_puntos=len(estado_sistema['puntos']),
                    es_optimo=True
                )
            else:
                print(f"\nHeld-Karp omitido: {len(estado_sistema['puntos'])} puntos > límite de {config.MAX_PUNTOS_HELD_KARP}")

        if '2opt' in solicitud.algoritmos:
            print("\nEjecutando 2-Opt...")
            ruta, distancia, stats = tsp_2opt(matriz, mostrar_progreso=True)

            resultados['2opt'] = ResultadoTSP(
                algoritmo="2opt",
                ruta=ruta,
                distancia_total=distancia,
                tiempo_ejecucion=stats['tiempo_segundos'],
                num_puntos=len(estado_sistema['puntos']),
                es_optimo=False
            )

        estado_sistema['resultados_tsp'] = resultados

        comparacion = ComparacionAlgoritmos(
            fuerza_bruta=resultados.get('fuerza_bruta'),
            held_karp=resultados.get('held_karp'),
            vecino_2opt=resultados.get('2opt'),
            num_puntos=len(estado_sistema['puntos'])
        )

        return {
            "mensaje": "Algoritmos ejecutados exitosamente",
            "comparacion": comparacion.model_dump(),
            "mejor_resultado": comparacion.obtener_mejor_resultado().model_dump() if comparacion.obtener_mejor_resultado() else None,
            "mas_rapido": comparacion.obtener_mas_rapido().model_dump() if comparacion.obtener_mas_rapido() else None
        }

    except Exception as e:
        raise HTTPException(500, f"Error ejecutando algoritmos: {str(e)}")


@app.get("/api/exportar")
async def exportar_resultados(formato: str = "geojson"):
    """
    Exporta los resultados en el formato especificado.
    Soporta GeoJSON y WKT.
    """
    try:
        if not estado_sistema['resultados_tsp']:
            raise HTTPException(400, "No hay resultados para exportar")

        if formato == "geojson":
            puntos_coords = [(p.latitud, p.longitud) for p in estado_sistema['puntos']]
            puntos_nombres = [p.nombre for p in estado_sistema['puntos']]

            resultados_export = {
                alg: (res.ruta, res.distancia_total, {})
                for alg, res in estado_sistema['resultados_tsp'].items()
            }

            ruta_export = "exportacion_tsp.geojson"
            exportar_comparacion_algoritmos(
                resultados_export,
                puntos_coords,
                puntos_nombres,
                ruta_export
            )

            return FileResponse(
                ruta_export,
                media_type="application/json",
                filename="resultados_tsp.geojson"
            )

        else:
            raise HTTPException(400, f"Formato no soportado: {formato}")

    except Exception as e:
        raise HTTPException(500, f"Error exportando: {str(e)}")


@app.get("/health")
async def health_check():
    """Endpoint de health check para monitoreo"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

