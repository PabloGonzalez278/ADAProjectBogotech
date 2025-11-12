"""
Script para descargar la red vial de Bogotá desde OpenStreetMap
Usa la biblioteca OSMnx para obtener datos reales y completos.

INSTALACIÓN:
    pip install osmnx

USO:
    python descargar_red_bogota.py

SALIDA:
    - datos/bogota_completa.geojson (red vial completa)
    - datos/bogota_centro.geojson (solo centro)
    - datos/bogota_localidad.geojson (una localidad específica)
"""

import osmnx as ox
import json
import sys
from pathlib import Path

# Configuración de OSMnx
ox.settings.log_console = True
ox.settings.use_cache = True


def descargar_red_bogota_completa():
    """
    Descarga la red vial de TODO Bogotá.
    ADVERTENCIA: Es GRANDE (~50,000 nodos, ~100,000 aristas)
    Puede tardar 5-10 minutos y ocupar ~50 MB.
    """
    print("🌍 Descargando red vial de Bogotá completa...")
    print("⏱️ Esto puede tardar 5-10 minutos...")

    try:
        # Descargar red de toda la ciudad
        red = ox.graph_from_place(
            "Bogotá, Colombia",
            network_type='drive',  # Solo calles para vehículos
            simplify=True
        )

        print(f"✅ Descarga exitosa!")
        print(f"📊 Nodos: {len(red.nodes)}")
        print(f"📊 Aristas: {len(red.edges)}")

        # Guardar como GeoJSON
        output_path = Path(__file__).parent.parent / "datos" / "bogota_completa.geojson"
        ox.save_graph_geopackage(red, filepath=str(output_path).replace('.geojson', '.gpkg'))

        # Convertir a GeoJSON
        gdf_edges = ox.graph_to_gdfs(red, nodes=False, edges=True)
        gdf_edges.to_file(output_path, driver='GeoJSON')

        print(f"💾 Guardado en: {output_path}")
        return red

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def descargar_red_bogota_centro():
    """
    Descarga solo el centro de Bogotá (más manejable).
    Área: ~5 km² alrededor del centro histórico
    """
    print("🏛️ Descargando red del centro de Bogotá...")

    try:
        # Centro de Bogotá (Plaza de Bolívar)
        punto_central = (4.5981, -74.0758)  # (lat, lon)
        distancia = 2500  # 2.5 km de radio

        red = ox.graph_from_point(
            punto_central,
            dist=distancia,
            network_type='drive',
            simplify=True
        )

        print(f"✅ Descarga exitosa!")
        print(f"📊 Nodos: {len(red.nodes)}")
        print(f"📊 Aristas: {len(red.edges)}")

        # Guardar como GeoJSON
        output_path = Path(__file__).parent.parent / "datos" / "bogota_centro.geojson"
        gdf_edges = ox.graph_to_gdfs(red, nodes=False, edges=True)
        gdf_edges.to_file(output_path, driver='GeoJSON')

        print(f"💾 Guardado en: {output_path}")
        return red

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def descargar_red_por_localidad(nombre_localidad="Chapinero"):
    """
    Descarga la red de una localidad específica de Bogotá.

    Localidades disponibles:
    - Usaquén, Chapinero, Santa Fe, San Cristóbal, Usme, Tunjuelito,
    - Bosa, Kennedy, Fontibón, Engativá, Suba, Barrios Unidos,
    - Teusaquillo, Los Mártires, Antonio Nariño, Puente Aranda,
    - La Candelaria, Rafael Uribe Uribe, Ciudad Bolívar, Sumapaz
    """
    print(f"📍 Descargando red de la localidad: {nombre_localidad}...")

    try:
        query = f"{nombre_localidad}, Bogotá, Colombia"

        red = ox.graph_from_place(
            query,
            network_type='drive',
            simplify=True
        )

        print(f"✅ Descarga exitosa!")
        print(f"📊 Nodos: {len(red.nodes)}")
        print(f"📊 Aristas: {len(red.edges)}")

        # Guardar como GeoJSON
        nombre_archivo = nombre_localidad.lower().replace(" ", "_")
        output_path = Path(__file__).parent.parent / "datos" / f"bogota_{nombre_archivo}.geojson"
        gdf_edges = ox.graph_to_gdfs(red, nodes=False, edges=True)
        gdf_edges.to_file(output_path, driver='GeoJSON')

        print(f"💾 Guardado en: {output_path}")
        return red

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"💡 Intenta con otra localidad o verifica el nombre")
        return None


