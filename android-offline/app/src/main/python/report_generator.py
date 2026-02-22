from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path

from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from PIL import Image


def _mk_inline_image(doc: DocxTemplate, image_path: str | None):
    """Replica la lógica de Django: ajusta la imagen y la inserta con tamaño fijo."""
    if not image_path:
        return None

    source = Path(image_path)
    if not source.exists():
        return None

    img = Image.open(source)
    img.thumbnail((int(120 * 11.8), int(105 * 11.8)))
    bio = BytesIO()
    img.save(bio, format=img.format or "PNG")
    bio.seek(0)
    return InlineImage(doc, bio, width=Mm(120), height=Mm(105))


def _inspection_context(doc: DocxTemplate):
    context = {
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "nombre": "Técnico Demo",
        "parque": "Parque Solar Demo",
        "inspeccion_compacto": "OK",
        "comentario_compacto": "Sin novedades.",
        "inspeccion_reconectador": "OK",
        "comentario_reconectador": "Sin novedades.",
        "inspeccion_medidor": "OK",
        "comentario_medidor": "Sin novedades.",
        "inspeccion_sala_control": "OK",
        "comentario_sala_control": "Limpieza al día.",
        "inspeccion_linea_mt": "OK",
        "comentario_linea_mt": "Sin daños visibles.",
        "inspeccion_ct": "OK",
        "comentario_ct": "Operación normal.",
        "inspeccion_inversores": "OK",
        "comentario_inversores": "Sin alarmas.",
        "inspeccion_modulos": "OK",
        "comentario_modulos": "Sin hot spots aparentes.",
        "nivel_soiling": "Bajo",
        "comentarios_supervisor": "Reporte generado offline en Android.",
    }

    for key in [
        "imagen_ecm",
        "imagen_reconectador",
        "imagen_medidor",
        "imagen_sala_control",
        "imagen_linea_mt",
        "imagen_ct",
        "imagen_inversores",
        "imagen_modulos",
        "imagen_soiling",
    ]:
        context[key] = _mk_inline_image(doc, None)

    context["foto_adicional"] = []
    return context


def _activities_context():
    return {
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "nombre": "Técnico Demo",
        "parque": "Parque Solar Demo",
        "resumen": "Se completaron actividades preventivas y verificación de equipos.",
        "foto_adicional": [],
    }


def generate_report(report_type: str, template_path: str, output_dir: str) -> str:
    doc = DocxTemplate(template_path)

    if report_type == "inspection":
        context = _inspection_context(doc)
        prefix = "reporte_inspeccion"
    elif report_type == "activities":
        context = _activities_context()
        prefix = "reporte_actividades"
    else:
        raise ValueError(f"Tipo de reporte no soportado: {report_type}")

    doc.render(context)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    full_path = output_path / filename
    doc.save(full_path)

    return str(full_path)
