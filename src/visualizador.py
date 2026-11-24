"""
Módulo de visualización gráfica e interactiva del Grafo y de la Ruta Óptima de Dijkstra.

Utiliza `PyVis` (basado en Vis.js) para generar un lienzo HTML interactivo donde el usuario
puede arrastrar los nodos con el mouse, hacer zoom y distinguir por colores:
- Nodo Origen (Verde)
- Nodo Destino (Naranja/Ámbar)
- Nodos Intermedios de la Ruta Óptima (Azul intenso)
- Nodos Fuera de la Ruta (Gris claro)
- Aristas Seleccionadas en el Camino Mínimo (Verde brillante y trazo grueso)
- Aristas No Seleccionadas (Gris suave y trazo delgado)
"""

# Importamos json para inyectar opciones de física y diseño visual en Vis.js
import json
# Importamos tipos de datos para documentar claramente los parámetros y retornos
from typing import Dict, List, Optional, Set, Tuple
# Importamos Network de pyvis para construir el grafo interactivo en HTML
from pyvis.network import Network
# Importamos nuestras clases del modelo y algoritmo
from src.grafo import Grafo
from src.dijkstra import ResultadoDijkstra


def obtener_aristas_de_ruta(camino: List[str], dirigido: bool = True) -> Set[Tuple[str, str]]:
    """
    Convierte una lista ordenada de nodos (ej. `['A', 'C', 'B', 'D', 'E']`) en un conjunto
    de pares `(u, v)` que representan los tramos consecutivos de la ruta óptima.

    Si el grafo es no dirigido (`dirigido=False`), incluye tanto `(u, v)` como `(v, u)`
    para que la arista se pinte sin importar el sentido en que fue registrada.

    Parámetros:
        camino (List[str]): Lista de vértices que conforman la ruta óptima desde el origen al destino.
        dirigido (bool): Indica si el grafo es dirigido (`True`) o no dirigido (`False`).

    Retorna:
        Set[Tuple[str, str]]: Conjunto de tuplas `(origen_tramo, destino_tramo)` pertenecientes al camino óptimo.
    """
    aristas_ruta: Set[Tuple[str, str]] = set()
    # Si el camino tiene menos de 2 nodos, no hay aristas que resaltar
    if len(camino) < 2:
        return aristas_ruta

    # Recorremos cada par consecutivo de nodos en la ruta: (camino[i], camino[i+1])
    for i in range(len(camino) - 1):
        u, v = camino[i], camino[i + 1]
        aristas_ruta.add((u, v))
        if not dirigido:
            # En grafos no dirigidos marcamos también el sentido inverso para asegurar la coincidencia visual
            aristas_ruta.add((v, u))

    return aristas_ruta


