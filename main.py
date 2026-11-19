"""
Punto de entrada principal del proyecto (Script de demostración y validación manual).

Construye un grafo dirigido de prueba, ejecuta el algoritmo de Dijkstra desde
el nodo 'A' hasta el nodo 'E', y muestra detalladamente en consola las distancias
mínimas hacia cada vértice, el árbol de predecesores, la ruta óptima y su costo total.
"""

# Importamos la estructura de datos Grafo para construir la red de nodos y aristas
from src.grafo import Grafo
# Importamos la función principal que ejecuta el algoritmo de caminos mínimos de Dijkstra
from src.dijkstra import ejecutar_dijkstra


def main() -> None:
    """
    Función principal que configura el caso de estudio, ejecuta Dijkstra e imprime el reporte.
    """
    # Instanciamos un nuevo objeto Grafo vacío
    grafo = Grafo()

    # Definimos la lista de aristas dirigidas del caso de validación manual.
    # Cada tupla tiene el formato: (nodo_origen, nodo_destino, peso_o_costo)
    aristas = [
        ("A", "B", 4),   # Conexión de A hacia B con costo 4
        ("A", "C", 2),   # Conexión de A hacia C con costo 2
        ("C", "B", 1),   # Conexión de C hacia B con costo 1 (mejora el costo para llegar a B: 2+1 = 3 < 4)
        ("B", "D", 5),   # Conexión de B hacia D con costo 5
        ("C", "D", 8),   # Conexión directa de C hacia D con costo 8
        ("C", "E", 10),  # Conexión directa de C hacia E con costo 10
        ("D", "E", 2),   # Conexión de D hacia E con costo 2
    ]

    # Recorremos la lista de tuplas y agregamos cada conexión dirigida dentro del grafo
    for origen_arista, destino_arista, peso in aristas:
        grafo.agregar_arista(origen_arista, destino_arista, peso)

    # Definimos el nodo de partida (origen) y el nodo objetivo (destino) para la consulta
    origen = "A"
    destino = "E"

    # Ejecutamos el algoritmo de Dijkstra en el grafo partiendo desde el nodo origen ("A")
    resultado = ejecutar_dijkstra(grafo, origen)
    # Reconstruimos la lista ordenada de nodos que forman el camino más corto hacia "E"
    ruta_optima = resultado.camino_hacia(destino)
    # Obtenemos el costo numérico total acumulado de la ruta óptima hacia "E"
    costo_total = resultado.costo_hacia(destino)

    # Impresión formateada en consola de los resultados obtenidos
    print("=" * 55)
    print("  VALIDACIÓN MANUAL - ALGORITMO DE DIJKSTRA (FASE 2)")
    print("=" * 55)
    print(f"Nodo origen  : {origen}")
    print(f"Nodo destino : {destino}\n")

    # 1. Mostramos la tabla de distancias mínimas desde el origen hacia todos los nodos del grafo
    print("1. Distancias mínimas desde A:")
    for nodo, distancia in resultado.distancias.items():
        print(f"   - {origen} -> {nodo}: {distancia}")

    # 2. Mostramos el diccionario de predecesores (qué nodo antecede a cuál en el camino óptimo)
    print("\n2. Diccionario de predecesores:")
    print(f"   {resultado.predecesores}")

    # 3. Mostramos la secuencia visual de saltos que componen la ruta óptima de A hasta E
    print("\n3. Ruta óptima:")
    print(f"   {' -> '.join(ruta_optima)}")

    # 4. Mostramos el costo total de la ruta formateado de manera limpia (:g elimina decimales .0 innecesarios)
    print("\n4. Costo total:")
    print(f"   {costo_total:g}")
    print("=" * 55)


# Punto de entrada estándar en Python: solo ejecuta main() si el archivo es invocado directamente
if __name__ == "__main__":
    main()
