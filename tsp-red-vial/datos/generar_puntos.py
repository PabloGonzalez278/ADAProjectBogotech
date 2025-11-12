"""
Script para generar archivos CSV con puntos de interés en Bogotá
"""
import os

# Ruta base
base_path = r"C:\Users\mesas\PycharmProjects\algoritmos proyecto\ADAProjectBogotech\tsp-red-vial\datos"

# Puntos de ejemplo (5 puntos - cerca de la Javeriana)
puntos_ejemplo = """id,latitud,longitud,nombre
1,4.6286,-74.0645,Universidad Javeriana
2,4.6350,-74.0629,Parque Nacional
3,4.6397,-74.0557,Centro Comercial Andino
4,4.6320,-74.0710,Museo Nacional
5,4.6250,-74.0680,Planetario de Bogota
"""

# Puntos de 10 (incluye la Javeriana y alrededores)
puntos_10 = """id,latitud,longitud,nombre
1,4.6286,-74.0645,Universidad Javeriana
2,4.6350,-74.0629,Parque Nacional Olaya Herrera
3,4.6397,-74.0557,Centro Comercial Andino
4,4.6320,-74.0710,Museo Nacional de Colombia
5,4.6250,-74.0680,Planetario de Bogota
6,4.6097,-74.0817,Monserrate
7,4.6534,-74.0836,Plaza de Bolivar
8,4.6181,-74.0653,Barrio La Candelaria
9,4.6392,-74.0931,Parque Simon Bolivar
10,4.6682,-74.0559,Parque de la 93
"""

# Puntos de 15
puntos_15 = """id,latitud,longitud,nombre
1,4.6286,-74.0645,Universidad Javeriana
2,4.6350,-74.0629,Parque Nacional Olaya Herrera
3,4.6397,-74.0557,Centro Comercial Andino
4,4.6320,-74.0710,Museo Nacional de Colombia
5,4.6250,-74.0680,Planetario de Bogota
6,4.6097,-74.0817,Monserrate
7,4.6534,-74.0836,Plaza de Bolivar
8,4.6181,-74.0653,Barrio La Candelaria
9,4.6392,-74.0931,Parque Simon Bolivar
10,4.6682,-74.0559,Parque de la 93
11,4.7110,-74.0721,Centro Comercial Unicentro
12,4.5981,-74.0758,Zona Rosa - Zona T
13,4.6760,-74.0480,Chapinero Alto
14,4.6486,-74.1028,Biblioteca Virgilio Barco
15,4.6011,-74.0660,Teatro Colon
"""

# Zona Javeriana (8 puntos)
puntos_zona_javeriana = """id,latitud,longitud,nombre
1,4.6286,-74.0645,Universidad Javeriana
2,4.6283,-74.0632,Hospital San Ignacio
3,4.6298,-74.0670,Colegio San Bartolome
4,4.6310,-74.0625,Estadio Nemesio Camacho El Campin
5,4.6350,-74.0629,Parque Nacional
6,4.6320,-74.0710,Museo Nacional
7,4.6397,-74.0557,Centro Comercial Andino
8,4.6420,-74.0640,Torre Colpatria
"""

# Centro Histórico
puntos_centro_historico = """id,latitud,longitud,nombre
1,4.6534,-74.0836,Plaza de Bolivar
2,4.6533,-74.0730,Capitolio Nacional
3,4.6181,-74.0653,Museo Botero
4,4.5967,-74.0758,Casa de Narino
5,4.6011,-74.0660,Teatro Colon
6,4.5982,-74.0816,Iglesia de Monserrate Base
7,4.6097,-74.0817,Teleferico Monserrate
8,4.6145,-74.0702,Chorro de Quevedo
9,4.5989,-74.0751,Palacio de Justicia
10,4.6025,-74.0735,Museo del Oro
"""

# Zona Norte
puntos_zona_norte = """id,latitud,longitud,nombre
1,4.6682,-74.0559,Parque de la 93
2,4.6638,-74.0546,Centro Comercial El Retiro
3,4.6710,-74.0489,Usaquen Centro
4,4.6760,-74.0480,Iglesia de Usaquen
5,4.6830,-74.0550,Hacienda Santa Barbara
6,4.6920,-74.0380,Unicentro Bogota
7,4.7110,-74.0721,Country Club
8,4.6595,-74.0524,Parque El Virrey
"""

# Ruta de Museos
puntos_ruta_museos = """id,latitud,longitud,nombre
1,4.6320,-74.0710,Museo Nacional de Colombia
2,4.6181,-74.0653,Museo Botero
3,4.6025,-74.0735,Museo del Oro
4,4.6350,-74.0629,Museo de Arte Moderno
5,4.6250,-74.0680,Planetario de Bogota
6,4.6011,-74.0660,Museo de Arte Colonial
7,4.6145,-74.0702,Museo de Bogota
8,4.6420,-74.0640,Museo de Arte del Banco de la Republica
9,4.6392,-74.0931,Biblioteca Nacional
10,4.6486,-74.1028,Biblioteca Virgilio Barco
"""

# Escribir archivos
archivos = {
    "puntos_ejemplo.csv": puntos_ejemplo,
    "puntos_10.csv": puntos_10,
    "puntos_15.csv": puntos_15,
    "puntos_zona_javeriana.csv": puntos_zona_javeriana,
    "puntos_centro_historico.csv": puntos_centro_historico,
    "puntos_zona_norte.csv": puntos_zona_norte,
    "puntos_ruta_museos.csv": puntos_ruta_museos
}

for nombre_archivo, contenido in archivos.items():
    ruta_completa = os.path.join(base_path, nombre_archivo)
    with open(ruta_completa, 'w', encoding='utf-8') as f:
        f.write(contenido.strip())
    print(f"✓ Creado: {nombre_archivo}")

print(f"\n✅ {len(archivos)} archivos CSV creados exitosamente en: {base_path}")
print("\nArchivos disponibles:")
for nombre in archivos.keys():
    print(f"  - {nombre}")

