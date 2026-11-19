# Proyecto: Algoritmo de Dijkstra en Python

Implementación modular y documentada del **Algoritmo de Dijkstra** para encontrar caminos más cortos desde un nodo origen hacia todos los demás nodos en un grafo dirigido o no dirigido con pesos no negativos.

---

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Explicación de los Componentes](#explicación-de-los-componentes)
4. [Caso de Validación Manual](#caso-de-validación-manual)
5. [Requisitos e Instalación](#requisitos-e-instalación)
6. [Ejecución del Proyecto y Pruebas](#ejecución-del-proyecto-y-pruebas)
7. [Complejidad Algorítmica](#complejidad-algorítmica)

---

## Descripción General

El algoritmo de Dijkstra resuelve el problema del **camino más corto de origen único** (*Single-Source Shortest Path - SSSP*) en grafos ponderados cuyas aristas poseen costos no negativos ($w(u, v) \ge 0$).

Esta implementación utiliza:
- **Listas de adyacencia** mediante diccionarios y `dataclasses` para representar el grafo de forma clara y eficiente en memoria.
- **Cola de prioridad (`heapq` / Min-Heap)** para seleccionar en cada iteración el vértice no visitado con menor distancia acumulada.
- **Reconstrucción de caminos (*backtracking*)** mediante un mapa de nodos predecesores.

---

## Estructura del Proyecto

```text
dijkstra-project/
├── src/
│   ├── __init__.py          # Inicializador del paquete principal
│   ├── grafo.py             # Definición de las clases Arista y Grafo
│   ├── dijkstra.py          # Implementación de ejecutar_dijkstra y ResultadoDijkstra
│   └── visualizador.py      # Módulo reservado para visualización del grafo
├── tests/
│   └── test_dijkstra.py     # Pruebas unitarias automatizadas con pytest
├── main.py                  # Script principal de demostración y validación manual
├── pytest.ini               # Configuración de rutas para pytest
├── requirements.txt         # Dependencias del proyecto
└── README.md                # Documentación general del proyecto
```

---

## Explicación de los Componentes

### 1. `src/grafo.py`
Modela la estructura de la red:
- **`Arista`**: Clase de datos (`@dataclass`) que almacena el nodo `destino` (`str`) y el `peso` (`float`) de una conexión dirigida.
- **`Grafo`**:
  - `adyacencia`: Diccionario `Dict[str, List[Arista]]` que mapea cada vértice con su lista de aristas salientes.
  - `agregar_vertice(vertice)`: Registra un nodo en el grafo si aún no existe.
  - `agregar_arista(origen, destino, peso, bidireccional=False)`: Crea la conexión entre dos nodos validando que el peso no sea negativo (`ValueError` si `peso < 0`).
  - `vertices`: Propiedad que retorna la lista de todos los nodos registrados.

### 2. `src/dijkstra.py`
Contiene el motor de búsqueda del camino óptimo:
- **`ResultadoDijkstra`**:
  - Almacena los diccionarios resultantes `distancias` y `predecesores` junto con el nodo `origen`.
  - `camino_hacia(destino)`: Reconstruye la ruta óptima desde el origen hasta el destino retrocediendo por el diccionario de predecesores. Si el nodo es inalcanzable, retorna `[]`.
  - `costo_hacia(destino)`: Retorna la distancia mínima acumulada hacia el destino (o `inf` si no hay conexión).
- **`ejecutar_dijkstra(grafo, origen)`**:
  - Inicializa todas las distancias en $\infty$ excepto la del nodo `origen` ($0.0$).
  - Utiliza un *Min-Heap* (`heapq`) con tuplas `(distancia_acumulada, nodo)` y un conjunto `visitados` para expandir los nodos de forma voraz (*greedy*) y relajar las aristas adyacentes.

### 3. `main.py`
Script ejecutable que construye el grafo de validación, ejecuta el algoritmo desde el nodo `A` hasta el nodo `E` e imprime en consola:
1. Las distancias mínimas desde `A` hacia todos los nodos.
2. El diccionario de predecesores.
3. La ruta óptima paso a paso (`A -> C -> B -> D -> E`).
4. El costo total acumulado (`10`).

### 4. `tests/test_dijkstra.py`
Pruebas unitarias con `pytest` que verifican tres escenarios clave:
- **`test_caso_base_convergente`**: Verifica que el algoritmo elija caminos intermedios más económicos (`A -> C -> B -> D -> E` con costo `10`) frente a caminos directos más costosos.
- **`test_rechazo_pesos_negativos`**: Comprueba que se lance `ValueError` al intentar añadir una arista con peso negativo.
- **`test_nodo_desconexo`**: Verifica que un nodo aislado (`Z`) tenga costo `inf` y camino vacío `[]`.

---

## Caso de Validación Manual

El grafo configurado en `main.py` cuenta con los siguientes nodos y aristas dirigidas:

| Origen | Destino | Peso |
| :---: | :---: | :---: |
| A | B | 4 |
| A | C | 2 |
| C | B | 1 |
| B | D | 5 |
| C | D | 8 |
| C | E | 10 |
| D | E | 2 |

### Resultado esperado desde `A` hacia `E`:
- **Distancias mínimas desde `A`**:
  - `A -> A`: `0.0`
  - `A -> C`: `2.0`
  - `A -> B`: `3.0` (vía `C`)
  - `A -> D`: `8.0` (vía `B`)
  - `A -> E`: `10.0` (vía `D`)
- **Predecesores**: `{'A': None, 'B': 'C', 'C': 'A', 'D': 'B', 'E': 'D'}`
- **Ruta óptima**: `A -> C -> B -> D -> E`
- **Costo total**: `10`

---

## Requisitos e Instalación

1. Asegúrate de tener **Python 3.10+** instalado.
2. (Opcional) Crea y activa un entorno virtual:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Instala las dependencias necesarias:
   ```powershell
   pip install -r requirements.txt
   ```

---

## Ejecución del Proyecto y Pruebas

### Ejecutar la validación manual en consola
```powershell
python main.py
```

Salida en consola:
```text
=======================================================
  VALIDACIÓN MANUAL - ALGORITMO DE DIJKSTRA (FASE 2)
=======================================================
Nodo origen  : A
Nodo destino : E

1. Distancias mínimas desde A:
   - A -> A: 0.0
   - A -> B: 3.0
   - A -> C: 2.0
   - A -> D: 8.0
   - A -> E: 10.0

2. Diccionario de predecesores:
   {'A': None, 'B': 'C', 'C': 'A', 'D': 'B', 'E': 'D'}

3. Ruta óptima:
   A -> C -> B -> D -> E

4. Costo total:
   10
=======================================================
```

### Ejecutar las pruebas unitarias con `pytest`
```powershell
pytest -v
```

---

## Complejidad Algorítmica

Sea $V$ el número de vértices y $E$ el número de aristas del grafo:
- **Complejidad Temporal**: $\mathcal{O}((V + E) \log V)$, debido al uso del *Min-Heap* (`heapq`) para extraer el mínimo y relajar aristas.
- **Complejidad Espacial**: $\mathcal{O}(V + E)$, correspondiente al almacenamiento de la lista de adyacencia, los diccionarios de distancias/predecesores y la cola de prioridad.
