"""
Servidor FastAPI para el sistema de optimización de rutas TSP.
Proporciona endpoints REST para cargar datos, ejecutar algoritmos y exportar resultados.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import csv
from pathlib import Path
from datetime import datetime
from typing import List
import json

from dominio.modelos import (
    Punto, ResultadoTSP, ComparacionAlgoritmos,
    SolicitudEvaluacion
)
from dominio.cargador_red import CargadorRedOptimizado
from dominio.rutas_mas_cortas import calcular_matriz_distancias, obtener_camino_detallado
from dominio.ajustar_puntos import integrar_multiples_puntos, validar_integracion
from dominio.tsp_fuerza_bruta import tsp_fuerza_bruta
from dominio.tsp_held_karp import tsp_held_karp
from dominio.tsp_vecino_2opt import tsp_2opt
from dominio.exportar_geo import exportar_comparacion_algoritmos, generar_geojson_comparacion
from configuracion import config

app = FastAPI(
    title=config.API_TITULO,
    version=config.API_VERSION,
    description=config.API_DESCRIPCION
)

# Configuración de CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estado global del sistema
estado_sistema = {
    'red_cargada': False,
    'puntos_cargados': False,
    'grafo': None,
    'nodos_coords': None,
    'puntos': [],
    'nodos_puntos': [],
    'resultados_tsp': {}
}


@app.get("/")
async def raiz():
    return {"nombre": config.API_TITULO, "version": config.API_VERSION}


@app.get("/api/estado")
async def obtener_estado():
    return {
        "red_cargada": estado_sistema['red_cargada'],
        "puntos_cargados": estado_sistema['puntos_cargados'],
        "num_nodos": estado_sistema['grafo'].number_of_nodes() if estado_sistema['grafo'] else 0,
        "num_aristas": estado_sistema['grafo'].number_of_edges() if estado_sistema['grafo'] else 0,
        "num_puntos": len(estado_sistema['puntos']),
        "algoritmos_ejecutados": list(estado_sistema['resultados_tsp'].keys()),
    }


@app.post("/api/cargar-red")
async def cargar_red(archivo: UploadFile = File(...)):
    if not archivo.filename.endswith('.geojson'):
        raise HTTPException(400, "El archivo debe ser GeoJSON")
    
    ruta_temporal = Path(f"temp_{archivo.filename}")
    with open(ruta_temporal, 'wb') as f:
        f.write(await archivo.read())

    cargador = CargadorRedOptimizado()
    grafo, nodos_coords = cargador.cargar_con_cache(str(ruta_temporal), forzar_recarga=False)
    
    estado_sistema.update({
        'grafo': grafo,
        'nodos_coords': nodos_coords,
        'red_cargada': True,
        'puntos_cargados': False,
        'puntos': [],
        'nodos_puntos': [],
        'resultados_tsp': {}
    })
    
    ruta_temporal.unlink()
    return {"mensaje": "Red cargada", "num_nodos": grafo.number_of_nodes(), "num_aristas": grafo.number_of_edges()}


@app.post("/api/cargar-puntos")
async def cargar_puntos(archivo: UploadFile = File(...)):
    if not estado_sistema['red_cargada']:
        raise HTTPException(400, "Primero debe cargar una red vial")
    if not archivo.filename.endswith('.csv'):
        raise HTTPException(400, "El archivo debe ser CSV")

    lineas = (await archivo.read()).decode('utf-8').splitlines()
    lector = csv.DictReader(lineas)
    puntos_data = [
        (int(f['id']), float(f['latitud']), float(f['longitud']), f.get('nombre', f"Punto {f['id']}"))
        for f in lector
    ]

    if len(puntos_data) < 2:
        raise HTTPException(400, "Se necesitan al menos 2 puntos")

    resultados_integracion = integrar_multiples_puntos(
        estado_sistema['grafo'],
        estado_sistema['nodos_coords'],
        puntos_data
    )
    
    estado_sistema['puntos'] = [Punto(id=p[0], latitud=p[1], longitud=p[2], nombre=p[3]) for p in puntos_data]
    estado_sistema['nodos_puntos'] = [resultados_integracion[p[0]][0] for p in puntos_data]
    estado_sistema['puntos_cargados'] = True

    return {"mensaje": "Puntos integrados", "num_puntos": len(puntos_data), "puntos": estado_sistema['puntos']}


@app.post("/api/evaluar-algoritmos")
async def evaluar_algoritmos(solicitud: SolicitudEvaluacion):
    if not estado_sistema['puntos_cargados']:
        raise HTTPException(400, "Primero debe cargar puntos")

    num_puntos_actual = len(estado_sistema['puntos'])
    matriz = calcular_matriz_distancias(
        estado_sistema['grafo'],
        [p.model_dump() for p in estado_sistema['puntos']],
        estado_sistema['nodos_coords'],
        estado_sistema['nodos_puntos']
    )
    
    resultados = {}
    if 'fuerza_bruta' in solicitud.algoritmos and num_puntos_actual <= config.MAX_PUNTOS_FUERZA_BRUTA:
        ruta, dist, stats = tsp_fuerza_bruta(matriz)
        resultados['fuerza_bruta'] = ResultadoTSP(algoritmo="fuerza_bruta", ruta=ruta, distancia_total=dist, tiempo_ejecucion=stats['tiempo_segundos'], es_optimo=True, num_puntos=num_puntos_actual)
    
    if 'held_karp' in solicitud.algoritmos and num_puntos_actual <= config.MAX_PUNTOS_HELD_KARP:
        ruta, dist, stats = tsp_held_karp(matriz)
        resultados['held_karp'] = ResultadoTSP(algoritmo="held_karp", ruta=ruta, distancia_total=dist, tiempo_ejecucion=stats['tiempo_segundos'], es_optimo=True, num_puntos=num_puntos_actual)

    if '2opt' in solicitud.algoritmos:
        ruta, dist, stats = tsp_2opt(matriz)
        resultados['2opt'] = ResultadoTSP(algoritmo="2opt", ruta=ruta, distancia_total=dist, tiempo_ejecucion=stats['tiempo_segundos'], es_optimo=False, num_puntos=num_puntos_actual)

    estado_sistema['resultados_tsp'] = resultados
    # CORRECCIÓN: Añadir el campo 'num_puntos' requerido
    comparacion = ComparacionAlgoritmos(
        fuerza_bruta=resultados.get('fuerza_bruta'), 
        held_karp=resultados.get('held_karp'), 
        vecino_2opt=resultados.get('2opt'),
        num_puntos=num_puntos_actual
    )
    
    return {"mensaje": "Algoritmos ejecutados", "comparacion": comparacion}


@app.get("/api/ruta-detallada")
async def api_obtener_ruta_detallada(
    punto_idx_origen: int = Query(..., ge=0),
    punto_idx_destino: int = Query(..., ge=0)
):
    if not estado_sistema['puntos_cargados']:
        raise HTTPException(400, "No hay puntos cargados.")
    
    try:
        nodo_origen = estado_sistema['nodos_puntos'][punto_idx_origen]
        nodo_destino = estado_sistema['nodos_puntos'][punto_idx_destino]

        resultado = obtener_camino_detallado(
            estado_sistema['grafo'],
            nodo_origen,
            nodo_destino,
            estado_sistema['nodos_coords']
        )
        
        camino_coords = [seg['coords_desde'] for seg in resultado['segmentos']]
        if resultado['segmentos']:
            camino_coords.append(resultado['segmentos'][-1]['coords_hacia'])

        return {
            "distancia_total": resultado['distancia_total'],
            "camino_coords": camino_coords
        }
    except IndexError:
        raise HTTPException(404, f"Índice de punto fuera de rango.")
    except Exception as e:
        raise HTTPException(500, f"No se pudo calcular la ruta detallada: {e}")


@app.get("/api/exportar")
async def exportar_resultados(formato: str = Query(default='geojson', regex='^(geojson|json)$')):
    """
    Exporta los resultados de los algoritmos TSP ejecutados en formato GeoJSON.
    
    Args:
        formato: Formato de exportación ('geojson' o 'json')
    
    Returns:
        Archivo GeoJSON con las rutas de todos los algoritmos ejecutados
    """
    if not estado_sistema['puntos_cargados']:
        raise HTTPException(400, "Primero debe cargar puntos")
    
    if len(estado_sistema['resultados_tsp']) == 0:
        raise HTTPException(400, "No hay resultados de algoritmos para exportar. Ejecute los algoritmos primero.")
    
    # Preparar datos para la exportación
    puntos_coords = [(p.latitud, p.longitud) for p in estado_sistema['puntos']]
    puntos_nombres = [p.nombre for p in estado_sistema['puntos']]
    
    # Generar GeoJSON combinado
    geojson = generar_geojson_comparacion(
        estado_sistema['resultados_tsp'],
        puntos_coords,
        puntos_nombres,
        estado_sistema['grafo'],
        estado_sistema['nodos_puntos'],
        estado_sistema['nodos_coords']
    )
    
    # Convertir a JSON string con codificación UTF-8
    geojson_str = json.dumps(geojson, indent=2, ensure_ascii=False)
    geojson_bytes = geojson_str.encode('utf-8')
    
    # Devolver como respuesta con el tipo de contenido apropiado
    return Response(
        content=geojson_bytes,
        media_type="application/geo+json" if formato == 'geojson' else "application/json",
        headers={
            "Content-Disposition": f'attachment; filename="resultados_tsp_{datetime.now().strftime("%Y%m%d_%H%M%S")}.geojson"'
        }
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
