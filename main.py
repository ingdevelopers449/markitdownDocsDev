"""
Punto de entrada principal de la aplicación Doc2Markdown Studio.
Ejecuta una pantalla de carga moderna (Splash Screen) con barra de progreso instantánea.
"""
import sys

def main():
    # Si se pasan argumentos por línea de comandos (modo CLI)
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--gui"):
        from src.features.cli.runner import run_cli
        sys.exit(run_cli())
    else:
        # Modo Interfaz Gráfica con Splash Screen instantáneo
        try:
            from src.features.gui.splash import create_splash_screen
            splash, update_progress, close_splash = create_splash_screen()

            update_progress(25, "Cargando componentes de interfaz...")
            from src.features.gui.views import launch_gui

            update_progress(50, "Cargando motor de conversión MarkItDown...")

            def on_ready():
                close_splash()

            launch_gui(progress_callback=update_progress, on_ready_callback=on_ready)
        except Exception:
            # Fallback en caso de cualquier detalle en splash
            from src.features.gui.views import launch_gui
            launch_gui()

if __name__ == "__main__":
    main()
