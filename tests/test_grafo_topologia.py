from unittest.mock import patch

import networkx as nx
import pytest

from modelo.grafo_topologia import GrafoRed


@pytest.mark.parametrize(
    ("topologia", "cantidad_aristas"),
    [
        ("Estrella", 39),
        ("Árbol", 39),
        ("Malla", 67),
    ],
)
def test_generar_topologia_asigna_nodos_atributos_y_bloqueos(
    topologia: str,
    cantidad_aristas: int,
) -> None:
    grafo_red = GrafoRed()
    with patch(
        "modelo.grafo_topologia.random.sample",
        side_effect=lambda nodos, cantidad: list(nodos)[-cantidad:],
    ):
        grafo_red.generar_topologia(topologia)

    grafo = grafo_red.grafo
    assert grafo.number_of_nodes() == 40
    assert grafo.number_of_edges() == cantidad_aristas
    assert nx.is_connected(grafo)
    assert grafo.nodes["N1"]["tipo"] == "Servidor"

    bloqueados = [
        nodo for nodo, datos in grafo.nodes(data=True)
        if datos["estado"] == "Bloqueado"
    ]
    assert len(bloqueados) == 2
    assert "N1" not in bloqueados

    for nodo, datos in grafo.nodes(data=True):
        assert datos["tipo"] in {"PC", "Servidor", "IoT", "Impresora"}
        assert 0 <= datos["trafico"] <= 100
        assert 0 <= datos["cpu"] <= 100
        assert datos["activo"] is (nodo not in bloqueados)
        if nodo in bloqueados:
            assert grafo.degree(nodo) > 0

    assert all("peso" in datos for _, _, datos in grafo.edges(data=True))


def test_bloquear_nodo_lo_marca_inactivo_sin_quitarlo_ni_eliminar_enlaces() -> None:
    grafo_red = GrafoRed()
    grafo_red.grafo.add_edge("N1", "N2", peso=5)
    grafo_red.grafo.nodes["N2"].update(activo=True, estado="Normal")

    exito = grafo_red.bloquear_nodo("N2")

    assert exito is True
    assert "N2" in grafo_red.grafo
    assert grafo_red.grafo.has_edge("N1", "N2")
    assert grafo_red.grafo.nodes["N2"]["activo"] is False
    assert grafo_red.grafo.nodes["N2"]["estado"] == "Bloqueado"


def test_bloquear_nodo_inexistente_devuelve_false() -> None:
    grafo_red = GrafoRed()

    assert grafo_red.bloquear_nodo("N99") is False


def test_ruta_activa_evade_nodo_bloqueado() -> None:
    grafo_red = GrafoRed()
    grafo_red.grafo.add_edges_from(
        [("N1", "N2"), ("N2", "N4"), ("N1", "N3"), ("N3", "N4")]
    )
    for nodo in grafo_red.grafo:
        grafo_red.grafo.nodes[nodo]["activo"] = True
    grafo_red.bloquear_nodo("N2")

    ruta = grafo_red.obtener_ruta_activa("N1", "N4")

    assert ruta == ["N1", "N3", "N4"]
    assert grafo_red.grafo.has_edge("N1", "N2")


def test_ruta_activa_devuelve_none_si_no_hay_camino_alternativo() -> None:
    grafo_red = GrafoRed()
    grafo_red.grafo.add_edges_from([("N1", "N2"), ("N2", "N3")])
    for nodo in grafo_red.grafo:
        grafo_red.grafo.nodes[nodo]["activo"] = True
    grafo_red.bloquear_nodo("N2")

    assert grafo_red.obtener_ruta_activa("N1", "N3") is None


@pytest.mark.parametrize(
    ("origen", "destino"),
    [("N99", "N1"), ("N1", "N99")],
)
def test_ruta_activa_rechaza_extremos_inexistentes(
    origen: str,
    destino: str,
) -> None:
    grafo_red = GrafoRed()
    grafo_red.grafo.add_node("N1", activo=True)

    with pytest.raises(ValueError, match="no existe"):
        grafo_red.obtener_ruta_activa(origen, destino)


def test_ruta_activa_rechaza_extremo_inactivo() -> None:
    grafo_red = GrafoRed()
    grafo_red.grafo.add_edge("N1", "N2")
    grafo_red.grafo.nodes["N1"]["activo"] = False
    grafo_red.grafo.nodes["N2"]["activo"] = True

    with pytest.raises(ValueError, match="inactivo"):
        grafo_red.obtener_ruta_activa("N1", "N2")


def test_topologia_desconocida_lanza_error() -> None:
    with pytest.raises(ValueError, match="topología"):
        GrafoRed().generar_topologia("Anillo")
