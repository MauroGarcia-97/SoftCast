import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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
        self.callback_generar_red = None
        self.callback_bloquear_nodo = None
        self.callback_validar_ruta = None

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

        # Controles para Validación de AFD
        tk.Label(panel_control, text="Protocolo (Autómata):", fg="#BDC3C7", bg="#2C3E50").pack(pady=(30, 5))
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
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

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

    def _evento_generar_red(self):
        if self.callback_generar_red: self.callback_generar_red()

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

    # ================= MÉTODOS PÚBLICOS PARA EL CONTROLADOR =================

    def set_controladores(self, cb_generar, cb_bloquear, cb_validar):
        """Inyecta las funciones del Controlador en los botones."""
        self.callback_generar_red = cb_generar
        self.callback_bloquear_nodo = cb_bloquear
        self.callback_validar_ruta = cb_validar

    def actualizar_grafo(self, grafo) -> None:
        """Delega el dibujo del grafo actualizado al renderizador."""
        RenderizadorGrafo.dibujar_red(grafo, self.figura, self.canvas)

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