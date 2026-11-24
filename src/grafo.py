"""
Módulo de representación de grafos dirigidos y no dirigidos ponderados.

Este archivo define las estructuras de datos fundamentales para modelar una red
(grafo) mediante listas de adyacencia, utilizando clases para representar tanto
las conexiones individuales (Arista) como el grafo en su conjunto (Grafo).
Incluye además utilidades para cargar y exportar topologías en formato JSON.
"""

# Importamos json y Path para permitir la carga y guardado de grafos desde archivos externos (.json)
import json
from pathlib import Path
# Importamos dataclass para crear clases de datos de manera concisa sin escribir __init__ manualmente
from dataclasses import dataclass
# Importamos tipos de datos de typing para documentar las firmas de métodos y variables (Type Hints)
from typing import Any, Dict, List, Tuple, Union


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
    Representación de una red (dirigida o no dirigida) y ponderada mediante listas de adyacencia.

    Internamente utiliza un diccionario donde cada clave es el identificador de un vértice (nodo)
    y su valor asociado es una lista de objetos `Arista` que parten desde dicho vértice.
    """

    def __init__(self, dirigido: bool = True):
        """
        Inicializa un grafo vacío.

        Parámetros:
            dirigido (bool): Indica si el grafo es dirigido (True, por defecto) o no dirigido (False).
        """
        # Diccionario principal: mapea cada nodo (str) con su lista de aristas salientes (List[Arista])
        self.adyacencia: Dict[str, List[Arista]] = {}
        # Bandera que define el comportamiento general del grafo (Dirigido vs. No Dirigido)
        self.dirigido: bool = dirigido

    def agregar_vertice(self, vertice: str) -> None:
        """
        Registra un nuevo vértice (nodo) en el grafo si aún no existe.

        Parámetros:
            vertice (str): Identificador del nodo que se desea añadir a la red.
        """
        # Limpiamos espacios extremos para evitar nodos duplicados por error de digitación
        vertice = str(vertice).strip()
        if not vertice:
            raise ValueError("El nombre del vértice no puede estar vacío.")

        # Verificamos si el nodo no está registrado en el diccionario de adyacencia
        if vertice not in self.adyacencia:
            # Inicializamos su lista de conexiones salientes como una lista vacía
            self.adyacencia[vertice] = []

    def _insertar_o_actualizar_arco(self, u: str, v: str, peso: float) -> None:
        """
        Método interno auxiliar que inserta un arco dirigido u -> v o actualiza su peso si ya existía.

        Parámetros:
            u (str): Nodo de salida.
            v (str): Nodo de llegada.
            peso (float): Nuevo peso de la conexión.
        """
        # Si ya existe una arista de `u` hacia `v`, actualizamos su peso para no duplicarla
        for arista in self.adyacencia[u]:
            if arista.destino == v:
                arista.peso = float(peso)
                return
        # Si no existía previamente, agregamos la nueva instancia de Arista
        self.adyacencia[u].append(Arista(destino=v, peso=float(peso)))

    def agregar_arista(
        self,
        origen: str,
        destino: str,
        peso: float,
        bidireccional: bool = False,
    ) -> None:
        """
        Agrega o actualiza una arista ponderada desde un nodo `origen` hacia un nodo `destino`.
        Si los nodos no existen previamente en el grafo, se crean automáticamente.

        Parámetros:
            origen (str): Identificador del nodo de partida.
            destino (str): Identificador del nodo de llegada.
            peso (float): Costo o distancia de la arista (debe ser >= 0 para el algoritmo de Dijkstra).
            bidireccional (bool): Si es True (o si el grafo está configurado como no dirigido),
                                  agrega también la arista inversa (destino -> origen) con el mismo peso.

        Excepciones:
            ValueError: Si el peso proporcionado es negativo, ya que el algoritmo de Dijkstra
                        no garantiza caminos mínimos con costos negativos.
        """
        # Validación de precondición de Dijkstra: no se permiten aristas con pesos negativos
        if peso < 0:
            raise ValueError(
                f"Error: La arista {origen}->{destino} tiene peso negativo ({peso}). Dijkstra no lo admite."
            )

        origen = str(origen).strip()
        destino = str(destino).strip()

        # Nos aseguramos de que tanto el nodo origen como el nodo destino existan en el diccionario
        self.agregar_vertice(origen)
        self.agregar_vertice(destino)

        # Añadimos o actualizamos la arista dirigida en la lista de adyacencia del nodo origen
        self._insertar_o_actualizar_arco(origen, destino, peso)

        # Si se solicitó conexión bidireccional o el grafo completo es no dirigido, añadimos el sentido inverso
        if bidireccional or not self.dirigido:
            self._insertar_o_actualizar_arco(destino, origen, peso)

    @property
    def vertices(self) -> List[str]:
        """
        Propiedad que devuelve una lista con todos los vértices (nodos) registrados en el grafo.

        Retorna:
            List[str]: Lista con los identificadores de todos los nodos del grafo.
        """
        # Extraemos las claves del diccionario de adyacencia y las convertimos en una lista
        return list(self.adyacencia.keys())

    def obtener_aristas(self) -> List[Tuple[str, str, float]]:
        """
        Devuelve la lista de aristas del grafo como tuplas `(origen, destino, peso)`.

        Si el grafo es no dirigido (`self.dirigido == False`), evita duplicar el par inverso
        `(destino, origen)` para presentar cada conexión una sola vez en tablas o archivos.

        Retorna:
            List[Tuple[str, str, float]]: Lista de tuplas con origen, destino y peso.
        """
        lista_aristas: List[Tuple[str, str, float]] = []
        pares_vistos = set()

        for origen, aristas_salientes in self.adyacencia.items():
            for arista in aristas_salientes:
                if not self.dirigido:
                    # Ordenamos el par (origen, destino) para no repetir B-A si ya agregamos A-B
                    par_normalizado = tuple(sorted((origen, arista.destino)))
                    if par_normalizado in pares_vistos:
                        continue
                    pares_vistos.add(par_normalizado)
                lista_aristas.append((origen, arista.destino, arista.peso))

        return lista_aristas

    def a_diccionario(self, nombre: str = "Grafo Personalizado") -> Dict[str, Any]:
        """
        Serializa el grafo actual a un diccionario compatible con el formato JSON del proyecto.

        Parámetros:
            nombre (str): Nombre descriptivo para identificar la topología.

        Retorna:
            Dict[str, Any]: Diccionario listo para convertirse a JSON.
        """
        return {
            "nombre": nombre,
            "dirigido": self.dirigido,
            "vertices": self.vertices,
            "aristas": [
                {"origen": u, "destino": v, "peso": peso}
                for u, v, peso in self.obtener_aristas()
            ],
        }

    @classmethod
    def desde_diccionario(cls, datos: Dict[str, Any]) -> "Grafo":
        """
        Construye una instancia de `Grafo` a partir de un diccionario (proveniente de un JSON).

        Parámetros:
            datos (Dict[str, Any]): Diccionario con las claves `dirigido`, `vertices` y `aristas`.

        Retorna:
            Grafo: Nueva instancia del grafo poblada con todos sus vértices y aristas.
        """
        es_dirigido = bool(datos.get("dirigido", True))
        grafo = cls(dirigido=es_dirigido)

        # Registramos primero todos los vértices (incluyendo posibles nodos aislados)
        for vertice in datos.get("vertices", []):
            grafo.agregar_vertice(str(vertice))

        # Registramos todas las aristas con sus pesos correspondientes
        for item in datos.get("aristas", []):
            grafo.agregar_arista(
                origen=str(item["origen"]),
                destino=str(item["destino"]),
                peso=float(item["peso"]),
                bidireccional=not es_dirigido,
            )

        return grafo

    @classmethod
    def cargar_desde_json(cls, ruta_archivo: Union[str, Path]) -> Tuple["Grafo", Dict[str, Any]]:
        """
        Lee un archivo `.json` del disco y construye el objeto `Grafo` correspondiente.

        Parámetros:
            ruta_archivo (Union[str, Path]): Ruta hacia el archivo JSON.

        Retorna:
            Tuple[Grafo, Dict[str, Any]]: Tupla con la instancia de `Grafo` y los metadatos originales del JSON.
        """
        ruta = Path(ruta_archivo)
        with ruta.open("r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        grafo = cls.desde_diccionario(datos)
        return grafo, datos
