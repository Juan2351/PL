"""
Módulo de implementación del Algoritmo de Dijkstra.

Contiene la lógica para calcular los caminos más cortos desde un nodo origen
hacia todos los demás nodos de un grafo ponderado con pesos no negativos,
así como la clase contenedora para consultar las distancias y reconstruir las rutas óptimas.
"""

# Importamos heapq para utilizar una cola de prioridad (Min-Heap) eficiente
import heapq
# Importamos anotaciones de tipos para mejorar la legibilidad y el análisis estático del código
from typing import Dict, List, Optional, Tuple
# Importamos la clase Grafo para tipar el parámetro de entrada del algoritmo
from src.grafo import Grafo


class ResultadoDijkstra:
    """
    Encapsula los resultados obtenidos tras ejecutar el algoritmo de Dijkstra desde un nodo origen.

    Permite consultar el costo mínimo hacia cualquier nodo destino y reconstruir
    la secuencia exacta de vértices que conforman la ruta óptima.
    """

    def __init__(self, distancias: Dict[str, float], predecesores: Dict[str, Optional[str]], origen: str):
        """
        Inicializa el contenedor de resultados de Dijkstra.

        Parámetros:
            distancias (Dict[str, float]): Diccionario con la distancia mínima acumulada desde el origen a cada nodo.
            predecesores (Dict[str, Optional[str]]): Diccionario que guarda el nodo previo inmediato en la ruta óptima.
            origen (str): Identificador del nodo de partida desde el cual se ejecutó el algoritmo.
        """
        self.distancias = distancias      # Mapa: nodo -> costo mínimo acumulado desde el origen
        self.predecesores = predecesores  # Mapa: nodo -> nodo anterior en el camino más corto
        self.origen = origen              # Nodo inicial de la búsqueda

    def camino_hacia(self, destino: str) -> List[str]:
        """
        Reconstruye la ruta óptima (secuencia de nodos) desde el nodo origen hasta el nodo `destino`.

        Realiza un recorrido inverso (backtracking) a través del diccionario de predecesores
        comenzando desde el destino hasta llegar al origen.

        Parámetros:
            destino (str): Identificador del nodo al que se desea llegar.

        Retorna:
            List[str]: Lista ordenada de nodos desde el origen hasta el destino.
                       Si el destino no es alcanzable o no existe, retorna una lista vacía `[]`.
        """
        # Lista temporal donde almacenaremos los nodos del camino en orden inverso (destino -> origen)
        camino = []
        # Empezamos el rastreo hacia atrás desde el nodo destino
        actual: Optional[str] = destino
        
        # Retrocedemos de predecesor en predecesor mientras el nodo actual sea válido
        while actual is not None:
            camino.append(actual)  # Agregamos el nodo actual al recorrido
            if actual == self.origen:
                # Si ya llegamos al nodo origen, detenemos la búsqueda hacia atrás
                break
            # Avanzamos al nodo padre (predecesor) del nodo actual
            actual = self.predecesores.get(actual)
        
        # Invertimos la lista para que quede en el sentido correcto (origen -> ... -> destino)
        camino.reverse()
        
        # Verificamos que el camino no esté vacío y que efectivamente comience en el origen
        # (Si el nodo destino estaba desconectado, nunca habrá alcanzado a `self.origen`)
        return camino if (camino and camino[0] == self.origen) else []

    def costo_hacia(self, destino: str) -> float:
        """
        Obtiene el costo o distancia total mínima calculada desde el origen hasta el nodo `destino`.

        Parámetros:
            destino (str): Identificador del nodo destino a consultar.

        Retorna:
            float: Costo mínimo total hacia el destino, o `float('inf')` si el nodo es inalcanzable o no existe.
        """
        # Busca el nodo en el diccionario de distancias; si no existe, devuelve infinito
        return self.distancias.get(destino, float('inf'))


def ejecutar_dijkstra(grafo: Grafo, origen: str) -> ResultadoDijkstra:
    """
    Ejecuta el algoritmo de Dijkstra utilizando una cola de prioridad (Min-Heap).

    Calcula el árbol de caminos más cortos desde el vértice `origen` hacia todos
    los demás vértices alcanzables dentro del `grafo`.

    Parámetros:
        grafo (Grafo): Instancia del grafo sobre el cual se realizará la búsqueda.
        origen (str): Identificador del nodo de partida.

    Retorna:
        ResultadoDijkstra: Objeto con los diccionarios de distancias mínimas, predecesores
                           y métodos auxiliares para consultar rutas y costos.

    Excepciones:
        KeyError: Si el nodo `origen` no se encuentra registrado en el grafo.
    """
    # Validamos que el nodo de partida exista dentro del grafo antes de iniciar
    if origen not in grafo.adyacencia:
        raise KeyError(f"El nodo origen '{origen}' no existe en el grafo.")

    # 1. Inicialización de estructuras:
    # Asignamos distancia infinita a todos los vértices inicialmente, pues aún no conocemos cómo llegar a ellos
    distancias: Dict[str, float] = {v: float('inf') for v in grafo.vertices}
    # Inicializamos el predecesor de cada vértice como None (sin padre asignado en la ruta óptima)
    predecesores: Dict[str, Optional[str]] = {v: None for v in grafo.vertices}
    # La distancia desde el nodo origen hacia sí mismo es siempre 0.0
    distancias[origen] = 0.0

    # 2. Configuración de la cola de prioridad (Min-Heap) y conjunto de visitados:
    # Almacena tuplas (distancia_acumulada, nodo). heapq ordena automáticamente por el primer elemento (menor distancia)
    cola_prioridad: List[Tuple[float, str]] = [(0.0, origen)]
    # Conjunto para registrar los nodos cuya distancia mínima definitiva ya fue procesada y cerrada
    visitados = set()

    # 3. Bucle principal de exploración voraz (Greedy):
    # Se ejecuta mientras queden nodos pendientes por explorar en la cola de prioridad
    while cola_prioridad:
        # Extraemos el nodo `u` con la menor distancia acumulada disponible en el Min-Heap
        dist_actual, u = heapq.heappop(cola_prioridad)

        # Si el nodo `u` ya fue procesado anteriormente con una distancia menor, lo ignoramos (lazy deletion)
        if u in visitados:
            continue
        # Marcamos el nodo `u` como visitado; su distancia mínima desde el origen ya es definitiva
        visitados.add(u)

        # 4. Relajación de aristas (exploración de vecinos):
        # Iteramos sobre todas las aristas salientes desde el nodo actual `u`
        for arista in grafo.adyacencia[u]:
            v = arista.destino            # Nodo vecino al que apunta la arista
            peso = arista.peso            # Costo de desplazarse desde `u` hasta `v`
            nueva_dist = dist_actual + peso  # Costo total acumulado pasando por `u` para llegar a `v`

            # Condición de relajación: ¿Es más corto llegar a `v` pasando por `u` que el camino conocido hasta ahora?
            if nueva_dist < distancias[v]:
                distancias[v] = nueva_dist  # Actualizamos la mejor distancia conocida hacia `v`
                predecesores[v] = u         # Registramos a `u` como el nodo previo óptimo para llegar a `v`
                # Insertamos el nuevo estado en la cola de prioridad para expandir sus vecinos posteriormente
                heapq.heappush(cola_prioridad, (nueva_dist, v))

    # 5. Retornamos el objeto contenedor con todas las distancias mínimas y predecesores calculados
    return ResultadoDijkstra(distancias, predecesores, origen)