def descargar_red_bbox(norte, sur, este, oeste):
    """
    Descarga red dentro de un bounding box específico.

    Args:
        norte: latitud norte (ej: 4.70)
        sur: latitud sur (ej: 4.55)
        este: longitud este (ej: -74.05)
        oeste: longitud oeste (ej: -74.15)
    """
    print(f"📦 Descargando red en área específica...")
    print(f"   Norte: {norte}, Sur: {sur}")
    print(f"   Este: {este}, Oeste: {oeste}")

    try:
        red = ox.graph_from_bbox(
            north=norte,
            south=sur,
            east=este,
            west=oeste,
            network_type='drive',
            simplify=True
        )

        print(f"✅ Descarga exitosa!")
        print(f"📊 Nodos: {len(red.nodes)}")
        print(f"📊 Aristas: {len(red.edges)}")

        # Guardar como GeoJSON
        output_path = Path(__file__).parent.parent / "datos" / "bogota_bbox.geojson"
        gdf_edges = ox.graph_to_gdfs(red, nodes=False, edges=True)
        gdf_edges.to_file(output_path, driver='GeoJSON')

        print(f"💾 Guardado en: {output_path}")
        return red

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def menu_interactivo():
    """Menú interactivo para seleccionar qué descargar"""
    print("\n" + "="*60)
    print("🗺️  DESCARGADOR DE RED VIAL DE BOGOTÁ")
    print("="*60)
    print("\nOpciones:")
    print("1. Bogotá COMPLETA (⚠️  grande, ~5-10 min)")
    print("2. Centro de Bogotá (recomendado, ~1-2 min)")
    print("3. Localidad específica (~1-3 min)")
    print("4. Área personalizada (bbox)")
    print("5. Salir")
    print()

    opcion = input("Selecciona una opción (1-5): ").strip()

    if opcion == "1":
        descargar_red_bogota_completa()
    elif opcion == "2":
        descargar_red_bogota_centro()
    elif opcion == "3":
        print("\nLocalidades disponibles:")
        print("- Chapinero, Usaquén, Santa Fe, La Candelaria")
        print("- Kennedy, Suba, Engativá, Fontibón, etc.")
        localidad = input("\nNombre de la localidad: ").strip()
        descargar_red_por_localidad(localidad)
    elif opcion == "4":
        print("\nIngresa las coordenadas del área:")
        norte = float(input("Latitud norte (ej: 4.70): "))
        sur = float(input("Latitud sur (ej: 4.55): "))
        este = float(input("Longitud este (ej: -74.05): "))
        oeste = float(input("Longitud oeste (ej: -74.15): "))
        descargar_red_bbox(norte, sur, este, oeste)
    elif opcion == "5":
        print("👋 ¡Hasta luego!")
        sys.exit(0)
    else:
        print("❌ Opción inválida")


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║  DESCARGADOR DE RED VIAL DE BOGOTÁ                         ║
    ║  Powered by OpenStreetMap + OSMnx                          ║
    ╚════════════════════════════════════════════════════════════╝
    
    Este script descarga datos REALES de OpenStreetMap.
    
    IMPORTANTE:
    - Necesitas conexión a internet
    - La descarga puede tardar varios minutos
    - Los archivos pueden ser grandes (MB)
    
    INSTALACIÓN:
    pip install osmnx
    """)

    # Verificar que OSMnx esté instalado
    try:
        import osmnx
        print("✅ OSMnx está instalado correctamente\n")
    except ImportError:
        print("❌ ERROR: OSMnx no está instalado")
        print("📦 Instala con: pip install osmnx")
        sys.exit(1)

    menu_interactivo()

