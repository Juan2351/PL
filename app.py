"""
Interfaz gráfica web para el proyecto del Algoritmo de Dijkstra.

Actúa como la capa de Vista/Controlador sobre los módulos de `src/`:
- Columna izquierda: Configuración del grafo (plantillas JSON, modo dirigido/no dirigido,
  registro, edición y eliminación de caminos).
- Columna derecha: Selección de origen y destino, visualización del grafo con la ruta
  óptima resaltada en color verde y tabla de resultados (distancias y predecesores).
"""

from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

from src.grafo import Grafo
from src.dijkstra import ejecutar_dijkstra
from src.visualizador import generar_html_grafo_interactivo

# Carpeta donde se almacenan los archivos JSON de prueba
CARPETA_DATA = Path(__file__).resolve().parent / "data"


def cargar_json_en_sesion(ruta_archivo: Path) -> None:
    """
    Lee un archivo JSON de la carpeta `data/` y guarda sus datos en la sesión de la interfaz.
    """
    _, datos = Grafo.cargar_desde_json(ruta_archivo)
    st.session_state["dirigido"] = bool(datos.get("dirigido", True))
    st.session_state["aristas"] = [
        {
            "origen": str(a["origen"]).strip(),
            "destino": str(a["destino"]).strip(),
            "peso": float(a["peso"]),
        }
        for a in datos.get("aristas", [])
    ]
    st.session_state["origen_sel"] = str(datos.get("origen_por_defecto", "A"))
    st.session_state["destino_sel"] = str(datos.get("destino_por_defecto", "E"))


def inicializar_sesion() -> None:
    """
    Carga por defecto el caso de estudio del informe cuando se abre la aplicación por primera vez.
    """
    if "aristas" not in st.session_state:
        cargar_json_en_sesion(CARPETA_DATA / "caso_estudio_informe.json")


def construir_grafo() -> Grafo:
    """
    Crea y retorna el objeto `Grafo` con las aristas y el modo configurados en pantalla.
    """
    grafo = Grafo(dirigido=st.session_state["dirigido"])
    for item in st.session_state["aristas"]:
        grafo.agregar_arista(
            origen=item["origen"],
            destino=item["destino"],
            peso=float(item["peso"]),
            bidireccional=not st.session_state["dirigido"],
        )
    return grafo


