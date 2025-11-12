"""
Script para generar datos sintéticos para análisis de rendimiento.
Crea puntos aleatorios dentro del área de una red vial para pruebas.
"""

import argparse
import csv
import random
from pathlib import Path
from typing import Tuple, List


def generar_puntos_aleatorios(
    num_puntos: int,
    lat_min: float,
    lat_max: float,
    lon_min: float,
    lon_max: float,
    seed: int = None
) -> List[Tuple[int, float, float, str]]:
    """
    Genera puntos aleatorios dentro de un área geográfica.
    Distribuye los puntos uniformemente en el bounding box especificado.

    Args:
        num_puntos: Cantidad de puntos a generar
        lat_min: Latitud mínima del área
        lat_max: Latitud máxima del área
        lon_min: Longitud mínima del área
        lon_max: Longitud máxima del área
        seed: Semilla para reproducibilidad

    Returns:
        Lista de tuplas (id, latitud, longitud, nombre)
    """
    if seed is not None:
        random.seed(seed)

    puntos = []

    for i in range(num_puntos):
        lat = random.uniform(lat_min, lat_max)
        lon = random.uniform(lon_min, lon_max)
        nombre = f"Punto_{i+1}"

        puntos.append((i + 1, lat, lon, nombre))

    return puntos


def guardar_puntos_csv(puntos: List[Tuple], ruta_salida: str) -> None:
    """
    Guarda los puntos generados en un archivo CSV.
    Utiliza el formato estándar del sistema: id,latitud,longitud,nombre.

    Args:
        puntos: Lista de tuplas (id, lat, lon, nombre)
        ruta_salida: Ruta del archivo de salida
    """
    with open(ruta_salida, 'w', newline='', encoding='utf-8') as f:
        escritor = csv.writer(f)
        escritor.writerow(['id', 'latitud', 'longitud', 'nombre'])

        for punto in puntos:
            escritor.writerow(punto)


def generar_serie_datasets(
    tamanios: List[int],
    directorio_salida: str,
    bbox: dict,
    seed: int = 42
) -> None:
    """
    Genera múltiples datasets de diferentes tamaños.
    Útil para análisis de escalabilidad de algoritmos.

    Args:
        tamanios: Lista de tamaños de datasets a generar
        directorio_salida: Directorio donde guardar los archivos
        bbox: Diccionario con lat_min, lat_max, lon_min, lon_max
        seed: Semilla para reproducibilidad
    """
    Path(directorio_salida).mkdir(parents=True, exist_ok=True)

    for tamanio in tamanios:
        print(f"Generando dataset de {tamanio} puntos...")

        puntos = generar_puntos_aleatorios(
            tamanio,
            bbox['lat_min'],
            bbox['lat_max'],
            bbox['lon_min'],
            bbox['lon_max'],
            seed=seed + tamanio
        )

        nombre_archivo = f"puntos_{tamanio}.csv"
        ruta_salida = Path(directorio_salida) / nombre_archivo

        guardar_puntos_csv(puntos, str(ruta_salida))

        print(f"  Guardado: {ruta_salida}")


def main():
    """
    Función principal del script.
    Procesa argumentos de línea de comandos y genera los datasets.
    """
    parser = argparse.ArgumentParser(
        description='Genera puntos sintéticos para pruebas de TSP'
    )

    parser.add_argument(
        '--num-puntos',
        type=int,
        default=10,
        help='Número de puntos a generar (default: 10)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='datos/puntos_sinteticos.csv',
        help='Archivo de salida (default: datos/puntos_sinteticos.csv)'
    )

    parser.add_argument(
        '--lat-min',
        type=float,
        default=4.60,
        help='Latitud mínima (default: 4.60 - Bogotá)'
    )

    parser.add_argument(
        '--lat-max',
        type=float,
        default=4.70,
        help='Latitud máxima (default: 4.70 - Bogotá)'
    )

    parser.add_argument(
        '--lon-min',
        type=float,
        default=-74.10,
        help='Longitud mínima (default: -74.10 - Bogotá)'
    )

    parser.add_argument(
        '--lon-max',
        type=float,
        default=-74.05,
        help='Longitud máxima (default: -74.05 - Bogotá)'
    )

    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Semilla aleatoria (default: 42)'
    )

    parser.add_argument(
        '--serie',
        action='store_true',
        help='Generar serie de datasets de diferentes tamaños'
    )

    parser.add_argument(
        '--tamanios',
        type=str,
        default='5,10,15,20,25',
        help='Tamaños para serie (separados por comas, default: 5,10,15,20,25)'
    )

    args = parser.parse_args()

    if args.serie:
        tamanios = [int(x.strip()) for x in args.tamanios.split(',')]

        bbox = {
            'lat_min': args.lat_min,
            'lat_max': args.lat_max,
            'lon_min': args.lon_min,
            'lon_max': args.lon_max
        }

        directorio = Path(args.output).parent

        print("\nGenerando serie de datasets...")
        print(f"Tamaños: {tamanios}")
        print(f"Área: Lat [{args.lat_min}, {args.lat_max}], Lon [{args.lon_min}, {args.lon_max}]")
        print(f"Directorio: {directorio}\n")

        generar_serie_datasets(tamanios, str(directorio), bbox, args.seed)

        print(f"\nSerie completada: {len(tamanios)} datasets generados")

    else:
        print("\nGenerando dataset individual...")
        print(f"Puntos: {args.num_puntos}")
        print(f"Área: Lat [{args.lat_min}, {args.lat_max}], Lon [{args.lon_min}, {args.lon_max}]")
        print(f"Salida: {args.output}\n")

        puntos = generar_puntos_aleatorios(
            args.num_puntos,
            args.lat_min,
            args.lat_max,
            args.lon_min,
            args.lon_max,
            args.seed
        )

        guardar_puntos_csv(puntos, args.output)

        print(f"Dataset guardado: {args.output}")
        print(f"Puntos generados: {len(puntos)}")


if __name__ == '__main__':
    main()

