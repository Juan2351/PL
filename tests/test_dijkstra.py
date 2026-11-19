"""
Suite de pruebas unitarias para el grafo y el algoritmo de Dijkstra.

Utiliza el framework `pytest` para verificar el correcto funcionamiento del cálculo
de rutas óptimas, la validación contra pesos negativos y el manejo de nodos aislados (desconexos).
"""

# Importamos pytest para ejecutar aserciones y capturar excepciones esperadas
import pytest
# Importamos la clase Grafo para instanciar las redes de prueba en cada test
from src.grafo import Grafo
# Importamos la función ejecutar_dijkstra que será sometida a verificación
from src.dijkstra import ejecutar_dijkstra


def test_caso_base_convergente():
    """
    Verifica que el algoritmo encuentre correctamente la ruta más corta y el costo mínimo
    en un grafo dirigido donde existen múltiples caminos convergentes hacia el destino.
    """
    # Creamos una instancia de grafo vacío
    g = Grafo()
    
    # Agregamos las aristas dirigidas con sus respectivos pesos
    g.agregar_arista("A", "B", 4)
    g.agregar_arista("A", "C", 2)
    g.agregar_arista("C", "B", 1)   # Permite mejorar el camino hacia B pasando por C (costo 3 en vez de 4)
    g.agregar_arista("B", "D", 5)   # Permite llegar a D con costo acumulado 3 + 5 = 8 (mejor que A->C->D = 10)
    g.agregar_arista("C", "D", 8)
    g.agregar_arista("C", "E", 10)  # Camino directo de C a E daría costo 2 + 10 = 12
    g.agregar_arista("D", "E", 2)   # Camino pasando por D da el óptimo: 8 + 2 = 10

    # Ejecutamos Dijkstra desde el nodo inicial "A"
    res = ejecutar_dijkstra(g, "A")
    
    # Comprobamos que el costo total mínimo hacia "E" sea exactamente 10
    assert res.costo_hacia("E") == 10
    # Comprobamos que la secuencia de nodos de la ruta óptima sea A -> C -> B -> D -> E
    assert res.camino_hacia("E") == ["A", "C", "B", "D", "E"]


def test_rechazo_pesos_negativos():
    """
    Verifica que el grafo rechace la inserción de aristas con pesos negativos
    lanzando una excepción de tipo `ValueError`, dado que Dijkstra no soporta costos negativos.
    """
    g = Grafo()
    # Esperamos que al intentar insertar un peso de -3 se dispare un ValueError
    with pytest.raises(ValueError):
        g.agregar_arista("A", "B", -3)


def test_nodo_desconexo():
    """
    Verifica el comportamiento del algoritmo cuando existe un vértice aislado (sin conexión
    desde el nodo origen): su costo debe ser infinito y la ruta reconstruida debe ser vacía.
    """
    g = Grafo()
    # Conectamos A con B
    g.agregar_arista("A", "B", 5)
    # Agregamos un vértice "Z" completamente aislado (sin aristas entrantes ni salientes)
    g.agregar_vertice("Z")
    
    # Ejecutamos Dijkstra partiendo desde "A"
    res = ejecutar_dijkstra(g, "A")
    
    # Al ser inalcanzable desde "A", el costo hacia "Z" debe mantenerse en infinito
    assert res.costo_hacia("Z") == float('inf')
    # Al no existir ruta posible entre "A" y "Z", el camino devuelto debe ser una lista vacía
    assert res.camino_hacia("Z") == []
