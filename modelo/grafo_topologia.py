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
        self.tipos_dispositivo = ["PC", "Servidor", "IoT", "Impresora"]

    def generar_topologia(self, topologia: str) -> None:
        """
        Genera 40 nodos en la topología elegida y asigna telemetría aleatoria.

        Args:
            topologia (str): Tipo de topología: Estrella, Árbol o Malla.

        Raises:
            ValueError: Si se solicita un tipo de topología no soportado.
        """
        if topologia == "Estrella":
            grafo_generado = nx.star_graph(39)
        elif topologia == "Árbol":
            semilla = random.randint(0, 2**32 - 1)
            grafo_generado = nx.random_labeled_tree(40, seed=semilla)
        elif topologia == "Malla":
            grafo_generado = nx.grid_2d_graph(5, 8)
        else:
            raise ValueError("La topología debe ser Estrella, Árbol o Malla.")

        etiquetas = {
            nodo: f"N{indice}"
            for indice, nodo in enumerate(grafo_generado.nodes, start=1)
        }
        grafo_generado = nx.relabel_nodes(grafo_generado, etiquetas)

        self.grafo.clear()
        self.grafo.add_nodes_from(grafo_generado.nodes)
        self.grafo.add_edges_from(
            (origen, destino, {"peso": random.randint(1, 10)})
            for origen, destino in grafo_generado.edges
        )

        for datos in self.grafo.nodes.values():
            trafico = random.randint(0, 100)
            cpu = random.randint(0, 100)
            datos.update(
                tipo=random.choice(self.tipos_dispositivo),
                trafico=trafico,
                cpu=cpu,
                activo=True,
                estado="Anómalo" if cpu > 90 or trafico > 90 else "Normal",
            )

        self.grafo.nodes["N1"]["tipo"] = "Servidor"
        self.bloquear_nodos_aleatorios(cantidad=2, excluir={"N1"})

    def bloquear_nodo(self, nodo_id: str) -> bool:
        """
        Desactiva un equipo sin eliminarlo ni quitar sus enlaces del grafo.
        """
        if nodo_id in self.grafo:
            self.grafo.nodes[nodo_id].update(activo=False, estado="Bloqueado")
            return True
        return False

    def bloquear_nodos_aleatorios(
        self,
        cantidad: int = 2,
        excluir: set[str] | None = None,
    ) -> list[str]:
        """Bloquea nodos elegidos al azar, omitiendo los identificadores excluidos."""
        nodos = [
            nodo_id
            for nodo_id in self.grafo.nodes
            if excluir is None or nodo_id not in excluir
        ]
        if cantidad < 0 or cantidad > len(nodos):
            raise ValueError("La cantidad debe estar entre cero y el número de nodos.")

        nodos_seleccionados = random.sample(nodos, cantidad)
        for nodo_id in nodos_seleccionados:
            self.bloquear_nodo(nodo_id)
        return nodos_seleccionados

    def obtener_ruta_activa(self, origen: str, destino: str) -> list[str] | None:
        """
        Busca la ruta más corta entre nodos activos, evitando nodos bloqueados.

        Args:
            origen: Identificador del nodo inicial.
            destino: Identificador del nodo final.

        Returns:
            La secuencia de nodos de la ruta, o None si no hay ruta alternativa.

        Raises:
            ValueError: Si el origen o destino no existe o está inactivo.
        """
        for nodo_id, nombre in ((origen, "origen"), (destino, "destino")):
            if nodo_id not in self.grafo:
                raise ValueError(f"El nodo de {nombre} {nodo_id} no existe.")
            if not self.grafo.nodes[nodo_id].get("activo", True):
                raise ValueError(f"El nodo de {nombre} {nodo_id} está inactivo.")

        nodos_activos = [
            nodo_id
            for nodo_id, datos in self.grafo.nodes(data=True)
            if datos.get("activo", True)
        ]
        grafo_activo = self.grafo.subgraph(nodos_activos)

        try:
            return nx.shortest_path(grafo_activo, origen, destino)
        except nx.NetworkXNoPath:
            return None

    def obtener_datos_nodos(self) -> dict:
        """Retorna un diccionario con la información de todos los vértices."""
        return dict(self.grafo.nodes(data=True))