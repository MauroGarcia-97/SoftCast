"""
Script Principal - Sistema Inteligente SoftCast
Autores: María Fernanda Mantilla y Mauricio García
Ejecución: python main.py
"""

import sys
from modelo.grafo_topologia import GrafoRed
from modelo.automata_validador import AutomataRed
from vista.ventana_principal import InterfazSoftCast
from controlador.orquestador import ControladorPrincipal

def main():
    """Inicializa la arquitectura MVC y arranca la aplicación."""
    try:
        # 1. Instanciación de la Capa de Datos (Modelos)
        modelo_red = GrafoRed()
        modelo_automata = AutomataRed()

        # 2. Instanciación de la Capa Gráfica (Vista)
        vista_app = InterfazSoftCast()

        # 3. Ensamblaje Arquitectónico (Controlador)
        controlador = ControladorPrincipal(modelo_red, modelo_automata, vista_app)

        # 4. Despliegue de la aplicación
        controlador.iniciar()

    except Exception as e:
        print(f"[ERROR CRÍTICO] Fallo al iniciar el sistema SoftCast: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()