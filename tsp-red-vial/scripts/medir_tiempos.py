"""
Script para medir tiempos de ejecución de algoritmos TSP.
Genera datos de rendimiento para análisis empírico en el reporte técnico.
"""

import sys
import json
import csv
from pathlib import Path
from datetime import datetime
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from dominio.tsp_fuerza_bruta import tsp_fuerza_bruta, estimar_tiempo_ejecucion
from dominio.tsp_held_karp import tsp_held_karp, estimar_recursos_held_karp
from dominio.tsp_vecino_2opt import tsp_2opt


def generar_matriz_aleatoria(n: int, seed: int = None) -> np.ndarray:
    """
    Genera una matriz de distancias aleatoria simétrica.
    Simula distancias reales entre puntos en una red.

    Args:
        n: Dimensión de la matriz
        seed: Semilla para reproducibilidad

    Returns:
        Matriz numpy NxN simétrica con diagonal de ceros
    """
    if seed is not None:
        np.random.seed(seed)

    matriz = np.random.rand(n, n) * 1000

    matriz = (matriz + matriz.T) / 2

    np.fill_diagonal(matriz, 0)

    return matriz


def medir_algoritmo(
    nombre: str,
    funcion_tsp,
    matriz: np.ndarray,
    max_tiempo: float = 300.0
) -> dict:
    """
    Mide el rendimiento de un algoritmo TSP.
    Captura tiempo de ejecución, calidad de solución y estadísticas.

    Args:
        nombre: Nombre del algoritmo
        funcion_tsp: Función del algoritmo a medir
        matriz: Matriz de distancias
        max_tiempo: Tiempo máximo permitido en segundos

    Returns:
        Diccionario con métricas de rendimiento
    """
    n = len(matriz)

    print(f"  Ejecutando {nombre}...")

    try:
        inicio = datetime.now()
        ruta, distancia, stats = funcion_tsp(matriz, mostrar_progreso=False)
        tiempo = (datetime.now() - inicio).total_seconds()

        if tiempo > max_tiempo:
            print(f"    Advertencia: Tiempo excedido ({tiempo:.2f}s)")

        resultado = {
            'algoritmo': nombre,
            'n': n,
            'tiempo_segundos': tiempo,
            'distancia': distancia,
            'ruta': ruta,
            'exito': True,
            'error': None
        }

        resultado.update(stats)

        print(f"    Completado en {tiempo:.3f}s - Distancia: {distancia:.2f}")

        return resultado

    except Exception as e:
        print(f"    Error: {str(e)}")

        return {
            'algoritmo': nombre,
            'n': n,
            'tiempo_segundos': None,
            'distancia': None,
            'ruta': None,
            'exito': False,
            'error': str(e)
        }


def medir_escalabilidad(
    tamanios: list,
    algoritmos: list,
    repeticiones: int = 3,
    seed_base: int = 42
) -> list:
    """
    Mide la escalabilidad de algoritmos con diferentes tamaños.
    Ejecuta múltiples repeticiones para obtener medidas estables.

    Args:
        tamanios: Lista de tamaños de problema a probar
        algoritmos: Lista de nombres de algoritmos
        repeticiones: Número de repeticiones por configuración
        seed_base: Semilla base para generación de matrices

    Returns:
        Lista de diccionarios con resultados de todas las mediciones
    """
    resultados = []

    for n in tamanios:
        print(f"\nProbando con {n} puntos...")

        algoritmos_ejecutar = []

        if 'fuerza_bruta' in algoritmos:
            estimacion = estimar_tiempo_ejecucion(n)
            if estimacion.get('es_factible', False):
                algoritmos_ejecutar.append('fuerza_bruta')
            else:
                print(f"  Fuerza Bruta omitido: {estimacion.get('tiempo_legible', 'muy lento')}")

        if 'held_karp' in algoritmos:
            estimacion = estimar_recursos_held_karp(n)
            if estimacion.get('es_factible', False):
                algoritmos_ejecutar.append('held_karp')
            else:
                print(f"  Held-Karp omitido: {estimacion.get('razon', 'memoria excesiva')}")

        if '2opt' in algoritmos:
            algoritmos_ejecutar.append('2opt')

        for rep in range(repeticiones):
            print(f"\n  Repetición {rep + 1}/{repeticiones}")

            matriz = generar_matriz_aleatoria(n, seed=seed_base + n * 100 + rep)

            for alg_nombre in algoritmos_ejecutar:
                if alg_nombre == 'fuerza_bruta':
                    resultado = medir_algoritmo('fuerza_bruta', tsp_fuerza_bruta, matriz)
                elif alg_nombre == 'held_karp':
                    resultado = medir_algoritmo('held_karp', tsp_held_karp, matriz)
                elif alg_nombre == '2opt':
                    resultado = medir_algoritmo('2opt', tsp_2opt, matriz)

                resultado['repeticion'] = rep + 1
                resultado['timestamp'] = datetime.now().isoformat()

                resultados.append(resultado)

    return resultados


