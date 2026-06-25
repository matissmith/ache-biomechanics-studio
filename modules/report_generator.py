"""
Ache Innovation — Generador de Reportes PDF
Produce un reporte profesional con ReportLab.
"""

import io
from datetime import datetime
from typing import Dict

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


# ─── Paleta de colores Ache Innovation ────────────────────────────────────────
COLOR_PRIMARY   = colors.HexColor("#1a1a2e")
COLOR_ACCENT    = colors.HexColor("#667eea")
COLOR_GREEN     = colors.HexColor("#27ae60")
COLOR_ORANGE    = colors.HexColor("#e8a020")
COLOR_WARNING   = colors.HexColor("#fff3cd")
COLOR_LIGHT     = colors.HexColor("#f0f2f6")
COLOR_WHITE     = colors.white


def _styles():
    base = getSampleStyleSheet()

    title = ParagraphStyle(
        "AcheTitle",
        parent=base["Title"],
        fontSize=22, textColor=COLOR_WHITE,
        spaceAfter=4, alignment=TA_CENTER, fontName="Helvetica-Bold"
    )
    subtitle = ParagraphStyle(
        "AcheSubtitle",
        parent=base["Normal"],
        fontSize=10, textColor=colors.HexColor("#ccccff"),
        spaceAfter=0, alignment=TA_CENTER
    )
    section = ParagraphStyle(
        "AcheSection",
        parent=base["Heading2"],
        fontSize=13, textColor=COLOR_PRIMARY,
        spaceBefore=14, spaceAfter=6,
        fontName="Helvetica-Bold",
        borderPad=4
    )
    body = ParagraphStyle(
        "AcheBody",
        parent=base["Normal"],
        fontSize=10, textColor=colors.HexColor("#333333"),
        spaceAfter=4, leading=14, alignment=TA_JUSTIFY
    )
    bullet = ParagraphStyle(
        "AcheBullet",
        parent=body,
        leftIndent=14, bulletIndent=4, spaceAfter=3
    )
    warning = ParagraphStyle(
        "AcheWarning",
        parent=body,
        backColor=COLOR_WARNING,
        borderColor=COLOR_ORANGE,
        borderWidth=1, borderPad=6,
        textColor=colors.HexColor("#856404"),
        fontSize=9
    )
    small = ParagraphStyle(
        "AcheSmall",
        parent=body,
        fontSize=8, textColor=colors.gray
    )

    return {
        "title": title, "subtitle": subtitle, "section": section,
        "body": body, "bullet": bullet, "warning": warning, "small": small
    }


def _header_table(report_data: Dict, S: dict):
    """Encabezado con fondo oscuro."""
    case = report_data.get("case", {})
    fecha = report_data.get("fecha", datetime.now().strftime("%d/%m/%Y %H:%M"))

    header_data = [
        [Paragraph("Ache Innovation", S["title"])],
        [Paragraph("Sistema de Parametrización Morfológica para Prótesis Caninas", S["subtitle"])],
        [Paragraph(f"Reporte generado: {fecha}", S["subtitle"])],
    ]
    tbl = Table(header_data, colWidths=[17 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_PRIMARY),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [COLOR_PRIMARY]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    return tbl


def _patient_table(case: Dict, S: dict):
    nombre = case.get("nombre_perro", "—")
    dueno  = case.get("nombre_dueno", "—")
    peso   = f"{case.get('peso_actual', '—')} kg"
    sexo   = case.get("sexo", "—")
    edad   = case.get("edad", "—")
    extrem = case.get("extremidad", "—")
    estado = case.get("estado", "—")
    vet    = case.get("vet_nombre", "—")
    notas  = case.get("notas", "Sin notas")

    data = [
        ["Campo", "Valor"],
        ["Nombre del paciente", nombre],
        ["Propietario",         dueno],
        ["Veterinario",         vet],
        ["Peso actual",         peso],
        ["Sexo / Edad",         f"{sexo} / {edad}"],
        ["Extremidad afectada", extrem],
        ["Estado clínico",      estado],
        ["Notas",               notas],
    ]
    tbl = Table(data, colWidths=[5 * cm, 12 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), COLOR_ACCENT),
        ("TEXTCOLOR",    (0, 0), (-1, 0), COLOR_WHITE),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0), 10),
        ("BACKGROUND",   (0, 1), (0, -1), COLOR_LIGHT),
        ("FONTNAME",     (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLOR_WHITE, COLOR_LIGHT]),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
    ]))
    return tbl


