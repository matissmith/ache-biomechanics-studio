"""
modules/guia_quirurgica.py
Guía Técnica Preliminar Ache Innovation v0.2
Evaluación de muñón protetizable — adaptada al caso activo.

Para integrar en app.py:
    from modules.guia_quirurgica import render_guia_quirurgica
    render_guia_quirurgica(caso_activo=caso_activo)
"""

import streamlit as st

# ─── Paleta ──────────────────────────────────────────────────────────────────
NAVY   = "#173555"
BLUE   = "#245E96"
RED    = "#8B1E1E"
ORANGE = "#6B4700"
GREEN  = "#1F5F32"

# ─── Helpers de estilo ────────────────────────────────────────────────────────

def _card(content_fn, border_color=BLUE, bg="#F0F4FA"):
    st.markdown(
        f"""<div style="border-left:4px solid {border_color};background:{bg};
                       padding:12px 16px;border-radius:0 6px 6px 0;margin:6px 0;">""",
        unsafe_allow_html=True)
    content_fn()
    st.markdown("</div>", unsafe_allow_html=True)


def _alert(title, items, color=RED, bg="#FDF3F3"):
    html = (f"<div style='border-left:4px solid {color};background:{bg};"
            f"padding:10px 14px;border-radius:0 6px 6px 0;margin:8px 0;'>"
            f"<strong style='color:{color};'>⚠  {title}</strong>"
            f"<ul style='margin:6px 0 0 0;padding-left:18px;font-size:.92em;color:#26384A !important;'>")
    for item in items:
        html += f"<li>{item}</li>"
    html += "</ul></div>"
    st.markdown(html, unsafe_allow_html=True)


def _compat_box(letter, title, criteria, color, bg):
    html = (f"<div style='border-left:4px solid {color};background:{bg};"
            f"padding:10px 14px;border-radius:0 6px 6px 0;margin:6px 0;'>"
            f"<strong style='color:{color};font-size:1.0em;'>Nivel {letter} — {title}</strong>"
            f"<ul style='margin:6px 0 0 0;padding-left:18px;font-size:.90em;color:#26384A !important;'>")
    for c in criteria:
        html += f"<li>{c}</li>"
    html += "</ul></div>"
    st.markdown(html, unsafe_allow_html=True)


def _section_header(num, title):
    st.markdown(
        f"<h3 style='color:{NAVY};border-bottom:2px solid {BLUE};"
        f"padding-bottom:4px;margin-top:20px;'>{num}.  {title}</h3>",
        unsafe_allow_html=True)


def _h4(title):
    st.markdown(
        f"<h4 style='color:{BLUE};margin-top:14px;margin-bottom:4px;'>{title}</h4>",
        unsafe_allow_html=True)


def _html_table(headers, rows, col_widths=None):
    w = col_widths or ["auto"] * len(headers)
    style_tbl = "border-collapse:collapse;width:100%;font-size:.88em;margin:8px 0;"
    style_th   = f"background:{NAVY};color:white !important;padding:7px 10px;text-align:left;"
    td_even    = "padding:6px 10px;background:#F9FAFB;color:#26384A !important;"
    td_odd     = "padding:6px 10px;background:#FFFFFF;color:#26384A !important;"
    html = f"<table style='{style_tbl}'><thead><tr>"
    for i, h in enumerate(headers):
        ww = f"width:{w[i]};" if col_widths else ""
        html += f"<th style='{style_th}{ww}'>{h}</th>"
    html += "</tr></thead><tbody>"
    for ri, row in enumerate(rows):
        s = td_even if ri % 2 == 0 else td_odd
        html += "<tr>"
        for cell in row:
            if isinstance(cell, tuple):
                txt, clr = cell
                html += f"<td style='{s}color:{clr};font-weight:bold;'>{txt}</td>"
            else:
                html += f"<td style='{s}'>{cell}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


# ─── Helpers de personalización ───────────────────────────────────────────────

def _val(v, suffix="", default="—"):
    """Formatea un valor del caso: muestra el valor o '—' si es None/'—'/0."""
    if v is None or v == "—" or v == 0:
        return default
    return f"{v}{suffix}"


def _es_delantera(extremidad: str) -> bool:
    ext = str(extremidad).lower()
    return "delantera" in ext or "torácica" in ext or "toracica" in ext or "anterior" in ext


def _talla_from_breed_info(breed_info: dict) -> str:
    """Devuelve la talla desde breed_info, o estima desde el peso."""
    if not breed_info:
        return ""
    return breed_info.get("talla", "")


def _peso_max_protesis(peso_kg) -> str:
    """Peso máximo orientativo de la prótesis (2-3% del peso corporal)."""
    try:
        p = float(peso_kg)
        return f"{p*0.02*1000:.0f}–{p*0.03*1000:.0f} g"
    except Exception:
        return "—"


def _auto_clasificar(caso: dict) -> tuple[str, list[str]]:
    """
    Clasifica el caso en A/B/C/D automáticamente.
    Retorna (nivel: str, razones: list[str]).
    """
    razones_c, razones_b, razones_d = [], [], []

    causa = str(caso.get("causa", "")).lower()
    bcs   = caso.get("bcs")
    munon = caso.get("munon_largo_cm")
    breed_info = caso.get("breed_info") or {}
    medidas_ok = munon not in (None, "—", "") and float(munon) > 0 if munon not in (None, "—", "") else False

    if "oncol" in causa or "tumor" in causa:
        razones_c.append("Causa oncológica registrada → derivar a evaluación veterinaria urgente.")

    if bcs is not None:
        if bcs >= 8:
            razones_c.append(f"BCS {bcs}/9 (obesidad severa) — contraindica ajuste hasta reducción de peso.")
        elif bcs == 7:
            razones_b.append(f"BCS {bcs}/9 (sobrepeso leve) — monitorear durante adaptación.")

    if not medidas_ok:
        razones_d.append("Sin medidas del muñón — necesarias para diseñar el socket.")

    if caso.get("nivel_amputacion") in (1, 2):
        razones_c.append(f"Nivel {caso['nivel_amputacion']} (sin palanca ósea) — prótesis externa convencional no recomendada.")

    if razones_c:
        return "C", razones_c
    if razones_d:
        return "D", razones_d
    if razones_b:
        return "B", razones_b
    return "A", ["Sin alertas mayores detectadas automáticamente."]


# ─── Recomendaciones por talla ────────────────────────────────────────────────

