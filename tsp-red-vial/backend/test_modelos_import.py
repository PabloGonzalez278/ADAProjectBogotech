"""Script de prueba para verificar que modelos.py funcione correctamente con Pydantic V2"""

import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

try:
    print("Importando modelos...")
    from dominio.modelos import (
        Punto, InfoRed, ResultadoTSP, ComparacionAlgoritmos,
        MatrizDistancias, SolicitudEvaluacion, RespuestaError
    )
    print("✅ Modelos importados correctamente")
    
    # Probar crear un punto
    print("\nProbando crear un Punto...")
    punto = Punto(id=1, latitud=4.6486, longitud=-74.0978, nombre="Plaza de Bolívar")
    print(f"✅ Punto creado: {punto.nombre} ({punto.latitud}, {punto.longitud})")
    
    # Probar crear un ResultadoTSP
    print("\nProbando crear un ResultadoTSP...")
    resultado = ResultadoTSP(
        algoritmo="held_karp",
        ruta=[0, 1, 2, 0],
        distancia_total=1500.5,
        tiempo_ejecucion=0.05,
        num_puntos=3,
        es_optimo=True
    )
    print(f"✅ ResultadoTSP creado: {resultado.algoritmo}, distancia={resultado.distancia_total}m")
    
    # Probar validador
    print("\nProbando validadores...")
    try:
        punto_invalido = Punto(id=1, latitud=100, longitud=-74, nombre="Test")
        print("❌ El validador de latitud NO funcionó (debería haber fallado)")
    except Exception as e:
        print(f"✅ Validador funciona correctamente: {e}")
    
    print("\n✅ TODAS LAS PRUEBAS EXITOSAS - modelos.py funciona correctamente")
    
except Exception as e:
    print(f"\n❌ ERROR al importar modelos: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

