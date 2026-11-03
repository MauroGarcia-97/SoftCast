import networkx as nx
from typing import Dict, Any

class ClasificadorGNN:
    """
    Módulo de proyección para la Red Neuronal Basada en Grafos (GNN).
    Actúa como puente transformando la estructura de NetworkX en tensores matemáticos.
    """

    def __init__(self, grafo_referencia: nx.Graph):
        """
        Se acopla a la topología actual para extraer la matriz de características.
        """
        self.grafo = grafo_referencia

    def extraer_matriz_caracteristicas(self) -> Dict[str, Any]:
        """
        Simula la extracción de tensores (Node Features y Adjacency Matrix)
        que consumirán frameworks como PyTorch Geometric.
        """
        caracteristicas_tensor = []
        etiquetas_target = []

        for nodo, datos in self.grafo.nodes(data=True):
            # Extraemos Tráfico y CPU como vector de características (X)
            caracteristicas_tensor.append([datos.get('trafico', 0), datos.get('cpu', 0)])
            # Extraemos la etiqueta objetivo (Y)
            etiquetas_target.append(1 if datos.get('estado') == 'Anómalo' else 0)

        # La matriz de adyacencia (A)
        matriz_adyacencia = nx.adjacency_matrix(self.grafo).todense()

        return {
            "matriz_adyacencia": matriz_adyacencia,
            "caracteristicas_X": caracteristicas_tensor,
            "etiquetas_Y": etiquetas_target,
            "estado": "Datos formateados correctamente para ingesta de GNN."
        }