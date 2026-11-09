from modelo.grafo_topologia import GrafoRed
from modelo.automata_validador import AutomataRed
from vista.ventana_principal import InterfazSoftCast

class ControladorPrincipal:
    """
    Clase orquestadora que implementa el patrón de diseño Mediador/Controlador.
    Enlaza los eventos de la UI con el procesamiento del Autómata y la Teoría de Grafos.
    """

    def __init__(self, modelo_grafo: GrafoRed, modelo_automata: AutomataRed, vista: InterfazSoftCast):
        """
        Inyecta las dependencias (Modelos y Vista) y configura los callbacks.

        Args:
            modelo_grafo (GrafoRed): Instancia del gestor topológico de red.
            modelo_automata (AutomataRed): Instancia del validador de protocolos.
            vista (InterfazSoftCast): Instancia de la interfaz gráfica del usuario.
        """
        self.modelo_grafo = modelo_grafo
        self.modelo_automata = modelo_automata
        self.vista = vista

        # Inyectar los métodos de este controlador hacia los botones de la vista
        self.vista.set_controladores(
            cb_generar=self.manejar_generacion_red,
            cb_bloquear=self.manejar_bloqueo_nodo,
            cb_validar=self.manejar_validacion_ruta,
            cb_calcular_ruta=self.manejar_calculo_ruta,
        )

        # Bandera de seguridad para evitar validaciones si no hay red
        self.red_iniciada = False

    def iniciar(self) -> None:
        """Punto de arranque del ciclo de vida de la aplicación."""
        self.vista.registrar_log("Sistema inicializado. Esperando generación de topología.", "ALERTA")
        self.vista.iniciar_loop()

    # ================= MÉTODOS DE LÓGICA DE NEGOCIO (CALLBACKS) =================

    def manejar_generacion_red(self, topologia: str) -> None:
        """Genera y muestra la red según la topología seleccionada."""
        self.vista.registrar_log(
            f"Generando topología de red: {topologia}.",
            "INFO",
        )
        self.modelo_grafo.generar_topologia(topologia)
        self.red_iniciada = True

        self.vista.actualizar_grafo(self.modelo_grafo.grafo)
        self.vista.registrar_log(
            f"Topología {topologia} generada exitosamente con "
            f"{self.modelo_grafo.grafo.number_of_nodes()} nodos.",
            "INFO",
        )

    def manejar_bloqueo_nodo(self, nodo_id: str) -> None:
        """
        Procesa la inyección de una falla manual en la red.

        Args:
            nodo_id (str): Identificador del equipo a aislar (Ej: 'N2').
        """
        if not self.red_iniciada:
            self.vista.mostrar_alerta("Acción Inválida", "Debe generar la red antes de bloquear un nodo.")
            return

        # El modelo intenta bloquear matemáticamente el nodo
        exito = self.modelo_grafo.bloquear_nodo(nodo_id)

        if exito:
            self.vista.registrar_log(
                f"Falla inyectada: el nodo {nodo_id} está inactivo y permanece en la red.",
                "ERROR",
            )
            self.vista.actualizar_grafo(self.modelo_grafo.grafo)
        else:
            self.vista.mostrar_alerta("Error 404", f"El nodo {nodo_id} no existe en la topología actual.")

    def manejar_calculo_ruta(self, origen: str, destino: str) -> None:
        """Calcula una ruta que evite los nodos inactivos."""
        if not self.red_iniciada:
            self.vista.mostrar_alerta(
                "Acción inválida",
                "Debe generar la red antes de calcular una ruta.",
            )
            return

        try:
            ruta = self.modelo_grafo.obtener_ruta_activa(origen, destino)
        except ValueError as error:
            self.vista.mostrar_alerta("Ruta no disponible", str(error))
            return

        if ruta is None:
            self.vista.registrar_log(
                f"No hay una ruta activa entre {origen} y {destino}; "
                "no existe un camino alternativo que evite los nodos inactivos.",
                "ALERTA",
            )
            return

        self.vista.registrar_log(
            f"Ruta activa de {origen} a {destino}: {' -> '.join(ruta)}.",
            "INFO",
        )
        self.vista.actualizar_grafo(self.modelo_grafo.grafo, ruta)

    def manejar_validacion_ruta(self, cadena_protocolo: str) -> None:
        """
        Envía la secuencia de comunicación al Autómata Finito y audita el resultado.

        Args:
            cadena_protocolo (str): Secuencia sintáctica de red (Ej: 'SADF').
        """
        if not self.red_iniciada:
            self.vista.mostrar_alerta("Acción Inválida", "Debe generar la red antes de validar comunicaciones.")
            return

        self.vista.registrar_log(f"Iniciando auditoría de protocolo para cadena: '{cadena_protocolo}'", "INFO")

        # 1. Delegar la validación al núcleo matemático (Autómata)
        es_valida, traza_estados = self.modelo_automata.validar_cadena(cadena_protocolo)

        # 2. Formatear la respuesta visual de los estados lógicos (q0 -> q1 -> ...)
        ruta_str = " -> ".join(traza_estados)

        # 3. Informar al usuario del resultado
        if es_valida:
            self.vista.registrar_log(f"TRAZA: {ruta_str}", "INFO")
            self.vista.registrar_log("RESULTADO: CONEXIÓN ACEPTADA (Llegó a qF).", "INFO")
        else:
            self.vista.registrar_log(f"TRAZA: {ruta_str}", "ERROR")
            self.vista.registrar_log("RESULTADO: CONEXIÓN RECHAZADA (Cayó en qerr). Falla de protocolo o nodo bloqueado.", "ERROR")