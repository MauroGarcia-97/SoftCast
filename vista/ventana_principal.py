import tkinter as tk
from tkinter import ttk, messagebox
from collections.abc import Callable
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from .render_visual import RenderizadorGrafo

class InterfazSoftCast:
    """
    Ventana principal del sistema. Define la UI/UX del Dashboard.
    Esta clase NO toma decisiones lógicas, solo delega los eventos al Controlador.
    """

    def __init__(self):
        """Inicializa la ventana principal y estructura el Layout (MVC)."""
        self.root = tk.Tk()
        self.root.title("SoftCast - Sistema Inteligente de Detección de Fallas")
        self.root.geometry("1200x750")
        self.root.configure(bg="#F0F0F0")

        # Punteros a los callbacks del Controlador (Se inyectan después)
        self.callback_generar_red: Callable[[str], None] | None = None
        self.callback_bloquear_nodo: Callable[[str], None] | None = None
        self.callback_validar_ruta: Callable[[str], None] | None = None
        self.callback_calcular_ruta: Callable[[str, str], None] | None = None

        self._construir_interfaz()

    def _construir_interfaz(self) -> None:
        """Construye las 3 columnas principales del Dashboard."""

        # --- COLUMNA 1: Panel de Control (Izquierda) ---
        panel_control = tk.Frame(self.root, width=250, bg="#2C3E50", padx=15, pady=15)
        panel_control.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(panel_control, text="Panel de Control", fg="white", bg="#2C3E50",
                 font=("Arial", 14, "bold")).pack(pady=(0, 20))

        # Botón 1: Generar Red
        btn_generar = tk.Button(panel_control, text="1. Generar / Reiniciar Red",
                                bg="#3498DB", fg="white", font=("Arial", 10, "bold"),
                                command=self._evento_generar_red)
        btn_generar.pack(fill=tk.X, pady=10)

        # Controles para Bloqueo (Inyección de Fallas)
        tk.Label(panel_control, text="Inyectar Falla:", fg="#BDC3C7", bg="#2C3E50").pack(pady=(20, 5))
        self.entrada_nodo = tk.Entry(panel_control, justify="center")
        self.entrada_nodo.insert(0, "Ej: N2")
        self.entrada_nodo.pack(fill=tk.X, pady=5)

        btn_bloquear = tk.Button(panel_control, text="2. Bloquear Equipo",
                                 bg="#E74C3C", fg="white", font=("Arial", 10, "bold"),
                                 command=self._evento_bloquear_nodo)
        btn_bloquear.pack(fill=tk.X, pady=5)

        tk.Label(
            panel_control,
            text="Ruta de red (nodos activos):",
            fg="#BDC3C7",
            bg="#2C3E50",
        ).pack(pady=(15, 5))
        self.entrada_origen = tk.Entry(panel_control, justify="center")
        self.entrada_origen.insert(0, "Origen (Ej: N1)")
        self.entrada_origen.pack(fill=tk.X, pady=3)
        self.entrada_destino = tk.Entry(panel_control, justify="center")
        self.entrada_destino.insert(0, "Destino (Ej: N10)")
        self.entrada_destino.pack(fill=tk.X, pady=3)
        btn_calcular_ruta = tk.Button(
            panel_control,
            text="Calcular ruta activa",
            bg="#9B59B6",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self._evento_calcular_ruta,
        )
        btn_calcular_ruta.pack(fill=tk.X, pady=5)

        # Controles para Validación de AFD
        tk.Label(panel_control, text="Protocolo (Autómata):", fg="#BDC3C7", bg="#2C3E50").pack(pady=(15, 5))
        self.entrada_cadena = tk.Entry(panel_control, justify="center")
        self.entrada_cadena.insert(0, "SADF")
        self.entrada_cadena.pack(fill=tk.X, pady=5)

        btn_validar = tk.Button(panel_control, text="3. Validar Comunicación",
                                bg="#2ECC71", fg="white", font=("Arial", 10, "bold"),
                                command=self._evento_validar_ruta)
        btn_validar.pack(fill=tk.X, pady=5)

        # --- COLUMNA 2: Lienzo del Grafo (Centro) ---
        panel_lienzo = tk.Frame(self.root, bg="white")
        panel_lienzo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.figura = Figure(figsize=(6, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figura, master=panel_lienzo)
        self.toolbar = NavigationToolbar2Tk(
            self.canvas,
            panel_lienzo,
            pack_toolbar=False,
        )
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.get_tk_widget().bind(
            "<MouseWheel>",
            self._evento_rueda_grafo,
            add="+",
        )

        # --- COLUMNA 3: Consola de Auditoría (Derecha) ---
        panel_consola = tk.Frame(self.root, width=300, bg="#1E1E1E")
        panel_consola.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(panel_consola, text="Terminal de Auditoría (AFD)", fg="#00FF00", bg="#1E1E1E",
                 font=("Consolas", 12, "bold")).pack(pady=10)

        self.texto_consola = tk.Text(panel_consola, bg="#1E1E1E", fg="#00FF00", font=("Consolas", 10),
                                     state=tk.DISABLED, wrap=tk.WORD, width=40)
        self.texto_consola.pack(padx=10, pady=10, fill=tk.Y, expand=True)

        # Configurar etiquetas de color para la consola
        self.texto_consola.tag_config('INFO', foreground='#00FF00')   # Verde
        self.texto_consola.tag_config('ERROR', foreground='#FF4C4C')  # Rojo
        self.texto_consola.tag_config('ALERTA', foreground='#F1C40F') # Amarillo

    # ================= EVENTOS DE INTERFAZ =================

    def _evento_generar_red(self) -> None:
        """Solicita una topología y delega su generación al controlador."""
        topologia = self._solicitar_topologia()
        if topologia is not None and self.callback_generar_red is not None:
            self.callback_generar_red(topologia)

    def _solicitar_topologia(self) -> str | None:
        """Muestra un diálogo modal para elegir el tipo de topología."""
        dialogo = tk.Toplevel(self.root)
        dialogo.title("Seleccionar topología")
        dialogo.transient(self.root)
        dialogo.resizable(False, False)

        tk.Label(
            dialogo,
            text="¿Qué topología deseas generar?",
            padx=20,
            pady=12,
        ).pack()

        topologias = ("Estrella", "Árbol", "Malla")
        seleccion = tk.StringVar(value=topologias[0])
        selector = ttk.Combobox(
            dialogo,
            textvariable=seleccion,
            values=topologias,
            state="readonly",
        )
        selector.pack(padx=20, pady=5)

        resultado: str | None = None

        def confirmar() -> None:
            nonlocal resultado
            resultado = seleccion.get()
            dialogo.destroy()

        panel_botones = tk.Frame(dialogo)
        panel_botones.pack(pady=12)
        ttk.Button(panel_botones, text="Generar", command=confirmar).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            panel_botones,
            text="Cancelar",
            command=dialogo.destroy,
        ).pack(side=tk.LEFT, padx=5)

        dialogo.update_idletasks()
        ancho = dialogo.winfo_reqwidth()
        alto = dialogo.winfo_reqheight()
        x = (dialogo.winfo_screenwidth() - ancho) // 2
        y = (dialogo.winfo_screenheight() - alto) // 2
        dialogo.geometry(f"+{x}+{y}")
        dialogo.protocol("WM_DELETE_WINDOW", dialogo.destroy)
        dialogo.grab_set()
        selector.focus_set()
        self.root.wait_window(dialogo)
        return resultado

    def _evento_bloquear_nodo(self):
        nodo_id = self.entrada_nodo.get().strip().upper()
        if not nodo_id or nodo_id == "EJ: N2":
            self.mostrar_alerta("Error", "Ingrese un ID de nodo válido (Ej: N1).")
            return
        if self.callback_bloquear_nodo: self.callback_bloquear_nodo(nodo_id)

    def _evento_validar_ruta(self):
        cadena = self.entrada_cadena.get().strip().upper()
        if not cadena:
            self.mostrar_alerta("Error", "Ingrese la cadena del protocolo (Ej: SADF).")
            return
        if self.callback_validar_ruta: self.callback_validar_ruta(cadena)

    def _evento_calcular_ruta(self) -> None:
        """Valida origen y destino, y solicita calcular una ruta activa."""
        origen = self.entrada_origen.get().strip().upper()
        destino = self.entrada_destino.get().strip().upper()
        if not origen or not destino or origen.startswith("ORIGEN ") or destino.startswith("DESTINO "):
            self.mostrar_alerta(
                "Datos incompletos",
                "Ingrese los identificadores de origen y destino (Ej: N1 y N10).",
            )
            return
        if self.callback_calcular_ruta is not None:
            self.callback_calcular_ruta(origen, destino)

    def _evento_rueda_grafo(self, evento: tk.Event) -> str:
        """Desplaza o acerca el grafo según la rueda y las teclas modificadoras."""
        if not self.figura.axes or evento.delta == 0:
            return "break"

        ax = self.figura.axes[0]
        pasos = evento.delta / 120
        limite_x = ax.get_xlim()
        limite_y = ax.get_ylim()

        if evento.state & 0x0004:  # Control: acercar o alejar
            factor = 0.8 ** pasos
            centro_x = sum(limite_x) / 2
            centro_y = sum(limite_y) / 2
            mitad_x = (limite_x[1] - limite_x[0]) * factor / 2
            mitad_y = (limite_y[1] - limite_y[0]) * factor / 2
            ax.set_xlim(centro_x - mitad_x, centro_x + mitad_x)
            ax.set_ylim(centro_y - mitad_y, centro_y + mitad_y)
        elif evento.state & 0x0001:  # Shift: desplazamiento horizontal
            desplazamiento_x = (limite_x[1] - limite_x[0]) * 0.1 * pasos
            ax.set_xlim(
                limite_x[0] + desplazamiento_x,
                limite_x[1] + desplazamiento_x,
            )
        else:  # Rueda sin modificadores: desplazamiento vertical
            desplazamiento_y = (limite_y[1] - limite_y[0]) * 0.1 * pasos
            ax.set_ylim(
                limite_y[0] + desplazamiento_y,
                limite_y[1] + desplazamiento_y,
            )

        self.canvas.draw_idle()
        return "break"

    # ================= MÉTODOS PÚBLICOS PARA EL CONTROLADOR =================

    def set_controladores(
        self,
        cb_generar: Callable[[str], None],
        cb_bloquear: Callable[[str], None],
        cb_validar: Callable[[str], None],
        cb_calcular_ruta: Callable[[str, str], None],
    ) -> None:
        """Inyecta las funciones del Controlador en los botones."""
        self.callback_generar_red = cb_generar
        self.callback_bloquear_nodo = cb_bloquear
        self.callback_validar_ruta = cb_validar
        self.callback_calcular_ruta = cb_calcular_ruta

    def actualizar_grafo(self, grafo, ruta: list[str] | None = None) -> None:
        """Dibuja el grafo y, si se indica, resalta una ruta en azul."""
        RenderizadorGrafo.dibujar_red(grafo, self.figura, self.canvas, ruta)

    def registrar_log(self, mensaje: str, nivel: str = 'INFO') -> None:
        """Escribe un mensaje en la terminal lateral simulada."""
        self.texto_consola.config(state=tk.NORMAL)
        self.texto_consola.insert(tk.END, f"> {mensaje}\n\n", nivel)
        self.texto_consola.see(tk.END)  # Auto-scroll
        self.texto_consola.config(state=tk.DISABLED)

    def mostrar_alerta(self, titulo: str, mensaje: str) -> None:
        """Muestra una ventana emergente nativa de error o advertencia."""
        messagebox.showwarning(titulo, mensaje)

    def iniciar_loop(self):
        """Arranca el bucle principal de la aplicación UI."""
        self.root.mainloop()