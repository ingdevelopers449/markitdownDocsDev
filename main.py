"""
Punto de entrada principal de la aplicación Doc2Markdown Studio.
Ejecuta la interfaz gráfica moderna por defecto o el modo CLI si recibe argumentos.
"""
import sys

def main():
    # Si se pasan argumentos por línea de comandos (e.g. `python main.py archivo.xlsx`)
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--gui"):
        from src.features.cli.runner import run_cli
        sys.exit(run_cli())
    else:
        # Por defecto abre la interfaz gráfica de escritorio
        from src.features.gui.views import launch_gui
        launch_gui()

if __name__ == "__main__":
    main()
