from unittest.mock import Mock

import networkx as nx
import pytest

from controlador.orquestador import ControladorPrincipal
from modelo.automata_validador import AutomataRed
from modelo.grafo_topologia import GrafoRed
from vista.ventana_principal import InterfazSoftCast


@pytest.fixture
def dependencias() -> tuple[Mock, Mock, Mock, ControladorPrincipal]:
    modelo_grafo = Mock(spec=GrafoRed)
    modelo_grafo.grafo = nx.Graph()
    modelo_automata = Mock(spec=AutomataRed)
    vista = Mock(spec=InterfazSoftCast)
    controlador = ControladorPrincipal(modelo_grafo, modelo_automata, vista)
    return modelo_grafo, modelo_automata, vista, controlador


def test_generar_red_delega_topologia_y_actualiza_vista(dependencias) -> None:
    modelo_grafo, _, vista, controlador = dependencias
    modelo_grafo.grafo.add_nodes_from(["N1", "N2"])

    controlador.manejar_generacion_red("Malla")

    modelo_grafo.generar_topologia.assert_called_once_with("Malla")
    vista.actualizar_grafo.assert_called_once_with(modelo_grafo.grafo)
    assert controlador.red_iniciada is True


def test_bloqueo_manual_actualiza_grafo(dependencias) -> None:
    modelo_grafo, _, vista, controlador = dependencias
    controlador.red_iniciada = True
    modelo_grafo.bloquear_nodo.return_value = True

    controlador.manejar_bloqueo_nodo("N2")

    modelo_grafo.bloquear_nodo.assert_called_once_with("N2")
    vista.actualizar_grafo.assert_called_once_with(modelo_grafo.grafo)
    vista.registrar_log.assert_called_once()


def test_bloqueo_antes_de_generar_red_muestra_alerta(dependencias) -> None:
    modelo_grafo, _, vista, controlador = dependencias

    controlador.manejar_bloqueo_nodo("N2")

    vista.mostrar_alerta.assert_called_once()
    modelo_grafo.bloquear_nodo.assert_not_called()


def test_calcular_ruta_resalta_la_ruta_en_la_vista(dependencias) -> None:
    modelo_grafo, _, vista, controlador = dependencias
    controlador.red_iniciada = True
    modelo_grafo.obtener_ruta_activa.return_value = ["N1", "N3", "N4"]

    controlador.manejar_calculo_ruta("N1", "N4")

    modelo_grafo.obtener_ruta_activa.assert_called_once_with("N1", "N4")
    vista.actualizar_grafo.assert_called_once_with(
        modelo_grafo.grafo,
        ["N1", "N3", "N4"],
    )


def test_calcular_ruta_sin_camino_registra_alerta(dependencias) -> None:
    modelo_grafo, _, vista, controlador = dependencias
    controlador.red_iniciada = True
    modelo_grafo.obtener_ruta_activa.return_value = None

    controlador.manejar_calculo_ruta("N1", "N4")

    vista.registrar_log.assert_called_once()
    assert vista.registrar_log.call_args.args[1] == "ALERTA"
    vista.actualizar_grafo.assert_not_called()


def test_calcular_ruta_con_extremo_invalido_muestra_alerta(dependencias) -> None:
    modelo_grafo, _, vista, controlador = dependencias
    controlador.red_iniciada = True
    modelo_grafo.obtener_ruta_activa.side_effect = ValueError("El nodo de origen N99 no existe.")

    controlador.manejar_calculo_ruta("N99", "N4")

    vista.mostrar_alerta.assert_called_once()
    vista.actualizar_grafo.assert_not_called()


def test_validar_protocolo_delega_al_automata(dependencias) -> None:
    _, modelo_automata, vista, controlador = dependencias
    controlador.red_iniciada = True
    modelo_automata.validar_cadena.return_value = (True, ["q0", "q1", "q2", "qF"])

    controlador.manejar_validacion_ruta("SAF")

    modelo_automata.validar_cadena.assert_called_once_with("SAF")
    assert vista.registrar_log.call_count == 3
