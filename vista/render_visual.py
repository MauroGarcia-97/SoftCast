import networkx as nx
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

class RenderizadorGrafo:
    """
    Clase especializada en tomar la estructura matemática de NetworkX
    y traducirla en variables visuales (colores, tamaños, posiciones).
    """

    @staticmethod
    def dibujar_red(
        grafo: nx.Graph,
        figura: Figure,
        canvas: FigureCanvasTkAgg,
        ruta: list[str] | None = None,
    ) -> None:
        """
        Dibuja la topología de la red en la figura de Matplotlib embebida.

        Args:
            grafo (nx.Graph): El grafo matemático a renderizar.
            figura (Figure): El contenedor gráfico de Matplotlib.
            canvas (FigureCanvasTkAgg): El lienzo de Tkinter que muestra la figura.
            ruta (list[str] | None): Camino que se resalta en azul, si se proporciona.
        """
        if figura.axes:
            ax = figura.axes[0]
            ax.clear()
        else:
            ax = figura.add_subplot(111)
        ax.set_title("Topología de Red SoftCast (En Vivo)", fontsize=14, fontweight='bold')

        if len(grafo.nodes) == 0:
            canvas.draw()
            return

        # 1. Layout Espacial (Algoritmo de fuerza dirigida - resortes)
        posiciones = nx.spring_layout(grafo, seed=42)

        # 2. Mapeo de Variables Visuales (Semántica de Color)
        colores_nodos = []
        etiquetas_nodos = {}

        for nodo, datos in grafo.nodes(data=True):
            estado = datos.get('estado', 'Normal')

            # Código de colores según el estado dictado por el Modelo (IA/Simulación)
            if estado == 'Anómalo':
                colores_nodos.append('#FFA500') # Naranja para anomalías
            elif estado == 'Bloqueado':
                colores_nodos.append('#FF0000') # Rojo para equipos bloqueados
            else:
                colores_nodos.append('#008000') # Verde para operación normal

            # Etiqueta visible en pantalla (ID + CPU)
            etiquetas_nodos[nodo] = f"{nodo}\n{datos.get('tipo', '')}\nCPU:{datos.get('cpu', 0)}%"

        aristas_ruta = {
            frozenset((origen, destino))
            for origen, destino in zip(ruta or (), (ruta or ())[1:])
        }
        aristas = list(grafo.edges)
        colores_aristas = [
            '#0066FF' if frozenset(arista) in aristas_ruta else '#A0A0A0'
            for arista in aristas
        ]
        anchos_aristas = [
            3.0 if frozenset(arista) in aristas_ruta else 1.5
            for arista in aristas
        ]

        # 3. Renderizado Geométrico
        nx.draw(
            grafo,
            pos=posiciones,
            ax=ax,
            with_labels=True,
            labels=etiquetas_nodos,
            node_color=colores_nodos,
            node_size=2500,
            font_size=8,
            font_weight='bold',
            font_color='white',
            edge_color=colores_aristas,
            width=anchos_aristas,
        )

        # 4. Actualizar el lienzo en pantalla
        canvas.draw()