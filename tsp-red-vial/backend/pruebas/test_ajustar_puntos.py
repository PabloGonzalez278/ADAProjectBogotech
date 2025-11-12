"""
Pruebas unitarias para el módulo de ajuste de puntos.
Verifica la integración de puntos en la red vial.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import networkx as nx
from dominio.ajustar_puntos import (
    proyectar_punto_en_arista,
    dividir_arista,
    integrar_punto_en_red,
    integrar_multiples_puntos,
    validar_integracion
)


class TestProyeccionPunto:
    """
    Pruebas para la proyección de puntos sobre aristas.
    Verifica el cálculo geométrico de proyección.
    """

    def test_proyeccion_punto_medio(self):
        """Prueba proyección de punto en el medio de arista"""
        punto = (1.0, 1.5)
        coord_u = (1.0, 1.0)
        coord_v = (1.0, 2.0)

        punto_proyectado, ratio = proyectar_punto_en_arista(punto, coord_u, coord_v)

        assert abs(ratio - 0.5) < 0.01

    def test_proyeccion_cerca_inicio(self):
        """Prueba proyección cerca del inicio de arista"""
        punto = (1.0, 1.1)
        coord_u = (1.0, 1.0)
        coord_v = (1.0, 2.0)

        punto_proyectado, ratio = proyectar_punto_en_arista(punto, coord_u, coord_v)

        assert ratio < 0.2

    def test_proyeccion_cerca_final(self):
        """Prueba proyección cerca del final de arista"""
        punto = (1.0, 1.9)
        coord_u = (1.0, 1.0)
        coord_v = (1.0, 2.0)

        punto_proyectado, ratio = proyectar_punto_en_arista(punto, coord_u, coord_v)

        assert ratio > 0.8


class TestDivisionArista:
    """
    Pruebas para la división de aristas.
    Verifica que las aristas se dividan correctamente.
    """

    def test_division_arista_simple(self):
        """Prueba división simple de una arista"""
        grafo = nx.Graph()
        grafo.add_edge('A', 'B', weight=10.0)

        num_aristas_inicial = grafo.number_of_edges()

        dividir_arista(
            grafo, 'A', 'B', 'C',
            (1.5, 1.5),
            5.0, 5.0
        )

        assert not grafo.has_edge('A', 'B')
        assert grafo.has_edge('A', 'C')
        assert grafo.has_edge('C', 'B')
        assert grafo.number_of_edges() == num_aristas_inicial + 1

    def test_pesos_despues_division(self):
        """Verifica que los pesos se asignen correctamente"""
        grafo = nx.Graph()
        grafo.add_edge('A', 'B', weight=10.0)

        dividir_arista(
            grafo, 'A', 'B', 'C',
            (1.5, 1.5),
            6.0, 4.0
        )

        assert grafo['A']['C']['weight'] == 6.0
        assert grafo['C']['B']['weight'] == 4.0

    def test_error_arista_inexistente(self):
        """Verifica manejo de error con arista inexistente"""
        grafo = nx.Graph()
        grafo.add_node('A')
        grafo.add_node('B')

        with pytest.raises(ValueError, match="no existe"):
            dividir_arista(grafo, 'A', 'B', 'C', (1.5, 1.5), 5.0, 5.0)


class TestIntegracionPunto:
    """
    Pruebas para la integración de puntos en la red.
    Verifica el proceso completo de integración.
    """

    def test_integracion_punto_simple(self):
        """Prueba integración de un punto en red simple"""
        grafo = nx.Graph()
        grafo.add_edge('n1', 'n2', weight=100.0)

        coords = {
            'n1': (0.0, 0.0),
            'n2': (0.0, 1.0)
        }

        punto = (0.0, 0.5)

        nodo_creado, distancia = integrar_punto_en_red(
            grafo, coords, punto, 1, "Punto 1", umbral_distancia=100.0
        )

        assert 'punto_1' in nodo_creado
        assert nodo_creado in coords
        assert grafo.has_node(nodo_creado)

    def test_punto_fuera_umbral(self):
        """Verifica rechazo de punto fuera del umbral"""
        grafo = nx.Graph()
        grafo.add_edge('n1', 'n2', weight=10.0)

        coords = {
            'n1': (0.0, 0.0),
            'n2': (0.0, 1.0)
        }

        punto_lejano = (10.0, 10.0)

        with pytest.raises(ValueError, match="demasiado lejos"):
            integrar_punto_en_red(
                grafo, coords, punto_lejano, 1, "Punto Lejano",
                umbral_distancia=1.0
            )

    def test_conectividad_despues_integracion(self):
        """Verifica que la red siga conectada después de integrar"""
        grafo = nx.Graph()
        grafo.add_edge('n1', 'n2', weight=10.0)
        grafo.add_edge('n2', 'n3', weight=10.0)

        coords = {
            'n1': (0.0, 0.0),
            'n2': (0.0, 1.0),
            'n3': (0.0, 2.0)
        }

        punto = (0.0, 0.5)

        nodo_creado, _ = integrar_punto_en_red(
            grafo, coords, punto, 1, "P1", umbral_distancia=100.0
        )

        assert nx.is_connected(grafo)


class TestIntegracionMultiple:
    """
    Pruebas para integración de múltiples puntos.
    Verifica procesamiento batch de puntos.
    """

    def test_integracion_3_puntos(self):
        """Prueba integración de 3 puntos"""
        grafo = nx.Graph()
        grafo.add_edge('n1', 'n2', weight=100.0)
        grafo.add_edge('n2', 'n3', weight=100.0)

        coords = {
            'n1': (0.0, 0.0),
            'n2': (0.0, 1.0),
            'n3': (0.0, 2.0)
        }

        puntos = [
            (1, 0.0, 0.3, "Punto A"),
            (2, 0.0, 0.7, "Punto B"),
            (3, 0.0, 1.5, "Punto C")
        ]

        resultados = integrar_multiples_puntos(
            grafo, coords, puntos, umbral_distancia=100.0,
            mostrar_progreso=False
        )

        assert len(resultados) == 3
        assert all(id in resultados for id in [1, 2, 3])

    def test_orden_integracion(self):
        """Verifica que los puntos se integren en orden"""
        grafo = nx.Graph()
        grafo.add_edge('n1', 'n2', weight=10.0)

        coords = {
            'n1': (0.0, 0.0),
            'n2': (0.0, 1.0)
        }

        puntos = [
            (1, 0.0, 0.2, "P1"),
            (2, 0.0, 0.5, "P2"),
            (3, 0.0, 0.8, "P3")
        ]

        nodos_inicial = grafo.number_of_nodes()

        resultados = integrar_multiples_puntos(
            grafo, coords, puntos, umbral_distancia=100.0,
            mostrar_progreso=False
        )

        assert grafo.number_of_nodes() == nodos_inicial + 3


class TestValidacionIntegracion:
    """
    Pruebas para validación de integración.
    Verifica que los puntos integrados sean válidos.
    """

    def test_validacion_exitosa(self):
        """Prueba validación de integración exitosa"""
        grafo = nx.Graph()
        grafo.add_edge('n1', 'punto_1', weight=5.0)
        grafo.add_edge('punto_1', 'n2', weight=5.0)
        grafo.add_edge('n2', 'punto_2', weight=5.0)
        grafo.add_edge('punto_2', 'n3', weight=5.0)

        coords = {
            'n1': (0.0, 0.0),
            'punto_1': (0.0, 0.5),
            'n2': (0.0, 1.0),
            'punto_2': (0.0, 1.5),
            'n3': (0.0, 2.0)
        }

        nodos_puntos = ['punto_1', 'punto_2']

        es_valido, errores = validar_integracion(grafo, coords, nodos_puntos)

        assert es_valido
        assert len(errores) == 0

    def test_validacion_nodo_inexistente(self):
        """Prueba detección de nodo inexistente"""
        grafo = nx.Graph()
        coords = {}
        nodos_puntos = ['nodo_fantasma']

        es_valido, errores = validar_integracion(grafo, coords, nodos_puntos)

        assert not es_valido
        assert len(errores) > 0

    def test_validacion_nodo_aislado(self):
        """Prueba detección de nodo aislado"""
        grafo = nx.Graph()
        grafo.add_node('punto_1')

        coords = {'punto_1': (0.0, 0.0)}
        nodos_puntos = ['punto_1']

        es_valido, errores = validar_integracion(grafo, coords, nodos_puntos)

        assert not es_valido
        assert any('aislado' in e for e in errores)

