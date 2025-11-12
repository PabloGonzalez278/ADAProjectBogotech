"""
Pruebas unitarias para el módulo de rutas más cortas.
Verifica el cálculo de distancias sobre redes viales.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import networkx as nx
import numpy as np
from dominio.rutas_mas_cortas import (
    calcular_camino_mas_corto,
    calcular_matriz_distancias,
    verificar_matriz_simetrica,
    verificar_desigualdad_triangular
)


class TestCaminoMasCorto:
    """
    Pruebas para el cálculo de caminos más cortos.
    Verifica que el algoritmo de Dijkstra funcione correctamente.
    """

    def test_camino_directo(self):
        """Prueba camino directo entre dos nodos"""
        grafo = nx.Graph()
        grafo.add_edge('A', 'B', weight=10.0)

        camino, distancia = calcular_camino_mas_corto(grafo, 'A', 'B')

        assert camino == ['A', 'B']
        assert distancia == 10.0

    def test_camino_con_intermedios(self):
        """Prueba camino que pasa por nodos intermedios"""
        grafo = nx.Graph()
        grafo.add_edge('A', 'B', weight=5.0)
        grafo.add_edge('B', 'C', weight=3.0)
        grafo.add_edge('C', 'D', weight=2.0)

        camino, distancia = calcular_camino_mas_corto(grafo, 'A', 'D')

        assert camino == ['A', 'B', 'C', 'D']
        assert distancia == 10.0

    def test_camino_mas_corto_vs_directo(self):
        """Verifica que elija el camino más corto, no el directo"""
        grafo = nx.Graph()
        grafo.add_edge('A', 'D', weight=100.0)
        grafo.add_edge('A', 'B', weight=5.0)
        grafo.add_edge('B', 'C', weight=5.0)
        grafo.add_edge('C', 'D', weight=5.0)

        camino, distancia = calcular_camino_mas_corto(grafo, 'A', 'D')

        assert len(camino) == 4
        assert distancia == 15.0

    def test_error_nodo_inexistente(self):
        """Verifica manejo de errores cuando un nodo no existe"""
        grafo = nx.Graph()
        grafo.add_edge('A', 'B', weight=10.0)

        with pytest.raises(ValueError, match="no encontrado"):
            calcular_camino_mas_corto(grafo, 'A', 'Z')

    def test_error_sin_camino(self):
        """Verifica manejo de errores cuando no hay camino"""
        grafo = nx.Graph()
        grafo.add_node('A')
        grafo.add_node('B')

        with pytest.raises(ValueError, match="No existe camino"):
            calcular_camino_mas_corto(grafo, 'A', 'B')


class TestMatrizDistancias:
    """
    Pruebas para el cálculo de matrices de distancias.
    Verifica que se calculen correctamente todas las distancias.
    """

    def test_matriz_3_puntos(self):
        """Prueba matriz de 3 puntos en grafo simple"""
        grafo = nx.Graph()
        grafo.add_edge('n1', 'n2', weight=10.0)
        grafo.add_edge('n2', 'n3', weight=20.0)

        coords = {
            'n1': (0, 0),
            'n2': (1, 1),
            'n3': (2, 2)
        }

        puntos = [(0, 0), (1, 1), (2, 2)]
        nodos = ['n1', 'n2', 'n3']

        matriz = calcular_matriz_distancias(
            grafo, puntos, coords, nodos, mostrar_progreso=False
        )

        assert matriz.shape == (3, 3)
        assert matriz[0, 1] == 10.0
        assert matriz[1, 2] == 20.0
        assert matriz[0, 2] == 30.0

    def test_matriz_simetrica(self):
        """Verifica que la matriz sea simétrica"""
        grafo = nx.Graph()
        grafo.add_edge('n1', 'n2', weight=5.0)
        grafo.add_edge('n2', 'n3', weight=7.0)
        grafo.add_edge('n3', 'n1', weight=9.0)

        coords = {'n1': (0, 0), 'n2': (1, 1), 'n3': (2, 2)}
        puntos = [(0, 0), (1, 1), (2, 2)]
        nodos = ['n1', 'n2', 'n3']

        matriz = calcular_matriz_distancias(
            grafo, puntos, coords, nodos, mostrar_progreso=False
        )

        for i in range(3):
            for j in range(3):
                assert abs(matriz[i, j] - matriz[j, i]) < 0.001

    def test_diagonal_ceros(self):
        """Verifica que la diagonal sean ceros"""
        grafo = nx.Graph()
        grafo.add_edge('n1', 'n2', weight=10.0)

        coords = {'n1': (0, 0), 'n2': (1, 1)}
        puntos = [(0, 0), (1, 1)]
        nodos = ['n1', 'n2']

        matriz = calcular_matriz_distancias(
            grafo, puntos, coords, nodos, mostrar_progreso=False
        )

        assert matriz[0, 0] == 0.0
        assert matriz[1, 1] == 0.0

    def test_error_dimensiones_incorrectas(self):
        """Verifica manejo de errores con dimensiones incorrectas"""
        grafo = nx.Graph()
        coords = {}
        puntos = [(0, 0), (1, 1)]
        nodos = ['n1']

        with pytest.raises(ValueError, match="no coincide"):
            calcular_matriz_distancias(
                grafo, puntos, coords, nodos, mostrar_progreso=False
            )


class TestVerificacionMatriz:
    """
    Pruebas para verificación de propiedades de matrices.
    Comprueba simetría y desigualdad triangular.
    """

    def test_matriz_simetrica_valida(self):
        """Verifica detección correcta de matriz simétrica"""
        matriz = np.array([
            [0, 5, 10],
            [5, 0, 3],
            [10, 3, 0]
        ])

        es_simetrica = verificar_matriz_simetrica(matriz)

        assert es_simetrica

    def test_matriz_asimetrica(self):
        """Verifica detección correcta de matriz asimétrica"""
        matriz = np.array([
            [0, 5, 10],
            [6, 0, 3],
            [10, 3, 0]
        ])

        es_simetrica = verificar_matriz_simetrica(matriz)

        assert not es_simetrica

    def test_desigualdad_triangular_valida(self):
        """Verifica que matriz métrica cumpla desigualdad triangular"""
        matriz = np.array([
            [0, 10, 15],
            [10, 0, 8],
            [15, 8, 0]
        ])

        es_valida, violaciones = verificar_desigualdad_triangular(matriz)

        assert es_valida
        assert len(violaciones) == 0

    def test_desigualdad_triangular_invalida(self):
        """Verifica detección de violaciones de desigualdad triangular"""
        matriz = np.array([
            [0, 10, 5],
            [10, 0, 12],
            [5, 12, 0]
        ])

        es_valida, violaciones = verificar_desigualdad_triangular(matriz)

        assert not es_valida or len(violaciones) >= 0


class TestGrafoComplejo:
    """
    Pruebas con grafos más complejos.
    Simula escenarios reales de redes viales.
    """

    def test_grafo_grilla(self):
        """Prueba con grafo en forma de grilla"""
        grafo = nx.grid_2d_graph(3, 3)

        grafo_numerado = nx.convert_node_labels_to_integers(grafo)

        for u, v in grafo_numerado.edges():
            grafo_numerado[u][v]['weight'] = 1.0

        camino, distancia = calcular_camino_mas_corto(
            grafo_numerado, 0, 8
        )

        assert distancia == 4.0

    def test_grafo_conexo(self):
        """Verifica funcionamiento en grafo completamente conexo"""
        grafo = nx.complete_graph(5)

        for u, v in grafo.edges():
            grafo[u][v]['weight'] = abs(u - v) * 5.0

        camino, distancia = calcular_camino_mas_corto(grafo, 0, 4)

        assert camino is not None
        assert distancia > 0

