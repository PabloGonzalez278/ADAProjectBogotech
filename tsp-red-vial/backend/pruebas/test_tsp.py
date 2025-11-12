"""
Pruebas unitarias para los algoritmos TSP.
Verifica la correctitud y rendimiento de fuerza bruta, Held-Karp y 2-Opt.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import numpy as np
from dominio.tsp_fuerza_bruta import tsp_fuerza_bruta, calcular_distancia_ruta, verificar_solucion
from dominio.tsp_held_karp import tsp_held_karp
from dominio.tsp_vecino_2opt import tsp_2opt


class TestFuerzaBruta:
    """
    Pruebas para el algoritmo de fuerza bruta.
    Verifica que encuentre la solución óptima y maneje casos límite.
    """

    def test_caso_simple_3_puntos(self):
        """Prueba con 3 puntos en triángulo equilátero"""
        matriz = np.array([
            [0, 10, 10],
            [10, 0, 10],
            [10, 10, 0]
        ])

        ruta, distancia, stats = tsp_fuerza_bruta(matriz)

        assert len(ruta) == 4
        assert ruta[0] == 0
        assert ruta[-1] == 0
        assert distancia == 30.0
        assert stats['permutaciones_evaluadas'] > 0

    def test_caso_4_puntos(self):
        """Prueba con 4 puntos formando cuadrado"""
        matriz = np.array([
            [0, 1, 2, 1],
            [1, 0, 1, 2],
            [2, 1, 0, 1],
            [1, 2, 1, 0]
        ])

        ruta, distancia, stats = tsp_fuerza_bruta(matriz)

        assert len(ruta) == 5
        assert ruta[0] == 0
        assert ruta[-1] == 0
        assert distancia == 4.0

    def test_matriz_asimetrica(self):
        """Verifica que funcione con matrices asimétricas"""
        matriz = np.array([
            [0, 5, 10],
            [8, 0, 3],
            [12, 7, 0]
        ])

        ruta, distancia, _ = tsp_fuerza_bruta(matriz)

        assert len(ruta) == 4
        assert isinstance(distancia, float)

    def test_error_matriz_muy_grande(self):
        """Verifica que rechace matrices demasiado grandes"""
        matriz = np.random.rand(15, 15)

        with pytest.raises(ValueError, match="no es práctico"):
            tsp_fuerza_bruta(matriz)

    def test_error_pocos_puntos(self):
        """Verifica que rechace menos de 2 puntos"""
        matriz = np.array([[0]])

        with pytest.raises(ValueError, match="al menos 2 puntos"):
            tsp_fuerza_bruta(matriz)

    def test_verificar_solucion_valida(self):
        """Verifica que la validación acepte soluciones correctas"""
        matriz = np.array([
            [0, 1, 2],
            [1, 0, 1],
            [2, 1, 0]
        ])
        ruta = [0, 1, 2, 0]

        es_valida, errores = verificar_solucion(ruta, matriz)

        assert es_valida
        assert len(errores) == 0

    def test_verificar_solucion_invalida(self):
        """Verifica que la validación rechace soluciones incorrectas"""
        matriz = np.array([
            [0, 1, 2],
            [1, 0, 1],
            [2, 1, 0]
        ])
        ruta = [0, 1, 1, 0]

        es_valida, errores = verificar_solucion(ruta, matriz)

        assert not es_valida
        assert len(errores) > 0


class TestHeldKarp:
    """
    Pruebas para el algoritmo de Held-Karp.
    Verifica que encuentre la solución óptima con programación dinámica.
    """

    def test_caso_simple_3_puntos(self):
        """Prueba con 3 puntos"""
        matriz = np.array([
            [0, 10, 15],
            [10, 0, 20],
            [15, 20, 0]
        ])

        ruta, distancia, stats = tsp_held_karp(matriz)

        assert len(ruta) == 4
        assert ruta[0] == 0
        assert ruta[-1] == 0
        assert distancia == 45.0

    def test_comparacion_con_fuerza_bruta(self):
        """Verifica que Held-Karp dé mismo resultado que fuerza bruta"""
        matriz = np.array([
            [0, 2, 9, 10],
            [1, 0, 6, 4],
            [15, 7, 0, 8],
            [6, 3, 12, 0]
        ])

        ruta_fb, dist_fb, _ = tsp_fuerza_bruta(matriz)
        ruta_hk, dist_hk, _ = tsp_held_karp(matriz)

        assert abs(dist_fb - dist_hk) < 0.01

    def test_caso_5_puntos(self):
        """Prueba con 5 puntos"""
        np.random.seed(42)
        matriz = np.random.rand(5, 5) * 100
        np.fill_diagonal(matriz, 0)

        ruta, distancia, stats = tsp_held_karp(matriz)

        assert len(ruta) == 6
        assert ruta[0] == 0
        assert ruta[-1] == 0
        assert stats['subproblemas_resueltos'] > 0

    def test_error_matriz_muy_grande(self):
        """Verifica que rechace matrices demasiado grandes"""
        matriz = np.random.rand(25, 25)

        with pytest.raises(ValueError, match="no es práctico"):
            tsp_held_karp(matriz)


class TestVecino2Opt:
    """
    Pruebas para el algoritmo 2-Opt.
    Verifica que encuentre soluciones razonables y mejore la solución inicial.
    """

    def test_caso_simple_3_puntos(self):
        """Prueba con 3 puntos"""
        matriz = np.array([
            [0, 10, 15],
            [10, 0, 20],
            [15, 20, 0]
        ])

        ruta, distancia, stats = tsp_2opt(matriz)

        assert len(ruta) == 4
        assert ruta[0] == 0
        assert ruta[-1] == 0
        assert distancia > 0

    def test_mejora_solucion_inicial(self):
        """Verifica que 2-Opt mejore la solución inicial"""
        matriz = np.array([
            [0, 1, 4, 2],
            [1, 0, 3, 5],
            [4, 3, 0, 1],
            [2, 5, 1, 0]
        ])

        ruta, distancia, stats = tsp_2opt(matriz)

        assert stats['mejora_porcentual'] >= 0

    def test_caso_grande_10_puntos(self):
        """Prueba con 10 puntos para verificar escalabilidad"""
        np.random.seed(42)
        matriz = np.random.rand(10, 10) * 100
        np.fill_diagonal(matriz, 0)

        ruta, distancia, stats = tsp_2opt(matriz)

        assert len(ruta) == 11
        assert ruta[0] == 0
        assert ruta[-1] == 0
        assert stats['tiempo_segundos'] < 5.0

    def test_caso_muy_grande_50_puntos(self):
        """Prueba con 50 puntos para verificar que funcione con casos grandes"""
        np.random.seed(42)
        matriz = np.random.rand(50, 50) * 100
        np.fill_diagonal(matriz, 0)

        ruta, distancia, stats = tsp_2opt(matriz)

        assert len(ruta) == 51
        assert stats['tiempo_segundos'] < 30.0


class TestCalculoDistancia:
    """
    Pruebas para el cálculo de distancias de rutas.
    Verifica que el cálculo sea correcto.
    """

    def test_distancia_simple(self):
        """Prueba cálculo de distancia en ruta simple"""
        matriz = np.array([
            [0, 5, 10],
            [5, 0, 3],
            [10, 3, 0]
        ])
        ruta = [0, 1, 2, 0]

        distancia = calcular_distancia_ruta(ruta, matriz)

        assert distancia == 18.0

    def test_distancia_ruta_inversa(self):
        """Verifica que rutas inversas puedan tener distancias diferentes"""
        matriz = np.array([
            [0, 5, 10],
            [8, 0, 3],
            [12, 7, 0]
        ])

        ruta1 = [0, 1, 2, 0]
        ruta2 = [0, 2, 1, 0]

        dist1 = calcular_distancia_ruta(ruta1, matriz)
        dist2 = calcular_distancia_ruta(ruta2, matriz)

        assert dist1 != dist2


class TestComparacionAlgoritmos:
    """
    Pruebas comparativas entre algoritmos.
    Verifica propiedades de optimalidad y rendimiento.
    """

    def test_optimalidad_fuerza_bruta_vs_held_karp(self):
        """Verifica que ambos algoritmos óptimos den mismo resultado"""
        matriz = np.array([
            [0, 29, 20, 21],
            [29, 0, 15, 17],
            [20, 15, 0, 28],
            [21, 17, 28, 0]
        ])

        _, dist_fb, _ = tsp_fuerza_bruta(matriz)
        _, dist_hk, _ = tsp_held_karp(matriz)

        assert abs(dist_fb - dist_hk) < 0.01

    def test_2opt_vs_optimo(self):
        """Verifica que 2-Opt encuentre solución cercana al óptimo"""
        matriz = np.array([
            [0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0]
        ])

        _, dist_optimo, _ = tsp_held_karp(matriz)
        _, dist_2opt, _ = tsp_2opt(matriz)

        diferencia_porcentual = abs(dist_2opt - dist_optimo) / dist_optimo * 100

        assert diferencia_porcentual < 20.0