def _measurements_table(meas: Dict, breed_info: Dict, detected_breed: str, S: dict):
    munon_l  = meas.get("munon_largo_cm", 0)
    circunf_b = meas.get("munon_circunf_base_cm", 0)
    circunf_d = meas.get("munon_circunf_distal_cm", 0)
    scale    = meas.get("scale_mm_per_px", None)

    data = [
        ["Medida", "Valor", "Referencia raza"],
        ["Largo del muñón", f"{munon_l} cm",
         f"{breed_info.get('miembro_delantero_cm', '—')} cm (miembro ref.)"],
        ["Circunferencia en base", f"{circunf_b} cm", "—"],
        ["Circunferencia distal", f"{circunf_d} cm", "—"],
        ["Escala ArUco", f"{scale:.4f} mm/px" if scale else "Manual", "—"],
        ["Raza detectada", detected_breed or "No detectada",
         f"Talla: {breed_info.get('talla', '—')}"],
        ["Peso referencia raza",
         f"{breed_info.get('peso_min','—')}–{breed_info.get('peso_max','—')} kg",
         f"Altura: {breed_info.get('altura_min','—')}–{breed_info.get('altura_max','—')} cm"],
    ]
    tbl = Table(data, colWidths=[5.5 * cm, 5.5 * cm, 6 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), COLOR_GREEN),
        ("TEXTCOLOR",    (0, 0), (-1, 0), COLOR_WHITE),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLOR_WHITE, COLOR_LIGHT]),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
    ]))
    return tbl


def _prosthetic_table(specs: Dict, S: dict):
    if not specs:
        return Paragraph("No se generaron especificaciones de prótesis.", S["body"])

    data = [
        ["Parámetro", "Valor"],
        ["Longitud total de prótesis", f"{specs.get('longitud_total_cm', '—')} cm"],
        ["Diámetro del socket/encaje", f"{specs.get('diametro_socket_cm', '—')} cm"],
        ["Profundidad del encaje",     f"{specs.get('profundidad_socket_cm', '—')} cm"],
        ["Diámetro del eje",           f"{specs.get('diametro_pata_cm', '—')} cm"],
        ["Tipo de extremidad",         specs.get("tipo", "—")],
        ["Material recomendado",       specs.get("material", "PLA")],
    ]
    tbl = Table(data, colWidths=[8 * cm, 9 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), COLOR_ORANGE),
        ("TEXTCOLOR",    (0, 0), (-1, 0), COLOR_WHITE),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME",     (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("BACKGROUND",   (0, 1), (0, -1), COLOR_LIGHT),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLOR_WHITE, COLOR_LIGHT]),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
    ]))
    return tbl