_TALLA_SPECS = {
    "toy": {
        "label": "Toy (< 5 kg)",
        "socket_pared": "1.5–2 mm",
        "liner": "Silicona ultra-suave (Shore A 10-20) o EVA 3 mm",
        "material": "PETG o TPU flexible — PLA demasiado frágil",
        "peso_max_proto": "< 80 g totales",
        "pie": "TPU muy flexible, sin eje rígido, suela de silicona",
        "suspension": "Correa de velcro liviana o manga de silicona",
        "nota": "Huesos frágiles y muñones muy cortos: socket debe repartir carga uniformemente. "
                "Evitar cualquier borde rígido sin almohadillado.",
    },
    "pequeño": {
        "label": "Pequeño (5–10 kg)",
        "socket_pared": "2–3 mm",
        "liner": "Silicona Shore A 20-30 o EVA 4 mm",
        "material": "PETG o Nylon PA12 — buena relación rigidez/peso",
        "peso_max_proto": "80–200 g",
        "pie": "TPU con eje de PETG, suela de goma antideslizante",
        "suspension": "Arnés tipo chaleco o manga con pin",
        "nota": "Verificar longitud funcional respecto al miembro contralateral. "
                "Ajustar altura del pie para compensar discrepancia de longitud.",
    },
    "mediano": {
        "label": "Mediano (10–25 kg)",
        "socket_pared": "3–4 mm",
        "liner": "Silicona Shore A 30-40 o poliuretano",
        "material": "Nylon PA12 o PETG reforzado — considerar fibra de carbono en zona estructural",
        "peso_max_proto": "200–500 g",
        "pie": "Carbono + TPU o PETG articulado, suela de caucho vulcanizado",
        "suspension": "Succión o arnés con correa inguinal (miembro pelviano)",
        "nota": "Paciente con mayor actividad esperada. Diseñar para fatiga de ciclos altos. "
                "Incluir zona de retorno elástico en el pie.",
    },
    "grande": {
        "label": "Grande (25–45 kg)",
        "socket_pared": "4–5 mm con refuerzo en zona proximal",
        "liner": "Silicona Shore A 35-45 de 6 mm de espesor",
        "material": "PA12 o compuesto de fibra de carbono — aluminio para refuerzo axial",
        "peso_max_proto": "500–900 g",
        "pie": "Pie de carbono con suela de goma dura, eje de aluminio o acero",
        "suspension": "Sistema de succión + correa de seguridad; sistema de pin en nivel distal",
        "nota": "Alta carga de impacto. Verificar uniones mecánicas con torque elevado. "
                "Revisión cada 3 meses obligatoria por desgaste acelerado.",
    },
    "gigante": {
        "label": "Gigante (> 45 kg)",
        "socket_pared": "5–7 mm, considerar refuerzo metálico",
        "liner": "Silicona gruesa 8–10 mm o compuesto gel-silicona",
        "material": "Compuesto de fibra de carbono + aluminio estructural; PETG/PA solo en zonas no de carga",
        "peso_max_proto": "900–1500 g",
        "pie": "Pie de carbono de alta resistencia, suela de goma vulcanizada gruesa, eje de acero",
        "suspension": "Sistema de suspensión de dos correas + fijación proximal; evaluar integración con ortesis",
        "nota": "Inercia y masa elevadas: el paciente requiere rehabilitación física previa. "
                "Revisar integridad de cada componente en cada control.",
    },
}

_NIVEL_NOTAS = {
    1: ("No recomendado", RED,
        "Sin muñón aprovechable. La prótesis externa convencional no tiene punto de apoyo. "
        "Evaluar opciones de ortesis de compensación o ITAP si el equipo clínico lo considera."),
    2: ("Muy difícil", RED,
        "Sin palanca ósea. El encaje no tiene punto estable. Requiere sistema de suspensión complejo "
        "(arnés full-body). Solo considerar con equipo especializado y expectativas realistas."),
    3: ("Factible con restricciones", ORANGE,
        "Palanca corta. Requiere codo/stifle protésico y sistema de suspensión avanzado. "
        "Socket proximal con almohadillado en trocánter/escápula. Resultado funcional limitado."),
    4: ("Factible", ORANGE,
        "Mejor palanca que nivel 3. El codo/stifle protésico sigue siendo necesario. "
        "La propulsión/soporte estará reducida pero puede lograrse marcha funcional."),
    5: ("Buena aptitud", GREEN,
        "La articulación proximal (codo o stifle) está preservada — punto de apoyo estable. "
        "El socket puede ser más simple. Necesita articulación protésica distal (codo externo o stifle externo)."),
    6: ("Óptima ✓", GREEN,
        "Mejor escenario funcional. La articulación proximal y la palanca ósea permiten marcha "
        "eficiente. Socket convencional, sin articulación intermedia necesaria. Retorno elástico en pie."),
    7: ("Excelente ✓", GREEN,
        "Amputación parcial distal (carpo/tarso o dedos). Mínima pérdida funcional. "
        "Bota protésica o pie parcial. Adaptación muy rápida y pronóstico excelente."),
}


