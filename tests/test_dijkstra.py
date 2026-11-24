"""
Suite de pruebas unitarias para el grafo, el algoritmo de Dijkstra, la carga JSON y el visualizador.

Utiliza el framework `pytest` para verificar:
1. Cálculo de rutas óptimas en grafos dirigidos (caso de estudio del informe).
2. Cálculo de rutas óptimas en grafos no dirigidos (bidireccionales).
3. Validación contra pesos negativos (`ValueError`).
4. Manejo de nodos aislados o desconexos.
5. Carga de topologías desde archivos JSON (`data/caso_estudio_informe.json`).
6. Identificación y coloreado de aristas pertenecientes a la ruta óptima en el visualizador.
"""

from pathlib import Path
# Importamos pytest para ejecutar aserciones y capturar excepciones esperadas
import pytest
# Importamos la clase Grafo para instanciar las redes de prueba en cada test
from src.grafo import Grafo
# Importamos la función ejecutar_dijkstra que será sometida a verificación
from src.dijkstra import ejecutar_dijkstra
# Importamos utilidades del visualizador para verificar la detección de aristas óptimas
from src.visualizador import obtener_aristas_de_ruta, generar_html_grafo_interactivo


def test_caso_base_convergente():
    """
    Verifica que el algoritmo encuentre correctamente la ruta más corta y el costo mínimo
    en un grafo dirigido donde existen múltiples caminos convergentes hacia el destino.
    """
    g = Grafo(dirigido=True)

    # Agregamos las aristas dirigidas con sus respectivos pesos
    g.agregar_arista("A", "B", 4)
    g.agregar_arista("A", "C", 2)
    g.agregar_arista("C", "B", 1)   # Mejora el camino hacia B pasando por C (costo 3 en vez de 4)
    g.agregar_arista("B", "D", 5)   # Llega a D con costo acumulado 3 + 5 = 8 (mejor que A->C->D = 10)
    g.agregar_arista("C", "D", 8)
    g.agregar_arista("C", "E", 10)  # Camino directo de C a E daría costo 2 + 10 = 12
    g.agregar_arista("D", "E", 2)   # Camino pasando por D da el óptimo: 8 + 2 = 10

    # Ejecutamos Dijkstra desde el nodo inicial "A"
    res = ejecutar_dijkstra(g, "A")

    # Comprobamos que el costo total mínimo hacia "E" sea exactamente 10
    assert res.costo_hacia("E") == 10
    # Comprobamos que la secuencia de nodos de la ruta óptima sea A -> C -> B -> D -> E
    assert res.camino_hacia("E") == ["A", "C", "B", "D", "E"]


def test_grafo_no_dirigido_bidireccional():
    """
    Verifica que un grafo configurado como No Dirigido (`dirigido=False`) permita recorrer
    las aristas en sentido inverso al que fueron declaradas.
    """
    g = Grafo(dirigido=False)
    g.agregar_arista("A", "B", 3)
    g.agregar_arista("B", "C", 2)

    # Ejecutamos Dijkstra desde "C" hacia "A" (sentido inverso al registrado)
    res = ejecutar_dijkstra(g, "C")
    assert res.costo_hacia("A") == 5
    assert res.camino_hacia("A") == ["C", "B", "A"]


def test_rechazo_pesos_negativos():
    """
    Verifica que el grafo rechace la inserción de aristas con pesos negativos
    lanzando una excepción de tipo `ValueError`, dado que Dijkstra no soporta costos negativos.
    """
    g = Grafo()
    with pytest.raises(ValueError):
        g.agregar_arista("A", "B", -3)


def test_nodo_desconexo():
    """
    Verifica el comportamiento del algoritmo cuando existe un vértice aislado (sin conexión
    desde el nodo origen): su costo debe ser infinito y la ruta reconstruida debe ser vacía.
    """
    g = Grafo()
    g.agregar_arista("A", "B", 5)
    g.agregar_vertice("Z")  # Nodo completamente aislado

    res = ejecutar_dijkstra(g, "A")
    assert res.costo_hacia("Z") == float("inf")
    assert res.camino_hacia("Z") == []


def test_carga_desde_json():
    """
    Verifica que el grafo se pueda cargar dinámicamente desde el archivo JSON de la carpeta `data/`
    y arroje el mismo resultado óptimo del informe.
    """
    ruta_json = Path(__file__).resolve().parent.parent / "data" / "caso_estudio_informe.json"
    grafo, metadatos = Grafo.cargar_desde_json(ruta_json)

    assert grafo.dirigido is True
    assert metadatos["origen_por_defecto"] == "A"

    res = ejecutar_dijkstra(grafo, "A")
    assert res.costo_hacia("E") == 10.0
    assert res.camino_hacia("E") == ["A", "C", "B", "D", "E"]


def test_visualizador_resalta_aristas_ruta_optima():
    """
    Verifica que el módulo visualizador identifique los tramos exactos de la ruta óptima
    y genere el documento HTML con el color verde de resaltado (`#16A34A`).
    """
    g = Grafo(dirigido=True)
    g.agregar_arista("A", "C", 2)
    g.agregar_arista("C", "B", 1)
    g.agregar_arista("A", "B", 4)

    res = ejecutar_dijkstra(g, "A")
    camino = res.camino_hacia("B")

    tramos = obtener_aristas_de_ruta(camino, dirigido=True)
    assert ("A", "C") in tramos
    assert ("C", "B") in tramos
    assert ("A", "B") not in tramos

    html = generar_html_grafo_interactivo(g, camino_optimo=camino, origen="A", destino="B", resultado=res)
    assert "#16A34A" in html
