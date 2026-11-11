import pytest

from modelo.automata_validador import AutomataRed


@pytest.mark.parametrize(
    ("cadena", "traza_esperada"),
    [
        ("SAF", ["q0", "q1", "q2", "qF"]),
        ("SADF", ["q0", "q1", "q2", "q3", "qF"]),
        ("SADDDF", ["q0", "q1", "q2", "q3", "q3", "q3", "qF"]),
    ],
)
def test_acepta_protocolos_validos(
    cadena: str,
    traza_esperada: list[str],
) -> None:
    automata = AutomataRed()

    aceptada, traza = automata.validar_cadena(cadena)

    assert aceptada is True
    assert traza == traza_esperada


@pytest.mark.parametrize(
    ("cadena", "traza_esperada"),
    [
        ("", ["q0"]),
        ("SA", ["q0", "q1", "q2"]),
        ("A", ["q0", "qerr"]),
        ("SAE", ["q0", "q1", "q2", "qerr"]),
        ("SAX", ["q0", "q1", "q2", "qerr"]),
        ("SAFD", ["q0", "q1", "q2", "qF", "qerr"]),
    ],
)
def test_rechaza_protocolos_invalidos(
    cadena: str,
    traza_esperada: list[str],
) -> None:
    automata = AutomataRed()

    aceptada, traza = automata.validar_cadena(cadena)

    assert aceptada is False
    assert traza == traza_esperada
