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
    def dibujar_red(grafo: nx.Graph, figura: Figure, canvas: FigureCanvasTkAgg) -> None:
        """
        Dibuja la topología de la red en la figura de Matplotlib embebida.

        Args:
            grafo (nx.Graph): El grafo matemático a renderizar.
            figura (Figure): El contenedor gráfico de Matplotlib.
            canvas (FigureCanvasTkAgg): El lienzo de Tkinter que muestra la figura.
        """
        figura.clf()  # Limpiar renderizados anteriores
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
                colores_nodos.append('#FF4C4C') # Rojo para anomalías
            elif estado == 'Bloqueado':
                colores_nodos.append('#808080') # Gris para equipos caídos
            else:
                colores_nodos.append('#4CAF50') # Verde para operación normal

            # Etiqueta visible en pantalla (ID + CPU)
            etiquetas_nodos[nodo] = f"{nodo}\n{datos.get('tipo', '')}\nCPU:{datos.get('cpu', 0)}%"

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
            edge_color='#A0A0A0',
            width=1.5
        )

        # 4. Actualizar el lienzo en pantalla
        canvas.draw()