"""
Módulo de representación de grafos dirigidos y ponderados.

Este archivo define las estructuras de datos fundamentales para modelar una red
(grafo) mediante listas de adyacencia, utilizando clases para representar tanto
las conexiones individuales (Arista) como el grafo en su conjunto (Grafo).
"""

# Importamos dataclass para crear clases de datos de manera concisa sin escribir __init__ manualmente
from dataclasses import dataclass, field
# Importamos tipos de datos de typing para documentar las firmas de métodos y variables (Type Hints)
from typing import Dict, List, Tuple


@dataclass
class Arista:
    """
    Representa una conexión dirigida (arista o arco) hacia un nodo destino con un costo asociado.

    Atributos:
        destino (str): Identificador o nombre del nodo al que apunta esta arista.
        peso (float): Costo, distancia o ponderación necesaria para recorrer esta conexión.
    """
    destino: str  # Nodo final de la conexión dirigida
    peso: float   # Costo o peso no negativo asociado al recorrido de la arista


class Grafo:
    """
    Representación de una red dirigida y ponderada mediante listas de adyacencia.

    Internamente utiliza un diccionario donde cada clave es el identificador de un vértice (nodo)
    y su valor asociado es una lista de objetos `Arista` que parten desde dicho vértice.
    """

    def __init__(self):
        """
        Inicializa un grafo vacío.
        """
        # Diccionario principal: mapea cada nodo (str) con su lista de aristas salientes (List[Arista])
        self.adyacencia: Dict[str, List[Arista]] = {}

    def agregar_vertice(self, vertice: str) -> None:
        """
        Registra un nuevo vértice (nodo) en el grafo si aún no existe.

        Parámetros:
            vertice (str): Identificador del nodo que se desea añadir a la red.
        """
        # Verificamos si el nodo no está registrado en el diccionario de adyacencia
        if vertice not in self.adyacencia:
            # Inicializamos su lista de conexiones salientes como una lista vacía
            self.adyacencia[vertice] = []

    def agregar_arista(self, origen: str, destino: str, peso: float, bidireccional: bool = False) -> None:
        """
        Agrega una arista ponderada desde un nodo `origen` hacia un nodo `destino`.
        Si los nodos no existen previamente en el grafo, se crean automáticamente.

        Parámetros:
            origen (str): Identificador del nodo de partida.
            destino (str): Identificador del nodo de llegada.
            peso (float): Costo o distancia de la arista (debe ser >= 0 para el algoritmo de Dijkstra).
            bidireccional (bool): Si es True, agrega también la arista inversa (destino -> origen)
                                  con el mismo peso, simulando una arista no dirigida.

        Excepciones:
            ValueError: Si el peso proporcionado es negativo, ya que el algoritmo de Dijkstra
                        no garantiza caminos mínimos con costos negativos.
        """
        # Validación de precondición de Dijkstra: no se permiten aristas con pesos negativos
        if peso < 0:
            raise ValueError(f"Error: La arista {origen}->{destino} tiene peso negativo ({peso}). Dijkstra no lo admite.")
        
        # Nos aseguramos de que tanto el nodo origen como el nodo destino existan en el diccionario
        self.agregar_vertice(origen)
        self.agregar_vertice(destino)
        
        # Añadimos la nueva arista dirigida a la lista de adyacencia del nodo origen
        self.adyacencia[origen].append(Arista(destino=destino, peso=peso))
        
        # Si la conexión es bidireccional (no dirigida), añadimos la arista en sentido contrario
        if bidireccional:
            self.adyacencia[destino].append(Arista(destino=origen, peso=peso))

    @property
    def vertices(self) -> List[str]:
        """
        Propiedad que devuelve una lista con todos los vértices (nodos) registrados en el grafo.

        Retorna:
            List[str]: Lista con los identificadores de todos los nodos del grafo.
        """
        # Extraemos las claves del diccionario de adyacencia y las convertimos en una lista
        return list(self.adyacencia.keys())