def guardar_resultados_csv(resultados: list, ruta_salida: str) -> None:
    """
    Guarda los resultados en formato CSV para análisis.
    Incluye todas las métricas relevantes en columnas separadas.

    Args:
        resultados: Lista de diccionarios con resultados
        ruta_salida: Ruta del archivo CSV de salida
    """
    if not resultados:
        print("No hay resultados para guardar")
        return

    columnas = [
        'algoritmo', 'n', 'repeticion', 'tiempo_segundos',
        'distancia', 'exito', 'error', 'timestamp'
    ]

    with open(ruta_salida, 'w', newline='', encoding='utf-8') as f:
        escritor = csv.DictWriter(f, fieldnames=columnas, extrasaction='ignore')
        escritor.writeheader()

        for resultado in resultados:
            escritor.writerow(resultado)

    print(f"\nResultados guardados en: {ruta_salida}")


def guardar_resultados_json(resultados: list, ruta_salida: str) -> None:
    """
    Guarda los resultados en formato JSON con toda la información.
    Preserva estructuras complejas como listas de rutas.

    Args:
        resultados: Lista de diccionarios con resultados
        ruta_salida: Ruta del archivo JSON de salida
    """
    datos_json = {
        'timestamp': datetime.now().isoformat(),
        'num_mediciones': len(resultados),
        'resultados': resultados
    }

    with open(ruta_salida, 'w', encoding='utf-8') as f:
        json.dump(datos_json, f, indent=2, ensure_ascii=False, default=str)

    print(f"Resultados guardados en: {ruta_salida}")


def generar_reporte_resumen(resultados: list) -> None:
    """
    Genera un resumen estadístico de los resultados.
    Calcula promedios y desviaciones estándar por algoritmo y tamaño.

    Args:
        resultados: Lista de diccionarios con resultados
    """
    print("\n" + "="*70)
    print("RESUMEN DE RESULTADOS")
    print("="*70)

    resultados_exitosos = [r for r in resultados if r['exito']]

    if not resultados_exitosos:
        print("No hay resultados exitosos para resumir")
        return

    algoritmos = set(r['algoritmo'] for r in resultados_exitosos)
    tamanios = sorted(set(r['n'] for r in resultados_exitosos))

    for alg in sorted(algoritmos):
        print(f"\n{alg.upper()}:")
        print("-" * 70)
        print(f"{'n':<6} {'Tiempo Prom (s)':<18} {'Desv Est (s)':<15} {'Dist Prom':<15}")
        print("-" * 70)

        for n in tamanios:
            mediciones = [
                r for r in resultados_exitosos
                if r['algoritmo'] == alg and r['n'] == n
            ]

            if mediciones:
                tiempos = [m['tiempo_segundos'] for m in mediciones]
                distancias = [m['distancia'] for m in mediciones]

                tiempo_prom = np.mean(tiempos)
                tiempo_std = np.std(tiempos)
                dist_prom = np.mean(distancias)

                print(f"{n:<6} {tiempo_prom:<18.6f} {tiempo_std:<15.6f} {dist_prom:<15.2f}")


def main():
    """
    Función principal del script.
    Ejecuta mediciones y genera archivos de resultados.
    """
    print("="*70)
    print("MEDICIÓN DE RENDIMIENTO DE ALGORITMOS TSP")
    print("="*70)

    tamanios = [3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 18, 20]

    algoritmos = ['fuerza_bruta', 'held_karp', '2opt']

    repeticiones = 3

    print(f"\nConfiguración:")
    print(f"  Tamaños: {tamanios}")
    print(f"  Algoritmos: {algoritmos}")
    print(f"  Repeticiones: {repeticiones}")
    print(f"  Semilla: 42")

    input("\nPresiona Enter para comenzar las mediciones...")

    inicio_total = datetime.now()

    resultados = medir_escalabilidad(
        tamanios,
        algoritmos,
        repeticiones=repeticiones
    )

    tiempo_total = (datetime.now() - inicio_total).total_seconds()

    print(f"\n\nMediciones completadas en {tiempo_total:.2f} segundos")
    print(f"Total de mediciones: {len(resultados)}")

    directorio_salida = Path('resultados_analisis')
    directorio_salida.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    ruta_csv = directorio_salida / f'tiempos_{timestamp}.csv'
    ruta_json = directorio_salida / f'tiempos_{timestamp}.json'

    guardar_resultados_csv(resultados, str(ruta_csv))
    guardar_resultados_json(resultados, str(ruta_json))

    generar_reporte_resumen(resultados)

    print(f"\n{'='*70}")
    print("ANÁLISIS COMPLETADO")
    print(f"{'='*70}")
    print(f"\nArchivos generados:")
    print(f"  CSV:  {ruta_csv}")
    print(f"  JSON: {ruta_json}")


if __name__ == '__main__':
    main()

