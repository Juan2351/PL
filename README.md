# Proyecto: Algoritmo de Dijkstra en Python

Implementación modular, documentada y con interfaz gráfica interactiva del **Algoritmo de Dijkstra** para encontrar caminos más cortos desde un nodo origen hacia todos los demás nodos en un grafo **dirigido o no dirigido** con pesos no negativos.

---

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Explicación de los Componentes](#explicación-de-los-componentes)
4. [Caso de Validación Manual](#caso-de-validación-manual)
5. [Requisitos e Instalación](#requisitos-e-instalación)
6. [Ejecución del Proyecto (Consola, Interfaz Web y Pruebas)](#ejecución-del-proyecto-consola-interfaz-web-y-pruebas)
7. [Complejidad Algorítmica](#complejidad-algorítmica)

---

## Descripción General

El algoritmo de Dijkstra resuelve el problema del **camino más corto de origen único** (*Single-Source Shortest Path - SSSP*) en grafos ponderados cuyas aristas poseen costos no negativos ($w(u, v) \ge 0$).

Esta implementación incluye:
- **Listas de adyacencia** mediante diccionarios y `dataclasses` con soporte tanto para **grafos dirigidos** como **no dirigidos (doble vía)**.
- **Cola de prioridad (`heapq` / Min-Heap)** para seleccionar en cada iteración el vértice no visitado con menor distancia acumulada.
- **Reconstrucción de caminos (*backtracking*)** mediante un mapa de nodos predecesores.
- **Carga y exportación de topologías en formato JSON** desde la carpeta `data/`.
- **Interfaz Gráfica Interactiva (`Streamlit` + `PyVis`)**: Permite editar nodos, agregar/eliminar caminos, modificar pesos en vivo, alternar entre grafo dirigido y no dirigido, y visualizar el grafo resaltando en **color verde** los caminos seleccionados por la ruta óptima.

---

## Estructura del Proyecto

```text
dijkstra-project/
├── data/
│   ├── caso_estudio_informe.json          # Topología dirigida del caso analítico del informe
│   └── red_logistica_no_dirigida.json     # Topología no dirigida (doble vía) de ejemplo
├── src/
│   ├── grafo.py                           # Definición de Arista, Grafo y carga/exportación JSON
│   ├── dijkstra.py                        # Implementación de ejecutar_dijkstra y ResultadoDijkstra
│   └── visualizador.py                    # Generador del grafo interactivo con ruta coloreada (PyVis)
├── tests/
│   └── test_dijkstra.py                   # Pruebas unitarias automatizadas con pytest
├── .gitignore                             # Archivos y carpetas ignorados por Git
├── app.py                                 # Interfaz gráfica interactiva (Dashboard en Streamlit)
├── main.py                                # Script principal de validación en consola y lanzador de UI
├── pytest.ini                             # Configuración de rutas para pytest
├── requirements.txt                       # Dependencias del proyecto
└── README.md                              # Documentación general del proyecto
```

---

## Explicación de los Componentes

### 1. `src/grafo.py`
Modela la estructura de la red:
- **`Arista`**: Clase de datos (`@dataclass`) que almacena el nodo `destino` (`str`) y el `peso` (`float`) de una conexión.
- **`Grafo`**:
  - `adyacencia`: Diccionario `Dict[str, List[Arista]]` que mapea cada vértice con su lista de aristas salientes.
  - `dirigido`: Atributo booleano (`True` para aristas de un solo sentido, `False` para aristas bidireccionales).
  - `agregar_vertice(vertice)`: Registra un nodo en el grafo si aún no existe.
  - `agregar_arista(origen, destino, peso, bidireccional=False)`: Crea o actualiza la conexión entre dos nodos validando que el peso no sea negativo (`ValueError` si `peso < 0`).
  - `cargar_desde_json(ruta_archivo)` y `desde_diccionario(datos)`: Permiten cargar topologías dinámicamente desde archivos `.json`.

### 2. `src/dijkstra.py`
Contiene el motor de búsqueda del camino óptimo:
- **`ResultadoDijkstra`**:
  - Almacena los diccionarios resultantes `distancias` y `predecesores` junto con el nodo `origen`.
  - `camino_hacia(destino)`: Reconstruye la ruta óptima desde el origen hasta el destino retrocediendo por el diccionario de predecesores. Si el nodo es inalcanzable, retorna `[]`.
  - `costo_hacia(destino)`: Retorna la distancia mínima acumulada hacia el destino (o `inf` si no hay conexión).
- **`ejecutar_dijkstra(grafo, origen)`**:
  - Inicializa todas las distancias en $\infty$ excepto la del nodo `origen` ($0.0$).
  - Utiliza un *Min-Heap* (`heapq`) con tuplas `(distancia_acumulada, nodo)` y un conjunto `visitados` para expandir los nodos de forma voraz (*greedy*) y relajar las aristas adyacentes.

### 3. `src/visualizador.py` y `app.py` (Interfaz Gráfica UI/UX)
- **`src/visualizador.py`**: Utiliza `PyVis` para dibujar el grafo interactivo, coloreando en **verde esmeralda** el nodo origen, en **naranja** el nodo destino, en **azul** los nodos intermedios y en **verde grueso** las aristas seleccionadas por el camino óptimo.
- **`app.py`**: Divide la interfaz web en dos columnas:
  - **Panel Izquierdo (Lógica y Configuración):** Permite alternar entre *Dirigido* y *No Dirigido*, cargar plantillas JSON, agregar nuevos caminos, editar pesos existentes en tiempo real, eliminar aristas o agregar nodos aislados.
  - **Panel Derecho (Salida Visual y Analítica):** Permite elegir el nodo origen y destino, muestra el grafo interactivo con los caminos óptimos coloreados, el costo total mínimo y la tabla completa de distancias y predecesores.

### 4. `tests/test_dijkstra.py`
Suite de 6 pruebas unitarias con `pytest`:
- **`test_caso_base_convergente`**: Verifica el camino óptimo (`A -> C -> B -> D -> E`, costo `10`) en el grafo dirigido del informe.
- **`test_grafo_no_dirigido_bidireccional`**: Comprueba que en grafos no dirigidos las aristas puedan recorrerse en ambos sentidos.
- **`test_rechazo_pesos_negativos`**: Verifica que se lance `ValueError` ante pesos negativos.
- **`test_nodo_desconexo`**: Comprueba que un nodo aislado (`Z`) tenga costo `inf` y camino vacío `[]`.
- **`test_carga_desde_json`**: Valida la carga dinámica desde `data/caso_estudio_informe.json`.
- **`test_visualizador_resalta_aristas_ruta_optima`**: Verifica la identificación y coloreado de los tramos óptimos.

---

## Caso de Validación Manual

El grafo por defecto configurado en `main.py` y en `data/caso_estudio_informe.json` cuenta con las siguientes aristas dirigidas:

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
- **Distancias mínimas desde `A`**: `{'A': 0.0, 'B': 3.0, 'C': 2.0, 'D': 8.0, 'E': 10.0}`
- **Predecesores**: `{'A': None, 'B': 'C', 'C': 'A', 'D': 'B', 'E': 'D'}`
- **Ruta óptima**: `A -> C -> B -> D -> E`
- **Costo total**: `10`

---

## Requisitos e Instalación

1. Asegúrate de tener **Python 3.10+** instalado.
2. Activa tu entorno virtual:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
3. Instala las dependencias necesarias:
   ```powershell
   pip install -r requirements.txt
   ```

---

## Ejecución del Proyecto (Consola, Interfaz Web y Pruebas)

### 1. Abrir la Interfaz Gráfica Interactiva (Recomendado para la entrega final)
```powershell
streamlit run app.py
```
*(O también puedes ejecutar `python main.py --ui`)*.

### 2. Ejecutar la validación rápida en consola
```powershell
python main.py
```

### 3. Ejecutar las pruebas unitarias con `pytest`
```powershell
pytest -v
```

---

## Complejidad Algorítmica

Sea $V$ el número de vértices y $E$ el número de aristas del grafo:
- **Complejidad Temporal**: $\mathcal{O}((V + E) \log V)$, debido al uso del *Min-Heap* (`heapq`) para extraer el mínimo y relajar aristas.
- **Complejidad Espacial**: $\mathcal{O}(V + E)$, correspondiente al almacenamiento de la lista de adyacencia, los diccionarios de distancias/predecesores y la cola de prioridad.