def generate_pdf_report(report_data: Dict) -> bytes:
    """
    Genera el reporte PDF completo.

    Args:
        report_data: Dict con claves: case, measurements, breed_info,
                     detected_breed, prosthetic_specs, fecha

    Returns:
        Bytes del PDF generado
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2.5 * cm,
        title="Ache Innovation — Reporte Clínico",
        author="Ache Innovation"
    )

    S = _styles()
    story = []

    case          = report_data.get("case", {})
    meas          = report_data.get("measurements", {})
    breed_info    = report_data.get("breed_info", {})
    detected_breed = report_data.get("detected_breed", "No detectada")
    specs         = report_data.get("prosthetic_specs", {})
    extremidad    = case.get("extremidad", "")
    munon_largo   = meas.get("munon_largo_cm", 0)

    # ── Encabezado ──────────────────────────────────────────────────────────
    story.append(_header_table(report_data, S))
    story.append(Spacer(1, 0.4 * cm))

    # ── Datos del paciente ───────────────────────────────────────────────────
    story.append(Paragraph("1. Datos del Paciente", S["section"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_ACCENT))
    story.append(Spacer(1, 0.2 * cm))
    story.append(_patient_table(case, S))
    story.append(Spacer(1, 0.4 * cm))

    # ── Medidas morfológicas ─────────────────────────────────────────────────
    story.append(Paragraph("2. Medidas Morfológicas y Detección de Raza", S["section"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_GREEN))
    story.append(Spacer(1, 0.2 * cm))
    story.append(_measurements_table(meas, breed_info, detected_breed, S))
    story.append(Spacer(1, 0.4 * cm))

    # ── Especificaciones de prótesis ────────────────────────────────────────
    story.append(Paragraph("3. Especificaciones de Prótesis", S["section"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_ORANGE))
    story.append(Spacer(1, 0.2 * cm))
    story.append(_prosthetic_table(specs, S))
    story.append(Spacer(1, 0.4 * cm))

    # ── Guía quirúrgica ─────────────────────────────────────────────────────
    story.append(Paragraph("4. Guía Quirúrgica — Recomendaciones de Amputación", S["section"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY))
    story.append(Spacer(1, 0.2 * cm))

    story.append(Paragraph(
        "⚕️  AVISO: Esta guía es una herramienta de apoyo. "
        "La decisión quirúrgica final es responsabilidad exclusiva del veterinario tratante.",
        S["warning"]
    ))
    story.append(Spacer(1, 0.3 * cm))

    socket_depth = specs.get("profundidad_socket_cm", 4.0)
    munon_minimo = socket_depth + 2

    if "Delantera" in extremidad:
        articulacion = "codo (articulación humeroradial)"
        articulacion_evitar = "hombro"
    else:
        articulacion = "rodilla (articulación femorotibial)"
        articulacion_evitar = "cadera"

    guia_items = [
        f"<b>Nivel de corte recomendado:</b> {munon_minimo:.0f}–{munon_minimo + 3:.0f} cm "
        f"distales a la articulación del {articulacion}.",
        f"<b>Conservar articulación proximal:</b> Preservar el {articulacion} siempre que sea posible. "
        f"Evitar amputación a nivel del {articulacion_evitar} si existe tejido viable más distal.",
        "<b>Longitud mínima del muñón:</b> La longitud mínima debe garantizar al menos "
        f"{munon_minimo:.0f} cm desde la articulación para asegurar superficie de encaje.",
        "<b>Cierre del muñón:</b> Dejar colgajo de piel de 2–3 cm en el extremo distal "
        "para cubrir el hueso sin tensión excesiva.",
        "<b>Sección ósea:</b> Corte limpio perpendicular al eje longitudinal del hueso. "
        "Limar el extremo óseo para eliminar aristas.",
        "<b>Musculatura (mioplastia):</b> Seccionar y suturar los músculos antagonistas "
        "sobre el extremo óseo para dar forma cilíndrica al muñón.",
        "<b>Nervios:</b> Ligadura y sección proximal para prevenir la formación de neuromas.",
        "<b>Vasos sanguíneos:</b> Doble ligadura antes de la sección.",
        "<b>Forma objetivo del muñón:</b> Cilíndrica o ligeramente cónica — evitar forma bulbosa "
        "o muy cónica que dificulte el encaje.",
        "<b>Tiempo de cicatrización:</b> Esperar mínimo 6–8 semanas post-operatorio antes "
        "de iniciar el proceso de colocación de la prótesis.",
        "<b>Seguimiento:</b> Revisión de cicatriz y remodelación del muñón a las 2, 4 y 8 semanas.",
    ]

    for item in guia_items:
        story.append(Paragraph(f"• {item}", S["bullet"]))

    story.append(Spacer(1, 0.5 * cm))

    # ── Pie de página ────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        f"Ache Innovation — Sistemas de Movilidad Animal  |  "
        f"Generado: {report_data.get('fecha', '')}  |  "
        "Este documento es confidencial y de uso clínico exclusivo.",
        S["small"]
    ))

    doc.build(story)
    return buf.getvalue()
