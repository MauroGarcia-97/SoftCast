import networkx as nx
import random
from typing import Dict, Any

class GrafoRed:
    """
    Clase encargada de gestionar la topología matemática de la red SoftCast.
    Representa el grafo G = (V, E) donde V son los dispositivos y E los enlaces.
    """

    def __init__(self):
        """Inicializa el grafo no dirigido vacío y los parámetros de simulación."""
        self.grafo = nx.Graph()
        self.tipos_dispositivo = ["PC", "Servidor", "IoT"]

    def generar_topologia(self, num_nodos: int = 8) -> None:
        """
        Construye la red inyectando nodos con telemetría aleatoria y aristas.

        Args:
            num_nodos (int): Cantidad de dispositivos a simular en la red.
        """
        self.grafo.clear()  # Limpiar cualquier topología previa

        # 1. Generación de Vértices (Nodos) y sus características
        for i in range(1, num_nodos + 1):
            nodo_id = f"N{i}"
            tipo = random.choice(self.tipos_dispositivo)
            trafico = random.randint(10, 100)
            cpu = random.randint(10, 100)

            # Etiquetado base: CPU > 90 o Tráfico > 90 se considera Anómalo
            estado_inicial = "Anómalo" if cpu > 90 or trafico > 90 else "Normal"

            # Se inyecta el diccionario de datos al nodo (Preparación para GNN)
            self.grafo.add_node(
                nodo_id,
                tipo=tipo,
                trafico=trafico,
                cpu=cpu,
                estado=estado_inicial
            )

        # 2. Generación de Aristas (Enlaces) para asegurar conectividad
        for i in range(2, num_nodos + 1):
            # Conecta el nodo actual con uno anterior aleatorio para evitar grafos disconexos
            nodo_destino = f"N{random.randint(1, i-1)}"
            peso_enlace = random.randint(1, 10)
            self.grafo.add_edge(f"N{i}", nodo_destino, peso=peso_enlace)

    def bloquear_nodo(self, nodo_id: str) -> bool:
        """
        Simula la caída o bloqueo de un equipo en la red.
        Aísla el nodo eliminando todas sus aristas conectadas y actualiza su estado.
        """
        if nodo_id in self.grafo:
            aristas_a_eliminar = list(self.grafo.edges(nodo_id))
            self.grafo.remove_edges_from(aristas_a_eliminar)
            self.grafo.nodes[nodo_id]['estado'] = "Bloqueado"
            return True
        return False

    def obtener_datos_nodos(self) -> dict:
        """Retorna un diccionario con la información de todos los vértices."""
        return dict(self.grafo.nodes(data=True))