def main() -> None:
    """
    Renderiza la ventana principal dividida en panel de configuración y panel de resultados.
    """
    st.set_page_config(page_title="Algoritmo de Dijkstra", layout="wide")
    inicializar_sesion()

    st.title("Algoritmo de Dijkstra - Optimización de Redes")
    st.write("Programación Lineal | Facultad de Ingeniería - Universidad Libre")
    st.divider()

    # Dividimos la pantalla en dos columnas: Izquierda (Configuración) y Derecha (Salida)
    col_izquierda, col_derecha = st.columns([1, 1.4], gap="large")

    # =========================================================================
    # COLUMNA IZQUIERDA: CONFIGURACIÓN DE NODOS, PESOS Y TIPO DE GRAFO
    # =========================================================================
    with col_izquierda:
        st.subheader("Configuración del Grafo")

        # 1. Selector de modo de carga: plantillas JSON o crear un grafo nuevo desde cero
        archivos_json = sorted(CARPETA_DATA.glob("*.json"))
        mapa_archivos = {archivo.name: archivo for archivo in archivos_json}
        opciones_topologia = ["Crear grafo nuevo desde cero"] + list(mapa_archivos.keys())

        col_archivo, col_boton_cargar = st.columns([2, 1])
        with col_archivo:
            seleccion_topologia = st.selectbox(
                "Plantilla o grafo en blanco:",
                options=opciones_topologia,
                index=1 if len(opciones_topologia) > 1 else 0,
            )
        with col_boton_cargar:
            st.write("")
            st.write("")
            if st.button("Aplicar", use_container_width=True):
                if seleccion_topologia == "Crear grafo nuevo desde cero":
                    st.session_state["aristas"] = []
                    st.session_state["origen_sel"] = ""
                    st.session_state["destino_sel"] = ""
                else:
                    cargar_json_en_sesion(mapa_archivos[seleccion_topologia])
                st.rerun()

        # 2. Selector entre Grafo Dirigido y No Dirigido
        tipo_grafo = st.radio(
            "Tipo de red:",
            options=["Dirigido (un sentido)", "No dirigido (doble sentido)"],
            index=0 if st.session_state["dirigido"] else 1,
            horizontal=True,
        )
        es_dirigido = tipo_grafo.startswith("Dirigido")
        if es_dirigido != st.session_state["dirigido"]:
            st.session_state["dirigido"] = es_dirigido
            st.rerun()

        st.divider()

        # 3. Formulario para agregar un nuevo camino o actualizar su peso
        st.markdown("**Agregar o actualizar camino**")
        with st.form("formulario_arista", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                nuevo_origen = st.text_input("Origen", placeholder="A")
            with c2:
                nuevo_destino = st.text_input("Destino", placeholder="B")
            with c3:
                nuevo_peso = st.number_input("Peso", min_value=0.0, value=1.0, step=1.0)

            if st.form_submit_button("Guardar camino", use_container_width=True):
                u = nuevo_origen.strip()
                v = nuevo_destino.strip()
                if not u or not v:
                    st.warning("Ingrese tanto el nodo origen como el nodo destino.")
                elif u == v:
                    st.warning("El nodo origen y el destino deben ser diferentes.")
                else:
                    # Si el camino ya existe, actualizamos su peso; si no, lo agregamos a la lista
                    existe = False
                    for arista in st.session_state["aristas"]:
                        if arista["origen"] == u and arista["destino"] == v:
                            arista["peso"] = float(nuevo_peso)
                            existe = True
                            break
                    if not existe:
                        st.session_state["aristas"].append(
                            {"origen": u, "destino": v, "peso": float(nuevo_peso)}
                        )
                    st.rerun()

        # 4. Lista de caminos actuales para editar pesos o eliminar
        st.markdown("**Caminos registrados**")
        flecha = "->" if st.session_state["dirigido"] else "<->"

        for i, arista in enumerate(st.session_state["aristas"]):
            col_tramo, col_peso, col_eliminar = st.columns([1.5, 1.5, 1])
            with col_tramo:
                st.write(f"**{arista['origen']} {flecha} {arista['destino']}**")
            with col_peso:
                peso_actualizado = st.number_input(
                    "Peso",
                    min_value=0.0,
                    value=float(arista["peso"]),
                    step=1.0,
                    key=f"peso_{i}",
                    label_visibility="collapsed",
                )
                if peso_actualizado != arista["peso"]:
                    st.session_state["aristas"][i]["peso"] = float(peso_actualizado)
                    st.rerun()
            with col_eliminar:
                if st.button("Eliminar", key=f"eliminar_{i}", use_container_width=True):
                    st.session_state["aristas"].pop(i)
                    st.rerun()

    # =========================================================================
    # COLUMNA DERECHA: VISUALIZACIÓN DEL GRAFO Y RESULTADOS DE DIJKSTRA
    # =========================================================================
    with col_derecha:
        st.subheader("Visualización y Resultados")

        grafo = construir_grafo()
        nodos = grafo.vertices

        if not nodos:
            st.info("Agregue al menos un camino en el panel izquierdo para visualizar el grafo.")
            return

        # Aseguramos que los nodos seleccionados en sesión sean válidos dentro de la lista actual de nodos
        if st.session_state.get("origen_sel") not in nodos:
            st.session_state["origen_sel"] = nodos[0]
        if st.session_state.get("destino_sel") not in nodos:
            st.session_state["destino_sel"] = nodos[-1]

        # Selectores de Nodo Origen y Nodo Destino vinculados directamente por `key` a session_state
        c_origen, c_destino = st.columns(2)
        with c_origen:
            origen = st.selectbox("Nodo Origen:", options=nodos, key="origen_sel")
        with c_destino:
            destino = st.selectbox("Nodo Destino:", options=nodos, key="destino_sel")

        # Ejecutamos el algoritmo de Dijkstra sobre el grafo construido
        resultado = ejecutar_dijkstra(grafo, origen)
        camino_optimo = resultado.camino_hacia(destino)
        costo_total = resultado.costo_hacia(destino)

        # Resumen de Ruta Óptima y Costo Total
        res1, res2 = st.columns([2.5, 1])
        with res1:
            if camino_optimo:
                st.success(f"Ruta óptima: {' -> '.join(camino_optimo)}")
            else:
                st.error(f"No existe ruta posible desde {origen} hacia {destino}.")
        with res2:
            valor_costo = "Infinito" if costo_total == float("inf") else f"{costo_total:g}"
            st.metric("Costo total mínimo", valor_costo)

        st.caption(
            "Colores en el grafo: Verde = Origen y caminos seleccionados | "
            "Azul = Nodos intermedios de la ruta | Naranja = Destino | Gris = No seleccionados"
        )

        # Renderizamos el grafo interactivo con los caminos seleccionados pintados de verde
        html_grafo = generar_html_grafo_interactivo(
            grafo=grafo,
            camino_optimo=camino_optimo,
            origen=origen,
            destino=destino,
            resultado=resultado,
            altura_px=450,
        )
        components.html(html_grafo, height=465, scrolling=False)

        # Tabla resumen de distancias mínimas y predecesores
        st.markdown("**Tabla de distancias mínimas y predecesores**")
        tabla = []
        for nodo in nodos:
            dist = resultado.distancias[nodo]
            tabla.append(
                {
                    "Nodo": nodo,
                    f"Distancia desde {origen}": "Infinito" if dist == float("inf") else f"{dist:g}",
                    "Predecesor": resultado.predecesores[nodo] or "Ninguno",
                    "Camino acumulado": " -> ".join(resultado.camino_hacia(nodo)) or "Sin camino",
                }
            )
        st.dataframe(tabla, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