def generar_html_grafo_interactivo(
    grafo: Grafo,
    camino_optimo: Optional[List[str]] = None,
    origen: Optional[str] = None,
    destino: Optional[str] = None,
    resultado: Optional[ResultadoDijkstra] = None,
    altura_px: int = 520,
) -> str:
    """
    Construye y devuelve el código HTML de un grafo interactivo coloreando la ruta óptima de Dijkstra.

    Parámetros:
        grafo (Grafo): Instancia del grafo a visualizar.
        camino_optimo (Optional[List[str]]): Secuencia de nodos de la ruta mínima a resaltar.
        origen (Optional[str]): Identificador del nodo inicial (se colorea en verde).
        destino (Optional[str]): Identificador del nodo final (se colorea en naranja).
        resultado (Optional[ResultadoDijkstra]): Objeto de resultados para mostrar distancias en los tooltips.
        altura_px (int): Altura del lienzo interactivo en píxeles.

    Retorna:
        str: Cadena con el documento HTML completo listo para renderizarse en Streamlit o navegador.
    """
    camino_optimo = camino_optimo or []
    nodos_en_camino = set(camino_optimo)
    aristas_en_camino = obtener_aristas_de_ruta(camino_optimo, dirigido=grafo.dirigido)

    # Inicializamos la red de PyVis indicando si las aristas llevan flecha (directed=grafo.dirigido)
    red = Network(
        height=f"{altura_px}px",
        width="100%",
        directed=grafo.dirigido,
        bgcolor="#FFFFFF",
        font_color="#1E293B",
    )

    # 1. Agregamos todos los vértices (nodos) del grafo con colores según su rol en la ruta óptima
    for vertice in grafo.vertices:
        # Determinamos el color del nodo dependiendo de si es Origen, Destino, Intermedio óptimo o Normal
        if vertice == origen:
            color_fondo = "#16A34A"  # Verde esmeralda (Nodo Origen)
            color_borde = "#14532D"
            color_texto = "#FFFFFF"
            etiqueta_rol = "Nodo Origen"
        elif vertice == destino:
            color_fondo = "#EA580C"  # Naranja intenso (Nodo Destino)
            color_borde = "#7C2D12"
            color_texto = "#FFFFFF"
            etiqueta_rol = "Nodo Destino"
        elif vertice in nodos_en_camino:
            color_fondo = "#2563EB"  # Azul brillante (Nodo intermedio de la ruta óptima)
            color_borde = "#1E3A8A"
            color_texto = "#FFFFFF"
            etiqueta_rol = "En Ruta Óptima"
        else:
            color_fondo = "#E2E8F0"  # Gris claro (Nodo no seleccionado en la ruta)
            color_borde = "#64748B"
            color_texto = "#1E293B"
            etiqueta_rol = "No seleccionado"

        # Construimos el texto emergente (tooltip) al pasar el mouse sobre el nodo
        dist_nodo = (
            resultado.costo_hacia(vertice)
            if resultado is not None
            else None
        )
        texto_dist = (
            "∞ (Inalcanzable)"
            if dist_nodo == float("inf")
            else (f"{dist_nodo:g}" if dist_nodo is not None else "N/A")
        )
        tooltip_nodo = f"Nodo {vertice} (Distancia: {texto_dist})"

        red.add_node(
            vertice,
            label=vertice,
            title=tooltip_nodo,
            shape="circle",
            size=30,
            color={
                "background": color_fondo,
                "border": color_borde,
                "highlight": {"background": color_fondo, "border": "#0F172A"},
            },
            font={"color": color_texto, "size": 18, "face": "arial", "bold": True},
            borderWidth=3 if vertice in nodos_en_camino else 2,
        )

    # 2. Agregamos todas las aristas del grafo resaltando en color verde grueso las del camino óptimo
    for u, v, peso in grafo.obtener_aristas():
        es_arista_optima = (u, v) in aristas_en_camino

        if es_arista_optima:
            color_arista = "#16A34A"  # Verde brillante para los caminos seleccionados por Dijkstra
            grosor_arista = 5.5       # Línea gruesa para destacar el camino óptimo
        else:
            color_arista = "#94A3B8"  # Gris neutro para caminos descartados/no seleccionados
            grosor_arista = 2.0       # Línea delgada estándar

        etiqueta_peso = f"{peso:g}"
        sentido_txt = "→" if grafo.dirigido else "↔"
        tooltip_arista = f"{u} {sentido_txt} {v} (Peso: {etiqueta_peso})"

        red.add_edge(
            u,
            v,
            label=etiqueta_peso,
            title=tooltip_arista,
            color={"color": color_arista, "highlight": color_arista},
            width=grosor_arista,
            font={
                "size": 16,
                "color": "#14532D" if es_arista_optima else "#334155",
                "background": "#FFFFFF",
                "strokeWidth": 3,
                "strokeColor": "#FFFFFF",
                "align": "horizontal",
            },
            arrows="to" if grafo.dirigido else "",
        )

    # 3. Configuramos la física interactiva para que los nodos estén bien separados y sean fáciles de arrastrar
    opciones_vis = {
        "edges": {
            "smooth": {"type": "curvedCW", "roundness": 0.12},
            "arrowStrikethrough": False,
        },
        "physics": {
            "enabled": True,
            "barnesHut": {
                "gravitationalConstant": -3800,
                "centralGravity": 0.25,
                "springLength": 160,
                "springConstant": 0.04,
                "damping": 0.15,
                "avoidOverlap": 0.5,
            },
            "minVelocity": 0.75,
        },
        "interaction": {
            "hover": True,
            "navigationButtons": False,
            "keyboard": False,
        },
    }
    red.set_options(json.dumps(opciones_vis))

    # Retornamos el código HTML generado en memoria sin necesidad de dejar archivos basura en el proyecto
    return red.generate_html()