# ══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def render_guia_quirurgica(caso_activo: dict = None):
    """
    Renderiza la Guía Técnica Ache Innovation v0.2, personalizada al caso activo.

    Parameters
    ----------
    caso_activo : dict, optional
        Dict con claves: nombre_paciente, raza, peso_kg, edad, extremidad,
        nivel_amputacion (int 1-7), causa, bcs (int 1-9), munon_largo_cm,
        munon_circunf_base_cm, munon_circunf_distal_cm, longitud_protesis_cm,
        profundidad_socket_cm, material_protesis, breed_info (dict).
    """
    caso = caso_activo or {}

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:#FFFFFF;border:1px solid #C9D8E8;border-left:5px solid #F2AA24;
                border-radius:16px;padding:16px 18px;margin:0 0 16px 0;
                box-shadow:0 10px 24px rgba(23,53,85,.06);">
        <div style="color:#173555;font-weight:900;font-size:1.12rem;">
            🩺 Guía técnica · v0.2 — personalizada al caso
        </div>
        <div style="color:#5B6E82;font-weight:600;margin-top:5px;">
            Evaluación de muñón protetizable · Ache Innovation
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Banner caso activo (rico y personalizado) ─────────────────────────────
    if caso:
        nombre    = caso.get("nombre_paciente") or caso.get("nombre_perro") or "—"
        raza      = caso.get("raza", "—")
        peso      = caso.get("peso_kg", "—")
        ext       = caso.get("extremidad", "—")
        nivel_num = caso.get("nivel_amputacion")
        causa_str = caso.get("causa", "—")
        bcs_val   = caso.get("bcs")
        munon_l   = caso.get("munon_largo_cm", "—")
        munon_cb  = caso.get("munon_circunf_base_cm", "—")
        munon_cd  = caso.get("munon_circunf_distal_cm", "—")
        long_prot = caso.get("longitud_protesis_cm", "—")
        mat_prot  = caso.get("material_protesis", "—")
        breed_info = caso.get("breed_info") or {}
        talla     = _talla_from_breed_info(breed_info)

        nivel_label = f"Nivel {nivel_num}" if nivel_num else "No registrado"
        bcs_label   = f"BCS {bcs_val}/9" if bcs_val else "—"
        peso_proto  = _peso_max_protesis(peso) if peso != "—" else "—"

        # Determinar tipo de extremidad para mostrar
        tipo_ext = "🦾 Torácica" if _es_delantera(ext) else "🦵 Pelviana"

        st.markdown(f"""
        <div style="background:#F0F6FF;border:1px solid #C9D8E8;border-radius:14px;
                    padding:14px 18px;margin-bottom:12px;">
            <div style="font-weight:900;color:{NAVY};font-size:1.05rem;margin-bottom:10px;">
                📋 Caso activo: <span style="color:{BLUE};">{nombre}</span>
                <span style="font-weight:400;font-size:.9rem;color:#5B6E82;"> · {raza}</span>
            </div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;font-size:.92rem;">
                <div><b>Peso:</b> {_val(peso, ' kg')}</div>
                <div><b>Extremidad:</b> {tipo_ext} {ext}</div>
                <div><b>Nivel amputación:</b> {nivel_label}</div>
                <div><b>Causa:</b> {causa_str}</div>
                <div><b>BCS:</b> {bcs_label}</div>
                <div><b>Talla:</b> {talla.title() if talla else '—'}</div>
                <div><b>Muñón largo:</b> {_val(munon_l, ' cm')}</div>
                <div><b>Circunf. base:</b> {_val(munon_cb, ' cm')}</div>
                <div><b>Circunf. distal:</b> {_val(munon_cd, ' cm')}</div>
                <div><b>Long. prótesis:</b> {_val(long_prot, ' cm')}</div>
                <div><b>Material:</b> {mat_prot}</div>
                <div><b>Peso máx. proto:</b> {peso_proto}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Alertas automáticas inmediatas
        causa_lower = causa_str.lower()
        if "oncol" in causa_lower or "tumor" in causa_lower:
            _alert("⚠ Alerta oncológica automática",
                   ["Causa oncológica registrada en el caso.",
                    "La preservación del muñón puede estar contraindicada si compromete márgenes.",
                    "Derivar inmediatamente a evaluación oncológica veterinaria."])
        if bcs_val and bcs_val >= 8:
            _alert(f"⚠ BCS {bcs_val}/9 — Obesidad severa",
                   [f"BCS {bcs_val} contraindica el ajuste protésico hasta reducción de peso.",
                    "El exceso de carga puede causar lesiones en el muñón y el miembro contralateral."],
                   color=ORANGE, bg="#FFF8EE")
        elif bcs_val and bcs_val == 7:
            _alert(f"BCS {bcs_val}/9 — Sobrepeso leve",
                   ["Monitorear evolución durante la adaptación. Plan de control de peso recomendado."],
                   color=ORANGE, bg="#FFF8EE")
    else:
        st.caption("ℹ Sin caso activo. La guía funciona como referencia general.")

    st.markdown("---")

    with st.expander("📋  Uso previsto y límites de este documento", expanded=False):
        st.markdown(
            "_Documento de apoyo. No es una guía quirúrgica autónoma. "
            "No reemplaza evaluación clínica, radiográfica, oncológica, anestésica "
            "ni criterio del veterinario o cirujano responsable._"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    tabs = st.tabs([
        "⚕️ Clínico",
        "📐 Biomecánica & Niveles",
        "📊 Clasificación",
        "🔩 Diseño protésico",
        "🗓 Adaptación",
        "✅ Checklists",
        "📚 Referencia",
    ])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — CLÍNICO
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[0]:

        _section_header(1, "Principio clínico central")
        st.markdown(
            "> *« Si el veterinario considera viable preservar el muñón, ¿qué condiciones "
            "morfológicas y de tejidos debe tener para ser compatible con una prótesis externa? »*"
        )
        st.markdown(
            "La decisión quirúrgica prioriza salud, analgesia, márgenes oncológicos, control "
            "de infección, calidad de vida y rehabilitación. La compatibilidad protésica es un "
            "factor **adicional**, no el dominante."
        )

        # Auto-seleccionar causa desde el caso activo
        _causas = ["Traumática", "Congénita / malformativa", "Oncológica",
                   "Infecciosa", "Neurológica / funcional", "Post-amputación previa", "Desconocida"]
        _idx_causa = 0
        if caso:
            _causa_caso = str(caso.get("causa", "")).strip()
            for i, c in enumerate(_causas):
                if _causa_caso.lower().replace("ó","o").replace("é","e") in c.lower().replace("ó","o").replace("é","e"):
                    _idx_causa = i
                    break

        _section_header(2, "Clasificación inicial del caso")
        tipo = st.selectbox(
            "Origen del caso",
            _causas,
            index=_idx_causa,
            help="Se pre-selecciona automáticamente desde el caso activo cuando está disponible."
        )
        if "Onco" in tipo or "onco" in tipo:
            _alert(
                "Alerta crítica oncológica",
                ["En casos tumorales la preservación del muñón puede estar contraindicada.",
                 "Derivar a evaluación oncológica veterinaria antes de continuar.",
                 "La longitud del muñón en contexto oncológico es decisión exclusiva del equipo quirúrgico."]
            )

        _section_header(4, "Condiciones mínimas para muñón protetizable")
        bcs_caso = caso.get("bcs") if caso else None
        for c in [
            "Viabilidad de piel y tejidos blandos: cobertura adecuada, sin tensión.",
            "Ausencia de infección activa, heridas abiertas o necrosis.",
            "Dolor controlado o ausente.",
            "Cobertura adecuada sobre prominencias óseas.",
            "Forma compatible con socket (cilíndrica o levemente cónica).",
            "Longitud útil ≥30% del segmento óseo.",
            "Capacidad de suspensión y control rotacional.",
            "Evaluación neurológica: descartar neuroma o anestesia.",
            "Rango articular útil en articulaciones preservadas.",
            "BCS 4-6/9 (BCS ≥8 retrasa o contraindica el ajuste).",
            "Tutor comprometido con el protocolo de adaptación."
        ]:
            # Marcar visualmente si el caso activo viola alguna condición
            bcs_flag = "⚠ " if (bcs_caso and bcs_caso >= 8 and "BCS" in c) else ""
            st.markdown(f"• {bcs_flag}{c}")

        _section_header(5, "Contraindicaciones y alertas de alto riesgo")
        _alert(
            "Alertar y derivar ante cualquiera de las siguientes:",
            [
                "Sospecha o confirmación de neoplasia activa.",
                "Infección activa del muñón o tejidos perilesionales.",
                "Necrosis o vascularización comprometida.",
                "Dolor severo no controlado o neuropático intenso.",
                "Herida abierta, úlcera activa o piel inestable.",
                "Muñón extremadamente corto (<30% del segmento).",
                "Prominencias óseas sin cobertura de tejidos blandos.",
                "Neuroma con hipersensibilidad severa.",
                "Contracturas severas de articulaciones proximales.",
                "BCS 8-9 o enfermedad sistémica descompensada.",
                "Imposibilidad de seguimiento veterinario profesional."
            ]
        )

        _section_header(7, "Escalas de evaluación funcional")
        _h4("7.1  Dolor crónico")
        _html_table(
            ["Escala", "Ítems", "Puntaje", "Uso recomendado"],
            [
                ["CBPI — Canine Brief Pain Inventory", "11 (sev. ×4 + interf. ×7)",
                 "Sev: 0-40 / Int: 0-60", "Baseline, 4 sem, 3 m, 6 m. Validada para OA y dolor oncológico."],
                ["HCPI — Helsinki Chronic Pain Index", "11", "0-44",
                 "Monitoreo de adaptación protésica a largo plazo."],
            ], col_widths=["25%","22%","18%","35%"])
        _h4("7.2  Dolor agudo / post-operatorio")
        _html_table(
            ["Escala", "Ítems", "Puntaje", "Uso recomendado"],
            [["CMPS-SF (Glasgow Short Form)", "6 categorías",
              "0-24 (umbral: >5)", "Post-op y evaluación del muñón previo al ajuste."]],
            col_widths=["28%","18%","18%","36%"])
        _h4("7.3  Protocolo mínimo")
        for i, t in enumerate([
            "Baseline pre-protésico: CBPI + CMPS-SF + scoring observacional.",
            "4 semanas post-ajuste: CBPI + scoring.",
            "3 meses: CBPI + HCPI + revisión de socket.",
            "6 meses y anuales: batería completa."
        ], 1):
            st.markdown(f"{i}. {t}")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — BIOMECÁNICA & NIVELES
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[1]:

        _section_header(3, "Niveles de amputación y sus implicaciones protésicas")

        # Auto-seleccionar miembro desde el caso activo
        _default_member = 0
        if caso:
            if not _es_delantera(caso.get("extremidad", "")):
                _default_member = 1

        member = st.radio(
            "Miembro a consultar",
            ["Torácico (anterior)", "Pelviano (posterior)"],
            index=_default_member,
            horizontal=True,
            help="Se pre-selecciona automáticamente desde el caso activo."
        )

        nivel_actual = caso.get("nivel_amputacion") if caso else None

        if "Torácico" in member:
            _html_table(
                ["Niv.", "Nombre", "Descripción", "Palanca", "Aptitud", "Observaciones"],
                [
                    ["1", "Cuarto anterior",          "Escápula + húmero completos",          "Ninguna",  ("No recomendada", RED),    "Sin muñón aprovechable."],
                    ["2", "Desart. hombro",            "Húmero completo retirado",             "Mínima",   ("Muy difícil", RED),        "Encaje extremadamente complejo."],
                    ["3", "Transhumeral proximal",     ">50% del húmero retirado",             "Corta",    ("Factible *", ORANGE),      "Requiere codo protésico."],
                    ["4", "Transhumeral medio/distal", "<50% del húmero retirado",             "Moderada", ("Factible", ORANGE),        "Mejor palanca; codo protésico necesario."],
                    ["5", "Desart. del codo",          "Húmero completo preservado",           "Buena",    ("Buena", GREEN),            "Suspensión estable; codo externo requerido."],
                    ["6", "Transradial",               "Radio/cúbito parcial o completo",      "Óptima",   ("Óptima ✓", GREEN),         "Mejor escenario; codo preservado."],
                    ["7", "Desart. carpo / parcial",   "Carpo, metacarpo o dedos",             "Completa", ("Excelente ✓", GREEN),      "Casos más simples; bota o pie parcial."],
                ], col_widths=["4%","17%","22%","9%","13%","35%"])
        else:
            _html_table(
                ["Niv.", "Nombre", "Descripción", "Palanca", "Aptitud", "Observaciones"],
                [
                    ["1", "Hemipelvectomía",           "Pelvis + fémur retirados",             "Ninguna",  ("No recomendada", RED),    "Sin muñón."],
                    ["2", "Desart. de cadera",          "Fémur completo retirado",              "Mínima",   ("Muy difícil", RED),        "Sin palanca ósea."],
                    ["3", "Transfemoral proximal",      ">50% del fémur retirado",              "Corta",    ("Factible *", ORANGE),      "Requiere rodilla protésica (stifle)."],
                    ["4", "Transfemoral medio/distal",  "<50% del fémur retirado",              "Moderada", ("Factible", ORANGE),        "Rodilla protésica; mejor control."],
                    ["5", "Desart. del stifle",         "Fémur completo preservado",            "Buena",    ("Buena", GREEN),            "Palanca excelente; stifle externo requerido."],
                    ["6", "Transtibial",                "Tibia/fíbula parcial o completa",      "Óptima",   ("Óptima ✓", GREEN),         "Mejor escenario; stifle preservado = propulsión."],
                    ["7", "Desart. tarso / parcial",    "Tarso, metatarso o dedos",             "Completa", ("Excelente ✓", GREEN),      "Casos más simples; bota o pie parcial."],
                ], col_widths=["4%","17%","22%","9%","13%","35%"])

        st.caption("* Factible con restricciones — requiere evaluación avanzada. Niveles 1-2: no recomendados.")

        # ── Nota personalizada para el nivel del caso activo ──────────────────
        if nivel_actual and nivel_actual in _NIVEL_NOTAS:
            apt_label, apt_color, apt_nota = _NIVEL_NOTAS[nivel_actual]
            st.markdown(f"""
            <div style="border-left:4px solid {apt_color};background:#F8FAFD;
                        padding:12px 16px;border-radius:0 8px 8px 0;margin:14px 0;">
                <strong style="color:{apt_color};">
                    🎯 Caso activo — Nivel {nivel_actual}: {apt_label}
                </strong>
                <p style="margin:6px 0 0 0;color:#26384A;font-size:.94em;">{apt_nota}</p>
            </div>
            """, unsafe_allow_html=True)

        _section_header(6, "Biomecánica por extremidad")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Miembro torácico**")
            st.markdown(
                "Soporta ~60% del peso corporal. Una prótesis anterior bien ajustada redistribuye "
                "el 21% del peso hacia la prótesis, reduciendo la carga contralateral del 49% al 35%."
            )
            st.markdown("**Prioridades:** superficie amplia, amortiguación, control medio-lateral, "
                        "prevención de rotación del socket.")
        with col2:
            st.markdown("**Miembro pelviano**")
            st.markdown(
                "Principal generador de propulsión. La preservación del stifle es "
                "el factor más determinante en el diseño."
            )
            st.markdown("**Prioridades:** retorno elástico, longitud funcional correcta, "
                        "alineación cadera-stifle-tarso, tope de hiperextensión.")

        _alert(
            "Compensación en miembros remanentes",
            ["El riesgo de osteoartritis acelerada en miembros sanos es real tras cualquier amputación.",
             "La prótesis no solo restaura movilidad: reduce la sobrecarga compensatoria a largo plazo."],
            color=ORANGE, bg="#FDF8EE")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — CLASIFICACIÓN A/B/C/D
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[2]:

        _section_header(10, "Clasificación de compatibilidad protésica")

        # ── Clasificación automática basada en el caso ─────────────────────────
        if caso:
            nivel_auto, razones_auto = _auto_clasificar(caso)
            color_auto = {
                "A": GREEN, "B": ORANGE, "C": RED, "D": "#777777"
            }[nivel_auto]
            bg_auto = {"A": "#F0F7F0", "B": "#FDF8EE", "C": "#FDF3F3", "D": "#F5F5F5"}[nivel_auto]
            titulos = {
                "A": "Potencialmente compatible",
                "B": "Compatible con advertencias",
                "C": "No recomendado sin evaluación avanzada",
                "D": "Información insuficiente",
            }
            st.markdown("#### 🤖 Clasificación automática del caso activo")
            _compat_box(nivel_auto, titulos[nivel_auto], razones_auto, color_auto, bg_auto)
            st.markdown("---")

        st.markdown("#### Evaluación manual detallada")
        st.markdown("Marcá ítems adicionales que el sistema no puede inferir automáticamente:")

        # Pre-llenar desde caso activo donde sea posible
        _causa_lower  = str((caso or {}).get("causa", "")).lower()
        _bcs          = (caso or {}).get("bcs")
        _munon_val    = (caso or {}).get("munon_largo_cm")
        _nivel_amp    = (caso or {}).get("nivel_amputacion")

        _default_tumor   = "oncol" in _causa_lower or "tumor" in _causa_lower
        _default_bcs_alt = bool(_bcs) and _bcs >= 8
        _default_bcs_7   = bool(_bcs) and _bcs == 7
        _default_sin_med = _munon_val in (None, "—", "", 0)
        _default_niv_1_2 = _nivel_amp in (1, 2)

        c1, c2 = st.columns(2)
        with c1:
            tumor        = st.checkbox("Sospecha oncológica",             value=_default_tumor,   key="cls_tumor")
            infeccion    = st.checkbox("Infección activa",                value=False,            key="cls_infec")
            herida       = st.checkbox("Herida abierta / piel inestable", value=False,            key="cls_herida")
            dolor_severo = st.checkbox("Dolor severo no controlado",      value=False,            key="cls_dolor")
        with c2:
            longitud_corta = st.checkbox("Muñón <30% del segmento óseo",           value=_default_niv_1_2, key="cls_longc")
            sin_cobertura  = st.checkbox("Prominencias óseas sin cobertura",        value=False,            key="cls_cob")
            bcs_alto       = st.checkbox("BCS 8-9 (obesidad severa)",               value=_default_bcs_alt, key="cls_bcsalt")
            sin_vet        = st.checkbox("Sin veterinario responsable",             value=False,            key="cls_vet")

        c3, c4 = st.columns(2)
        with c3:
            longitud_borderline = st.checkbox("Muñón 30-40% del segmento (borderline)", value=False,       key="cls_longb")
            cicatrizacion       = st.checkbox("Cicatrización incompleta (<8 sem)",       value=False,       key="cls_cic")
            bcs_7               = st.checkbox("BCS 7 (sobrepeso leve)",                  value=_default_bcs_7, key="cls_bcs7")
        with c4:
            sin_escala    = st.checkbox("Sin escala de referencia en fotos", value=False,           key="cls_esc")
            sin_medidas   = st.checkbox("Sin medidas del muñón",             value=_default_sin_med, key="cls_med")
            info_incompleta = st.checkbox("Información clínica incompleta",  value=False,            key="cls_info")

        alertas_c = [tumor, infeccion, herida, dolor_severo,
                     longitud_corta, sin_cobertura, bcs_alto, sin_vet]
        alertas_b = [longitud_borderline, cicatrizacion, bcs_7, sin_escala]
        alertas_d = [sin_medidas, info_incompleta]

        st.markdown("---")
        st.markdown("#### Resultado de la evaluación manual:")
        if any(alertas_c):
            _compat_box("C", "No recomendado sin evaluación avanzada",
                ["Uno o más criterios de alto riesgo presentes.",
                 "Derivar a evaluación veterinaria antes de continuar."],
                RED, "#FDF3F3")
        elif any(alertas_d):
            _compat_box("D", "Información insuficiente",
                ["Faltan datos clínicos o morfológicos críticos."],
                "#777777", "#F5F5F5")
        elif any(alertas_b):
            _compat_box("B", "Compatible con advertencias",
                ["El caso puede ser viable pero hay factores a resolver.",
                 "Revisar los ítems marcados antes del ajuste."],
                ORANGE, "#FDF8EE")
        else:
            _compat_box("A", "Potencialmente compatible",
                ["Sin alertas mayores identificadas."],
                GREEN, "#F0F7F0")

        st.markdown("---")
        with st.expander("Ver criterios completos A / B / C / D"):
            _compat_box("A", "Potencialmente compatible",
                ["Sin sospecha oncológica.", "Sin infección, herida ni necrosis.", "Dolor controlado.",
                 "Longitud ≥30%.", "Piel estable.", "BCS 4-6/9.", "Veterinario identificado.",
                 "Fotos con escala válida.", "Tutor comprometido."], GREEN, "#F0F7F0")
            _compat_box("B", "Compatible con advertencias",
                ["Longitud 30-40% (borderline).", "Irregularidades menores de piel.",
                 "Cicatrización incompleta (<8 sem).", "BCS 7/9.", "Contractura articular leve.",
                 "Escala ausente.", "Información parcial."], ORANGE, "#FDF8EE")
            _compat_box("C", "No recomendado sin evaluación avanzada",
                ["Neoplasia activa.", "Infección.", "Piel deficiente.", "Herida abierta.",
                 "Dolor severo.", "Longitud <30%.", "Prominencias sin cobertura.",
                 "Neuroma severo.", "BCS 8-9.", "Sin veterinario."], RED, "#FDF3F3")
            _compat_box("D", "Información insuficiente",
                ["Fotos no evaluables.", "Sin medidas del muñón.",
                 "Datos contradictorios.", "No se puede descartar oncología."],
                "#777777", "#F5F5F5")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — DISEÑO PROTÉSICO
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[3]:

        # ── Recomendaciones personalizadas por talla/raza ─────────────────────
        talla_caso   = _talla_from_breed_info((caso or {}).get("breed_info") or {})
        specs_caso   = {
            "longitud": (caso or {}).get("longitud_protesis_cm", "—"),
            "socket":   (caso or {}).get("profundidad_socket_cm", "—"),
            "material": (caso or {}).get("material_protesis", "—"),
            "extremidad": (caso or {}).get("tipo_extremidad_disenio", "—"),
        }
        peso_caso = (caso or {}).get("peso_kg", "—")

        if talla_caso and talla_caso in _TALLA_SPECS:
            spec = _TALLA_SPECS[talla_caso]
            st.markdown(f"""
            <div style="background:#F0F6FF;border:1px solid #B8D0EE;border-radius:14px;
                        padding:14px 18px;margin-bottom:14px;">
                <div style="font-weight:900;color:{NAVY};font-size:1.0rem;margin-bottom:8px;">
                    🐾 Recomendaciones para talla <b>{spec['label']}</b>
                </div>
                <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px;font-size:.92rem;color:#26384A;">
                    <div>📦 <b>Pared socket:</b> {spec['socket_pared']}</div>
                    <div>🧴 <b>Liner:</b> {spec['liner']}</div>
                    <div>🔩 <b>Material estructura:</b> {spec['material']}</div>
                    <div>⚖️ <b>Peso máx. prótesis:</b> {spec['peso_max_proto']}</div>
                    <div>👟 <b>Pie protésico:</b> {spec['pie']}</div>
                    <div>🎗️ <b>Suspensión:</b> {spec['suspension']}</div>
                </div>
                <p style="margin:10px 0 0 0;font-size:.89em;color:#4A5E72;border-top:1px solid #C9D8E8;padding-top:8px;">
                    ⚠ {spec['nota']}
                </p>
            </div>
            """, unsafe_allow_html=True)

        elif peso_caso != "—":
            # Estimación por peso si no hay breed_info
            try:
                p = float(peso_caso)
                est_talla = ("toy" if p < 5 else "pequeño" if p < 10
                             else "mediano" if p < 25 else "grande" if p < 45 else "gigante")
                spec = _TALLA_SPECS[est_talla]
                st.markdown(f"""
                <div style="background:#F5F7FA;border:1px solid #C9D8E8;border-radius:14px;
                            padding:14px 18px;margin-bottom:14px;">
                    <div style="font-weight:900;color:{NAVY};font-size:1.0rem;margin-bottom:8px;">
                        🐾 Recomendaciones estimadas por peso ({peso_caso} kg → {spec['label']})
                    </div>
                    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px;font-size:.92rem;color:#26384A;">
                        <div>📦 <b>Pared socket:</b> {spec['socket_pared']}</div>
                        <div>🧴 <b>Liner:</b> {spec['liner']}</div>
                        <div>🔩 <b>Material:</b> {spec['material']}</div>
                        <div>⚖️ <b>Peso máx. prótesis:</b> {spec['peso_max_proto']}</div>
                        <div>👟 <b>Pie:</b> {spec['pie']}</div>
                        <div>🎗️ <b>Suspensión:</b> {spec['suspension']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                pass

        # ── Resumen del diseño actual ─────────────────────────────────────────
        if specs_caso["longitud"] != "—":
            st.markdown(f"""
            <div style="background:#F0FFF4;border:1px solid #A8D5B5;border-radius:12px;
                        padding:12px 16px;margin-bottom:12px;">
                <div style="font-weight:800;color:{GREEN};margin-bottom:6px;">
                    ✅ Diseño paramétrico actual
                </div>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;font-size:.91rem;color:#26384A;">
                    <div><b>Longitud total:</b> {_val(specs_caso['longitud'], ' cm')}</div>
                    <div><b>Prof. socket:</b> {_val(specs_caso['socket'], ' cm')}</div>
                    <div><b>Material:</b> {specs_caso['material']}</div>
                    <div><b>Extremidad:</b> {specs_caso['extremidad']}</div>
                    <div><b>Peso corporal:</b> {_val(peso_caso, ' kg')}</div>
                    <div><b>Peso máx. proto:</b> {_peso_max_protesis(peso_caso)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Recomendaciones por nivel de amputación en diseño ─────────────────
        nivel_d = (caso or {}).get("nivel_amputacion")
        if nivel_d and nivel_d in _NIVEL_NOTAS:
            apt_l, apt_c, apt_n = _NIVEL_NOTAS[nivel_d]
            st.markdown(f"""
            <div style="border-left:4px solid {apt_c};background:#F8FAFD;
                        padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:12px;">
                <strong style="color:{apt_c};">Implicaciones de diseño — Nivel {nivel_d}: {apt_l}</strong>
                <p style="margin:4px 0 0 0;font-size:.92em;color:#26384A;">{apt_n}</p>
            </div>
            """, unsafe_allow_html=True)

        _section_header(9, "Datos mínimos del software")
        with st.expander("Ver campos requeridos"):
            _h4("Paciente")
            for b in ["Nombre, especie, sexo, edad.",
                      "Peso actual (obligatorio para diseño de carga).",
                      "Raza o mestizo. BCS (1-9).",
                      "Nivel de actividad: sedentario / moderado / activo / deportivo."]:
                st.markdown(f"• {b}")
            _h4("Clínico")
            for b in ["Extremidad afectada y nivel de amputación (1-7).",
                      "Causa probable. Estado de cicatrización.",
                      "Veterinario responsable identificado."]:
                st.markdown(f"• {b}")
            _h4("Morfológico")
            for b in ["Longitud útil del muñón (con escala).",
                      "Circunferencia proximal y distal.",
                      "Forma: cilíndrica / cónica / bulbosa / irregular."]:
                st.markdown(f"• {b}")

        _section_header(8, "Protocolo fotográfico y escaneo 3D")
        with st.expander("Criterios de calidad"):
            _html_table(
                ["Parámetro", "Mínimo requerido", "Observaciones"],
                [
                    ["Cobertura del muñón", "4 ángulos ortogonales", "Gaps >10mm deben indicarse."],
                    ["Escala de referencia", "Marcador físico calibrado obligatorio", "Sin escala el diseño no es válido."],
                    ["Resolución", "<3mm entre puntos para socket", "Para suela se acepta resolución menor."],
                    ["Estabilidad", "Animal cooperativo o sedado leve", "El movimiento invalida el escaneo."],
                    ["Pelo", "Humedecido o aplastado con gel", "Zona rapada si pelo >1cm."],
                    ["Contralateral", "Recomendado si sano", "Referencia para longitud funcional objetivo."],
                ], col_widths=["22%","28%","50%"])

        _section_header(11, "Módulos de diseño externo")
        col_a, col_b = st.columns(2)
        with col_a:
            with st.expander("Socket (encaje)"):
                st.markdown(
                    "**Materiales:** Termoplástico, laminado de resina, impresión 3D "
                    "(PLA frágil → PETG → TPU/PA para mayor exigencia).\n\n"
                    "**Liner:** Silicona (mejor calidad), EVA (económico), gel (prominencias).\n\n"
                    "**Suspensión:** Correa/arnés, succión (muñón regular), auto-suspensión (desarticulaciones distales).\n\n"
                    "**Zonas de alivio:** olécranon, epicóndilos, cresta tibial, cabeza de fíbula, rótula.")
            with st.expander("Estructura principal"):
                st.markdown(
                    "Peso máximo orientativo: **2-3% del peso corporal**.\n\n"
                    "Socket y pie/terminal deben ser **reemplazables por separado**.")
        with col_b:
            with st.expander("Zona articular / flexible"):
                st.markdown(
                    "Transradial / transtibial: puede ser rígida.\n\n"
                    "Transhumeral / transfemoral: requiere articulación intermedia (codo o stifle).\n\n"
                    "Bisagra monoeje: simple y predecible. Elemento elástico: retorno de energía.")
            with st.expander("Pie protésico y suela"):
                st.markdown(
                    "Materiales: TPU flexible, silicona, caucho blando.\n\n"
                    "Suela: antideslizante, lavable y **reemplazable**.\n\n"
                    "Ángulo de quiebre: 45-55°, ajustable según marcha.")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 5 — ADAPTACIÓN PROGRESIVA
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[4]:

        _section_header(12, "Protocolo de adaptación progresiva")
        st.markdown(
            "La adaptación progresiva es **tan crítica como el diseño del socket**. "
            "Un encaje bien fabricado que se usa demasiado tiempo en las primeras semanas "
            "produce lesiones cutáneas y abandono de la prótesis."
        )

        _html_table(
            ["Período", "Uso diario", "Observaciones"],
            [
                ["Semana 1", "2-3 sesiones / 15-20 min supervisadas",
                 "Revisar piel tras cada sesión. Retirar ante cualquier cambio."],
                ["Semana 2", "3-4 sesiones / 20-30 min",
                 "Movimiento supervisado en plano. Tutor aprende señales de alarma."],
                ["Semanas 3-4", "1-2 h totales / 2-3 sesiones",
                 "Introducir superficies variadas. Monitoreo semanal."],
                ["Semanas 5-6", "Hasta 3 h/día", "Sin supervisión constante si no hay complicaciones."],
                ["Semanas 7-8", "Uso diario según tolerancia", "Tutor puede manejar independientemente."],
                ["Mes 3+", "Uso habitual", "Revisión trimestral o ante cambios de peso/actividad/irritación."],
            ], col_widths=["15%","30%","55%"])

        _alert(
            "Señales de alarma: retirar la prótesis de inmediato",
            ["Eritema que no desaparece en 20 min tras retirar el socket.",
             "Cualquier herida, ampolla, úlcera o excoriación.",
             "Aumento de cojera o apoyo peor que sin prótesis.",
             "Signos de dolor durante colocación, uso o retiro.",
             "Cambio de coloración, temperatura o inflamación del muñón.",
             "Olor inusual del socket o del muñón.",
             "El perro intenta quitarse la prótesis persistentemente."])

        _h4("Calendario de controles")
        for i, t in enumerate([
            "Día 7: primer control (crítico). Revisar piel, suspensión y socket.",
            "Día 14: segundo control. Confirmar progresión.",
            "Mes 1: evaluación completa con CBPI y ajustes de socket.",
            "Mes 3: reasignación de socket si hubo cambios de peso.",
            "Cada 6 meses: mantenimiento y revisión de componentes de desgaste."
        ], 1):
            st.markdown(f"{i}. {t}")

        _h4("Criterios de reemplazo del socket")
        for b in ["Cambio de peso ≥5% del peso corporal.",
                  "Más de 3 meses desde la amputación.",
                  "Lesiones cutáneas atribuibles al socket.",
                  "Cambio significativo del nivel de actividad.",
                  "Crecimiento del paciente."]:
            st.markdown(f"• {b}")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 6 — CHECKLISTS
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[5]:

        _section_header(13, "Checklist veterinario / cirujano")
        vet_items = [
            "¿Cuál es la causa de la amputación o pérdida de miembro?",
            "¿Existe sospecha oncológica? ¿Se requiere histopatología?",
            "¿Se requieren márgenes quirúrgicos amplios?",
            "¿Hay infección activa? ¿Cultivo y antibiograma realizados?",
            "¿La piel permite cierre sin tensión sobre el extremo óseo?",
            "¿Hay cobertura suficiente sobre prominencias óseas?",
            "¿El muñón toleraría contacto con un socket?",
            "¿Hay dolor neuropático, neuroma o hipersensibilidad focal?",
            "¿La articulación proximal preservada tiene rango funcional?",
            "¿La forma final permite suspensión y control rotacional?",
            "¿El paciente requiere rehabilitación previa al ajuste?",
            "¿El tutor puede cumplir el protocolo de adaptación y controles?",
            "¿Se evaluó el impacto a largo plazo en miembros contralaterales?",
        ]
        vet_checked = [st.checkbox(item, key=f"vet_{item[:30]}") for item in vet_items]
        vet_total = sum(vet_checked)
        st.progress(vet_total / len(vet_items))
        st.caption(f"{vet_total} / {len(vet_items)} ítems revisados")

        st.markdown("---")

        _section_header(14, "Checklist Ache / fabricación")
        fab_items = [
            "Medidas del muñón con escala confiable y validada.",
            "Fotos suficientes, bien orientadas y en condiciones aceptables.",
            "Peso actual confirmado (fecha de la medición).",
            "Extremidad y lado confirmados con el equipo clínico.",
            "Nivel de amputación registrado y confirmado.",
            "Estado clínico revisado y validado por veterinario.",
            "Alertas clínicas documentadas en el expediente.",
            "Socket conceptual revisado por profesional.",
            "Material definido según peso, actividad y presupuesto.",
            "Liner/interfaz definido según condición de piel.",
            "Sistema de suspensión definido según geometría del muñón.",
            "Suela y liner incluidos como componentes reemplazables.",
            "Plan de prueba progresiva comunicado al tutor por escrito.",
            "Protocolo de devolución o ajuste documentado.",
        ]
        fab_checked = [st.checkbox(item, key=f"fab_{item[:30]}") for item in fab_items]
        fab_total = sum(fab_checked)
        st.progress(fab_total / len(fab_items))
        st.caption(f"{fab_total} / {len(fab_items)} ítems completados")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 7 — REFERENCIA
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[6]:

        _section_header(15, "Límites del software")
        _alert(
            "El sistema Ache NO hace ni hará:",
            ["Diagnosticar enfermedades ni sospechar neoplasia.",
             "Decidir si se realiza una amputación.",
             "Definir el nivel quirúrgico exacto.",
             "Aprobar el uso clínico sin revisión profesional.",
             "Prometer marcha normal o recuperación total.",
             "Reemplazar radiografías, TC, examen físico ni criterio veterinario.",
             "Garantizar la seguridad de una prótesis sin seguimiento activo."],
            color=NAVY, bg="#EAF2FB")

        _section_header(17, "Glosario")
        for term, defn in {
            "BCS": "Body Condition Score (1-9). BCS 4-5: ideal; 1-3: delgadez; 8-9: obesidad.",
            "CBPI": "Canine Brief Pain Inventory. 11 ítems para dolor crónico.",
            "Control rotacional": "Capacidad del socket de resistir la rotación del muñón durante la marcha.",
            "Encaje / socket": "Componente que aloja el muñón. Su ajuste determina comodidad y función.",
            "ITAP": "Intraosseous Transcutaneous Amputation Prosthesis. Osseointegración.",
            "Liner / forro": "Capa suave (silicona, EVA, gel) entre muñón y socket.",
            "Longitud útil": "Porción del muñón usable para controlar la prótesis.",
            "Neuroma": "Crecimiento nervioso anormal en el extremo. Puede causar dolor severo al contacto.",
            "Palanca ósea": "Longitud del segmento residual. A mayor longitud, mejor control.",
            "Retorno elástico": "Capacidad del pie de almacenar y liberar energía durante el despegue.",
            "Suspensión": "Sistema que mantiene la prótesis: correa/arnés, succión, auto-suspensión.",
            "Transtibial": "Amputación debajo del stifle. Mejor escenario pelviano.",
            "Transradial": "Amputación debajo del codo. Mejor escenario torácico.",
            "Tutor": "Propietario/cuidador. Rol activo en adaptación e higiene.",
        }.items():
            st.markdown(f"**{term}:** {defn}")

        _section_header(18, "Bibliografía seleccionada")
        st.caption("Referencias verificadas en PubMed.")
        for num, authors, title, url in [
            ("1",  "AAHA.", "2022 AAHA Pain Management Guidelines.",
             "https://www.aaha.org/resources/2022-aaha-pain-management-guidelines-for-dogs-and-cats/"),
            ("2",  "WSAVA Global Pain Council.", "WSAVA Pain Guidelines.",
             "https://wsava.org/global-guidelines/pain-guidelines/"),
            ("3",  "Culp WT et al.", "Surgical approaches to canine appendicular osteosarcoma part 1. PMC12671202.",
             "https://pubmed.ncbi.nlm.nih.gov/41340931/"),
            ("4",  "Culp WT et al.", "Surgical approaches to canine appendicular osteosarcoma part 2. PMC12755153.",
             "https://pubmed.ncbi.nlm.nih.gov/41479421/"),
            ("7",  "Noronha de Souza MM et al.", "Impacts of exoprosthesis use in dogs: systematic review. PMC12631277.",
             "https://pubmed.ncbi.nlm.nih.gov/41280415/"),
            ("10", "Autor et al.", "Effects of a custom forelimb prosthesis on weight distribution. PMC13000723.",
             "https://pubmed.ncbi.nlm.nih.gov/41868109/"),
            ("12", "Autor et al.", "Clinical Application of 3D Printing in Canine Full Limb Prosthetics. PMC12767463.",
             "https://pubmed.ncbi.nlm.nih.gov/41497371/"),
        ]:
            st.markdown(f"**{num}.** {authors} *{title}* [{url}]({url})")

        st.markdown("---")
        st.markdown(
            "_Ache Innovation desarrolla herramientas de parametrización morfológica para asistir "
            "el diseño de prótesis externas veterinarias. **No reemplaza la evaluación clínica ni quirúrgica.**_"
        )
