# modelo/automata_validador.py
from typing import Tuple, List

class AutomataRed:
    """
    Autómata Finito Determinista (AFD) para validar el protocolo de comunicación.
    Formalización matemática: M = (Q, Sigma, delta, q0, F)
    """

    def __init__(self):
        """Define la quíntupla matemática estructural del AFD."""
        # Q: Conjunto de estados
        self.estados = {'q0', 'q1', 'q2', 'q3', 'qF', 'qerr'}
        
        # Sigma: Alfabeto permitido
        self.alfabeto = {'S', 'A', 'D', 'F', 'E'}
        
        # q0 y F: Estado inicial y subconjunto de estados finales
        self.estado_inicial = 'q0'
        self.estados_finales = {'qF'}
        
        # delta: Función de transición estricta (Diccionario de diccionarios)
        self.transiciones = {
            'q0': {'S': 'q1'},          # SYN -> Esperando ACK
            'q1': {'A': 'q2'},          # ACK -> Conexión establecida
            'q2': {'D': 'q3', 'F': 'qF'}, # DAT -> Transmitiendo, o FIN -> Cierre
            'q3': {'D': 'q3', 'F': 'qF'}  # Bucle de DAT o FIN -> Cierre
            # Cualquier símbolo 'E' o no definido enviará a 'qerr' lógicamente
        }

    def validar_cadena(self, cadena: str) -> Tuple[bool, List[str]]:
        """
        Procesa una secuencia de símbolos simulando una conexión de red.
        
        Args:
            cadena (str): Secuencia de caracteres del protocolo (ej. "SADF").
            
        Returns:
            Tuple[bool, List[str]]: (Es_Aceptada, Traza_de_estados)
        """
        estado_actual = self.estado_inicial
        traza = [estado_actual]
        
        for simbolo in cadena:
            # Si hay una interrupción (E) o el símbolo rompe la sintaxis de delta
            if simbolo == 'E' or simbolo not in self.transiciones.get(estado_actual, {}):
                estado_actual = 'qerr'
                traza.append(estado_actual)
                break  # Se rompe el ciclo porque cayó en estado de trampa
            
            # Salto al siguiente estado dictado por la función de transición
            estado_actual = self.transiciones[estado_actual][simbolo]
            traza.append(estado_actual)
            
        # Condición de aceptación: Terminar exactamente en un estado de F
        es_aceptada = estado_actual in self.estados_finales
        
        return es_aceptada, traza