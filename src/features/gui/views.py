"""Modern Desktop GUI for Doc2Markdown Studio using CustomTkinter with Drag & Drop support."""
import os
import re
import threading
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter as ctk

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_DND = True
except Exception:
    HAS_DND = False

from src.core.config import APP_NAME, APP_VERSION, APP_AUTHOR, APP_REPO_URL, APP_LICENSE, SUPPORTED_EXTENSIONS
from src.core.utils import format_size
from src.features.converter.service import ConversionService
from src.features.converter.models import ConversionRequest
from src.features.batch.service import BatchService
from src.features.history.service import HistoryService

# Set modern appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Base class supporting Drag and Drop if tkinterdnd2 is installed
if HAS_DND:
    class BaseWindow(ctk.CTk, TkinterDnD.DnDWrapper):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.TkdndVersion = TkinterDnD._require(self)
else:
    class BaseWindow(ctk.CTk):
        pass

class MainWindow(BaseWindow):
    """Main Application Window."""

    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{APP_VERSION} - Ahorro de Tokens para IA")
        self.geometry("1000x700")
        self.minsize(880, 600)

        # Set window icon if available
        icon_path = Path("icon.ico")
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path.resolve()))
            except Exception:
                pass

        # Services
        self.converter_service = ConversionService()
        self.batch_service = BatchService(self.converter_service)
        self.history_service = HistoryService()

        # State
        self.selected_files = []
        self.output_directory = None

        self._build_ui()
        self._setup_drag_and_drop()

    def _setup_drag_and_drop(self):
        """Enables drag-and-drop of files directly from Windows File Explorer onto the app."""
        if HAS_DND:
            try:
                self.drop_target_register(DND_FILES)
                self.dnd_bind('<<Drop>>', self._on_file_dropped)
            except Exception as e:
                print(f"Aviso DnD: {e}")

    def _on_file_dropped(self, event):
        """Handle files dropped from File Explorer."""
        raw_data = event.data
        if not raw_data:
            return

        # Windows paths with spaces are enclosed in curly braces {C:/path with spaces/file.xlsx}
        pattern = r'\{([^}]+)\}|(\S+)'
        matches = re.findall(pattern, raw_data)
        file_paths = [m[0] or m[1] for m in matches]

        for p_str in file_paths:
            p = Path(p_str)
            if p.is_file() and self.converter_service.is_supported(p):
                if p not in self.selected_files:
                    self.selected_files.append(p)
            elif p.is_dir():
                discovered = self.batch_service.discover_files(p, recursive=True)
                for f in discovered:
                    if f not in self.selected_files:
                        self.selected_files.append(f)

        self._update_file_display()

    def _build_ui(self):
        # Grid layout (2 columns: Sidebar & Main Workspace)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="⚡ Doc2Markdown", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 5))

        # Version Pill Badge
        version_label = ctk.CTkLabel(
            self.sidebar_frame,
            text=f"v{APP_VERSION} • {APP_AUTHOR}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#3498db"
        )
        version_label.grid(row=1, column=0, padx=20, pady=(0, 5))

        sub_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Optimizado para LLMs\n(Excel, Word, PDF -> MD)",
            font=ctk.CTkFont(size=11),
            text_color="gray70"
        )
        sub_label.grid(row=2, column=0, padx=20, pady=(0, 15))

        # Action Buttons in Sidebar
        self.btn_select_file = ctk.CTkButton(
            self.sidebar_frame, 
            text="📄 Seleccionar Archivo(s)", 
            command=self._on_select_files
        )
        self.btn_select_file.grid(row=3, column=0, padx=20, pady=8)

        self.btn_select_folder = ctk.CTkButton(
            self.sidebar_frame, 
            text="📁 Seleccionar Carpeta", 
            command=self._on_select_folder
        )
        self.btn_select_folder.grid(row=4, column=0, padx=20, pady=8)

        self.btn_output_folder = ctk.CTkButton(
            self.sidebar_frame,
            text="📂 Carpeta Destino",
            fg_color="#34495e",
            hover_color="#2c3e50",
            command=self._on_choose_output_dir
        )
        self.btn_output_folder.grid(row=5, column=0, padx=20, pady=8)

        # Convert Action Button
        self.btn_convert = ctk.CTkButton(
            self.sidebar_frame, 
            text="🚀 CONVERTIR A .MD", 
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2ecc71", 
            hover_color="#27ae60",
            command=self._start_conversion
        )
        self.btn_convert.grid(row=6, column=0, padx=20, pady=15)

        # Bottom info frame with GitHub repo and About modal
        self.bottom_sidebar = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.bottom_sidebar.grid(row=7, column=0, padx=15, pady=(10, 15), sticky="s")

        self.btn_clear = ctk.CTkButton(
            self.bottom_sidebar,
            text="Limpiar Selección",
            fg_color="#e74c3c",
            hover_color="#c0392b",
            height=28,
            command=self._clear_selection
        )
        self.btn_clear.pack(fill="x", pady=4)

        self.btn_repo = ctk.CTkButton(
            self.bottom_sidebar,
            text="⭐ Repositorio GitHub",
            fg_color="#24292e",
            hover_color="#1b1f23",
            height=28,
            command=self._open_repo
        )
        self.btn_repo.pack(fill="x", pady=4)

        self.btn_about = ctk.CTkButton(
            self.bottom_sidebar,
            text="ℹ️ Info y Créditos",
            fg_color="#2c3e50",
            hover_color="#1a252f",
            height=28,
            command=self._show_about
        )
        self.btn_about.pack(fill="x", pady=4)

        # Right Main Workspace
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        # Summary Bar
        self.summary_card = ctk.CTkFrame(self.main_frame, fg_color=("#2c3e50", "#1a252f"))
        self.summary_card.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.summary_card.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.lbl_card_files = ctk.CTkLabel(self.summary_card, text="Archivos: 0", font=ctk.CTkFont(size=13, weight="bold"))
        self.lbl_card_files.grid(row=0, column=0, pady=10)

        self.lbl_card_savings = ctk.CTkLabel(self.summary_card, text="Ahorro tokens: ~0%", font=ctk.CTkFont(size=13, weight="bold"), text_color="#2ecc71")
        self.lbl_card_savings.grid(row=0, column=1, pady=10)

        self.lbl_card_tokens = ctk.CTkLabel(self.summary_card, text="Tokens est.: 0", font=ctk.CTkFont(size=13, weight="bold"))
        self.lbl_card_tokens.grid(row=0, column=2, pady=10)

        self.lbl_status = ctk.CTkLabel(self.summary_card, text="Estado: Listo", font=ctk.CTkFont(size=13))
        self.lbl_status.grid(row=0, column=3, pady=10)

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.progress_bar.set(0)

        # Content Notebook / Tabview (Files, Preview Markdown, History)
        self.tabs = ctk.CTkTabview(self.main_frame)
        self.tabs.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.tab_files = self.tabs.add("Archivos a Convertir")
        self.tab_preview = self.tabs.add("Vista Previa Markdown")
        self.tab_history = self.tabs.add("Historial y Métricas")

        # Tab: Files List
        self.tab_files.grid_columnconfigure(0, weight=1)
        self.tab_files.grid_rowconfigure(0, weight=1)
        # Drop Zone & File List
        self.txt_file_list = ctk.CTkTextbox(self.tab_files, font=ctk.CTkFont(family="Consolas", size=12))
        self.txt_file_list.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.txt_file_list.insert("1.0", "📥 Puedes arrastrar y soltar archivos aquí desde cualquier carpeta de Windows\no usar el botón 'Seleccionar Archivo(s)' de la izquierda.\n\nSoporta: Excel (.xlsx, .xls), Word (.docx), PDF, PowerPoint (.pptx), CSV, etc.")
        self.txt_file_list.configure(state="disabled")

        # Tab: Preview Markdown
        self.tab_preview.grid_columnconfigure(0, weight=1)
        self.tab_preview.grid_rowconfigure(1, weight=1)

        self.preview_header_frame = ctk.CTkFrame(self.tab_preview, fg_color="transparent")
        self.preview_header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.lbl_preview_title = ctk.CTkLabel(self.preview_header_frame, text="Último archivo convertido:", font=ctk.CTkFont(weight="bold"))
        self.lbl_preview_title.pack(side="left", padx=5)

        self.btn_copy_markdown = ctk.CTkButton(
            self.preview_header_frame, 
            text="📋 Copiar al Portapapeles", 
            width=150,
            command=self._copy_markdown_to_clipboard
        )
        self.btn_copy_markdown.pack(side="right", padx=5)

        self.btn_open_folder = ctk.CTkButton(
            self.preview_header_frame,
            text="📂 Abrir Carpeta del Archivo",
            fg_color="#34495e",
            hover_color="#2c3e50",
            width=160,
            command=self._open_output_folder
        )
        self.btn_open_folder.pack(side="right", padx=5)

        self.last_converted_path = None

        self.txt_preview = ctk.CTkTextbox(self.tab_preview, font=ctk.CTkFont(family="Consolas", size=12))
        self.txt_preview.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Tab: History
        self.tab_history.grid_columnconfigure(0, weight=1)
        self.tab_history.grid_rowconfigure(0, weight=1)
        self.txt_history = ctk.CTkTextbox(self.tab_history, font=ctk.CTkFont(family="Consolas", size=12))
        self.txt_history.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self._refresh_history()

    def _open_repo(self):
        """Open author repository in default web browser."""
        webbrowser.open_new_tab(APP_REPO_URL)

    def _show_about(self):
        """Displays application details, version, author, and license."""
        about_dialog = ctk.CTkToplevel(self)
        about_dialog.title("Acerca de Doc2Markdown")
        about_dialog.geometry("450x330")
        about_dialog.resizable(False, False)
        about_dialog.attributes("-topmost", True)

        title = ctk.CTkLabel(
            about_dialog, 
            text="⚡ Doc2Markdown Studio", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(20, 5))

        info_text = (
            f"Versión: {APP_VERSION}\n"
            f"Autor Principal: {APP_AUTHOR}\n"
            f"Licencia: {APP_LICENSE}\n\n"
            "Software open source diseñado para que programadores, analistas\n"
            "y cualquier usuario conviertan documentos complejos a Markdown,\n"
            "reduciendo hasta un 90% el gasto de tokens en Inteligencias Artificiales.\n\n"
            "Todos los derechos reservados. Cualquier distribución debe dar crédito\n"
            "y mantener la autoría original."
        )

        lbl_info = ctk.CTkLabel(about_dialog, text=info_text, justify="center", font=ctk.CTkFont(size=12))
        lbl_info.pack(padx=20, pady=10)

        btn_visit = ctk.CTkButton(
            about_dialog,
            text="🌐 Ir al Repositorio",
            fg_color="#24292e",
            hover_color="#1b1f23",
            command=lambda: webbrowser.open_new_tab(APP_REPO_URL)
        )
        btn_visit.pack(pady=5)

        btn_close = ctk.CTkButton(
            about_dialog,
            text="Cerrar",
            fg_color="#34495e",
            hover_color="#2c3e50",
            command=about_dialog.destroy
        )
        btn_close.pack(pady=10)

    def _on_select_files(self):
        extensions = [f"*{ext}" for ext in SUPPORTED_EXTENSIONS.keys()]
        file_types = [
            ("Documentos soportados", " ".join(extensions)),
            ("Todos los archivos", "*.*")
        ]
        paths = filedialog.askopenfilenames(title="Seleccionar Documentos", filetypes=file_types)
        if paths:
            for p in paths:
                p_path = Path(p)
                if p_path not in self.selected_files:
                    self.selected_files.append(p_path)
            self._update_file_display()

    def _on_select_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar Carpeta con Documentos")
        if folder:
            discovered = self.batch_service.discover_files(Path(folder), recursive=True)
            for p in discovered:
                if p not in self.selected_files:
                    self.selected_files.append(p)
            self._update_file_display()

    def _on_choose_output_dir(self):
        folder = filedialog.askdirectory(title="Seleccionar Carpeta Destino")
        if folder:
            self.output_directory = Path(folder)
            messagebox.showinfo("Carpeta Destino", f"Los archivos .md se guardarán en:\n{self.output_directory}")

    def _clear_selection(self):
        self.selected_files.clear()
        self._update_file_display()

    def _update_file_display(self):
        self.txt_file_list.configure(state="normal")
        self.txt_file_list.delete("1.0", "end")
        if not self.selected_files:
            self.txt_file_list.insert("1.0", "No hay archivos seleccionados.")
            self.lbl_card_files.configure(text="Archivos: 0")
        else:
            self.lbl_card_files.configure(text=f"Archivos: {len(self.selected_files)}")
            total_size = sum(f.stat().st_size for f in self.selected_files if f.exists())
            self.txt_file_list.insert("end", f"Total seleccionado: {len(self.selected_files)} archivos ({format_size(total_size)})\n\n")
            for i, f in enumerate(self.selected_files, 1):
                self.txt_file_list.insert("end", f"[{i}] {f.name} ({format_size(f.stat().st_size)})\n    Ruta: {f}\n\n")
        self.txt_file_list.configure(state="disabled")

    def _open_output_folder(self):
        """Open Windows Explorer at the location of the converted file."""
        if self.last_converted_path and Path(self.last_converted_path).exists():
            import subprocess
            subprocess.run(f'explorer /select,"{Path(self.last_converted_path).resolve()}"', shell=True)
        elif self.output_directory and Path(self.output_directory).exists():
            import subprocess
            subprocess.run(f'explorer "{Path(self.output_directory).resolve()}"', shell=True)
        else:
            messagebox.showinfo("Carpeta", "Aún no se ha convertido ningún archivo o la carpeta no está disponible.")

    def _copy_markdown_to_clipboard(self):
        content = self.txt_preview.get("1.0", "end").strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            messagebox.showinfo("Portapapeles", "¡Contenido Markdown copiado con éxito para pegar en ChatGPT/Claude/Gemini!")

    def _start_conversion(self):
        if not self.selected_files:
            messagebox.showwarning("Sin archivos", "Por favor selecciona al menos un archivo antes de convertir.")
            return

        self.btn_convert.configure(state="disabled")
        self.progress_bar.set(0)
        self.lbl_status.configure(text="Convirtiendo...")

        # Run conversion in background thread to keep UI smooth
        threading.Thread(target=self._run_conversion_worker, daemon=True).start()

    def _run_conversion_worker(self):
        total = len(self.selected_files)
        total_tokens = 0
        total_saved_bytes = 0
        total_orig_bytes = 0
        last_result = None

        def on_progress(done, count, res):
            nonlocal total_tokens, total_saved_bytes, total_orig_bytes, last_result
            last_result = res
            self.history_service.record_conversion(res)
            if res.success:
                total_tokens += res.estimated_tokens
                total_saved_bytes += res.saved_bytes
                total_orig_bytes += res.original_size_bytes

            progress = done / count
            self.after(0, lambda: self._update_ui_progress(progress, done, count))

        results = self.batch_service.convert_batch(
            self.selected_files,
            output_dir=self.output_directory,
            progress_callback=on_progress
        )

        savings_pct = (total_saved_bytes / total_orig_bytes * 100) if total_orig_bytes > 0 else 0.0
        self.after(0, lambda: self._conversion_finished(results, total_tokens, savings_pct, last_result))

    def _update_ui_progress(self, progress, done, total):
        self.progress_bar.set(progress)
        self.lbl_status.configure(text=f"Procesando: {done}/{total}")

    def _conversion_finished(self, results, total_tokens, savings_pct, last_result):
        self.btn_convert.configure(state="normal")
        self.lbl_status.configure(text="¡Completado!")
        self.lbl_card_tokens.configure(text=f"Tokens est.: ~{total_tokens:,}")
        self.lbl_card_savings.configure(text=f"Ahorro peso: ~{savings_pct:.1f}%")

        if last_result and last_result.success:
            self.last_converted_path = last_result.output_path
            self.txt_preview.delete("1.0", "end")
            self.txt_preview.insert("1.0", last_result.markdown_content)
            self.lbl_preview_title.configure(text=f"Vista previa: {last_result.source_path.name}")
            self.tabs.set("Vista Previa Markdown")

        self._refresh_history()

        success_count = sum(1 for r in results if r.success)
        messagebox.showinfo(
            "Conversión Exitosa", 
            f"Se convirtieron {success_count}/{len(results)} documentos a Markdown (.md).\n"
            f"Tokens estimados para la IA: ~{total_tokens:,}\n"
            f"Los archivos .md ya están listos para subirse a tu IA sin derrochar tokens."
        )

    def _refresh_history(self):
        self.txt_history.delete("1.0", "end")
        records = self.history_service.get_all()
        if not records:
            self.txt_history.insert("1.0", "No hay conversiones registradas.")
            return

        self.txt_history.insert("end", f"Historial de conversiones ({len(records)} registros):\n")
        self.txt_history.insert("end", "="*70 + "\n\n")
        for rec in records:
            status = "✅ ÉXITO" if rec.get("success") else "❌ FALLO"
            name = Path(rec.get("source", "")).name
            tokens = rec.get("estimated_tokens", 0)
            orig_sz = format_size(rec.get("original_size", 0))
            md_sz = format_size(rec.get("markdown_size", 0))
            ts = rec.get("timestamp", "")[:19].replace("T", " ")
            self.txt_history.insert("end", f"[{ts}] {status} - {name}\n")
            self.txt_history.insert("end", f"    Tokens: ~{tokens:,} | Original: {orig_sz} -> MD: {md_sz}\n")
            if rec.get("output"):
                self.txt_history.insert("end", f"    Salida: {rec['output']}\n")
            self.txt_history.insert("end", "\n")

def launch_gui():
    """Launch the CustomTkinter GUI application."""
    app = MainWindow()
    app.mainloop()

