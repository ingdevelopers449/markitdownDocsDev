"""Modern Splash Screen with loading progress bar for instant visual feedback on startup."""
import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path

def create_splash_screen():
    """
    Creates an ultra-fast, lightweight native Tkinter splash screen.
    Opens instantly (< 0.1s) before loading heavy modules like MarkItDown, Onnx, and CustomTkinter.
    """
    splash = tk.Tk()
    splash.overrideredirect(True)  # Frameless modern splash window
    
    # Dimensions & centering
    width, height = 440, 260
    screen_w = splash.winfo_screenwidth()
    screen_h = splash.winfo_screenheight()
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    splash.geometry(f"{width}x{height}+{x}+{y}")
    splash.configure(bg="#1a252f")
    splash.attributes("-topmost", True)

    # Set icon if available
    try:
        # Check bundled asset path
        if hasattr(sys, '_MEIPASS'):
            icon_file = Path(sys._MEIPASS) / "icon.ico"
        else:
            icon_file = Path("icon.ico")
        if icon_file.exists():
            splash.iconbitmap(str(icon_file.resolve()))
    except Exception:
        pass

    # Decorative Card Border
    card = tk.Frame(splash, bg="#1a252f", highlightbackground="#3498db", highlightthickness=2)
    card.pack(fill="both", expand=True, padx=2, pady=2)

    # App Logo / Title
    lbl_logo = tk.Label(
        card,
        text="⚡ Doc2Markdown Studio",
        font=("Segoe UI", 18, "bold"),
        fg="#ffffff",
        bg="#1a252f"
    )
    lbl_logo.pack(pady=(35, 5))

    lbl_sub = tk.Label(
        card,
        text="Optimizador de Documentos para IA • v1.0.0",
        font=("Segoe UI", 10),
        fg="#3498db",
        bg="#1a252f"
    )
    lbl_sub.pack(pady=(0, 25))

    # Dynamic status message label
    lbl_status = tk.Label(
        card,
        text="Iniciando componentes del sistema...",
        font=("Segoe UI", 9),
        fg="#bdc3c7",
        bg="#1a252f"
    )
    lbl_status.pack(pady=(0, 10))

    # Progress bar style
    style = ttk.Style(splash)
    style.theme_use("clam")
    style.configure(
        "Splash.Horizontal.TProgressbar",
        troughcolor="#2c3e50",
        background="#2ecc71",
        lightcolor="#2ecc71",
        darkcolor="#2ecc71",
        bordercolor="#1a252f"
    )

    progress = ttk.Progressbar(
        card,
        style="Splash.Horizontal.TProgressbar",
        orient="horizontal",
        length=340,
        mode="determinate"
    )
    progress.pack(pady=(0, 20))
    progress["value"] = 10

    lbl_author = tk.Label(
        card,
        text="Desarrollado por ingdeveloper449",
        font=("Segoe UI", 8),
        fg="#7f8c8d",
        bg="#1a252f"
    )
    lbl_author.pack()

    splash.update()

    def update_progress(percent: int, message: str, delay_ms: int = 150):
        """Update the progress bar value and status message with smooth perception delay."""
        try:
            progress["value"] = percent
            lbl_status.config(text=message)
            splash.update()
            if delay_ms > 0:
                splash.after(delay_ms)
                splash.update()
        except Exception:
            pass

    def close_splash():
        """Smoothly destroy the splash window."""
        try:
            splash.destroy()
        except Exception:
            pass

    return splash, update_progress, close_splash

