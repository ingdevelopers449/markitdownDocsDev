"""Command Line Interface (CLI) feature for terminal power-users."""
import argparse
import sys
from pathlib import Path

from src.core.config import APP_NAME, APP_VERSION, SUPPORTED_EXTENSIONS
from src.core.utils import format_size
from src.features.converter.service import ConversionService
from src.features.converter.models import ConversionRequest
from src.features.batch.service import BatchService
from src.features.history.service import HistoryService

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="doc2md",
        description=f"{APP_NAME} v{APP_VERSION} - Convierte documentos (Excel, Word, PDF, PPTX) a Markdown para ahorrar tokens en IA."
    )
    parser.add_argument("path", type=str, nargs="?", default=None, help="Ruta del archivo o carpeta a convertir")
    parser.add_argument("-o", "--output", type=str, default=None, help="Directorio o archivo de salida (.md)")
    parser.add_argument("-r", "--recursive", action="store_true", help="Buscar archivos recursivamente si es carpeta")
    parser.add_argument("--no-header", action="store_true", help="No agregar encabezado con metadatos")
    parser.add_argument("--list-formats", action="store_true", help="Listar formatos soportados")
    return parser

def run_cli(args_list=None):
    parser = create_parser()
    args = parser.parse_args(args_list)

    if args.list_formats:
        print("Formatos soportados:")
        for ext, desc in SUPPORTED_EXTENSIONS.items():
            print(f"  {ext:<8} : {desc}")
        return 0

    if not args.path:
        parser.print_help()
        return 1

    target = Path(args.path)
    if not target.exists():
        print(f"[ERROR] La ruta no existe: {target}", file=sys.stderr)
        return 1

    converter = ConversionService()
    history = HistoryService()

    if target.is_file():
        out_path = Path(args.output) if args.output else None
        req = ConversionRequest(
            source_path=target,
            output_path=out_path,
            add_metadata_header=not args.no_header
        )
        print(f"[*] Convirtiendo: {target.name}...")
        res = converter.convert_file(req)
        history.record_conversion(res)

        if res.success:
            print("[EXITO] Conversión completada con éxito.")
            print(f"  -> Destino: {res.output_path}")
            print(f"  -> Tamaño Original: {format_size(res.original_size_bytes)} | Markdown: {format_size(res.markdown_size_bytes)}")
            print(f"  -> Ahorro de espacio: {res.savings_percentage}%")
            print(f"  -> Tokens estimados para IA: ~{res.estimated_tokens:,}")
            print(f"  -> Tiempo: {res.duration_seconds}s")
            return 0
        else:
            print(f"[ERROR] Error al convertir: {res.error_message}", file=sys.stderr)
            return 1

    elif target.is_dir():
        batch_service = BatchService(conversion_service=converter)
        files = batch_service.discover_files(target, recursive=args.recursive)
        if not files:
            print(f"[INFO] No se encontraron archivos soportados en {target}")
            return 0

        print(f"[*] Encontrados {len(files)} archivos para procesar...")
        out_dir = Path(args.output) if args.output else target

        def on_progress(done, total, result):
            status = "OK" if result.success else "FALLO"
            print(f" [{done}/{total}] {result.source_path.name} -> {status} (~{result.estimated_tokens} tokens)")
            history.record_conversion(result)

        results = batch_service.convert_batch(files, output_dir=out_dir, progress_callback=on_progress)
        success_count = sum(1 for r in results if r.success)
        total_tokens = sum(r.estimated_tokens for r in results if r.success)

        print("\n" + "="*40)
        print(f"Procesamiento por lotes finalizado: {success_count}/{len(results)} exitosos.")
        print(f"Total estimado de tokens generados: ~{total_tokens:,}")
        return 0

if __name__ == "__main__":
    sys.exit(run_cli())
