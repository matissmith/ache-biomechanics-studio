"""
modules/guia_quirurgica.py
Guía Técnica Preliminar Ache Innovation v0.2
Evaluación de muñón protetizable en perros para prótesis externa personalizada.

Para integrar en app.py:
    from modules.guia_quirurgica import render_guia_quirurgica
    # En el bloque de routing:
    elif page == "guia_quirurgica":
        render_guia_quirurgica(caso_activo)  # pasar dict del caso si existe
"""

import streamlit as st


# ─── Paleta de colores consistente con la app ────────────────────────────────
NAVY  = "#173555"
BLUE  = "#245E96"
RED   = "#8B1E1E"
ORANGE = "#6B4700"
GREEN  = "#1F5F32"

# ─── Helpers de estilo ────────────────────────────────────────────────────────

def _card(content_fn, border_color=BLUE, bg="#F0F4FA"):
    """Renderiza contenido dentro de un card con borde izquierdo de color."""
    st.markdown(
        f"""<div style="border-left: 4px solid {border_color};
                        background: {bg};
                        padding: 12px 16px;
                        border-radius: 0 6px 6px 0;
                        margin: 6px 0;">""",
        unsafe_allow_html=True
    )
    content_fn()
    st.markdown("</div>", unsafe_allow_html=True)


def _alert(title, items, color=RED, bg="#FDF3F3"):
    html = f"""
    <div style="border-left:4px solid {color}; background:{bg};
                padding:10px 14px; border-radius:0 6px 6px 0; margin:8px 0;">
      <strong style="color:{color};">⚠  {title}</strong>
      <ul style="margin:6px 0 0 0; padding-left:18px; font-size:0.92em; color:#26384A !important;">
    """
    for item in items:
        html += f"<li>{item}</li>"
    html += "</ul></div>"
    st.markdown(html, unsafe_allow_html=True)


def _compat_box(letter, title, criteria, color, bg):
    html = f"""
    <div style="border-left:4px solid {color}; background:{bg};
                padding:10px 14px; border-radius:0 6px 6px 0; margin:6px 0;">
      <strong style="color:{color}; font-size:1.0em;">Nivel {letter} — {title}</strong>
      <ul style="margin:6px 0 0 0; padding-left:18px; font-size:0.90em; color:#26384A !important;">
    """
    for c in criteria:
        html += f"<li>{c}</li>"
    html += "</ul></div>"
    st.markdown(html, unsafe_allow_html=True)


def _section_header(num, title):
    st.markdown(
        f"""<h3 style="color:{NAVY}; border-bottom:2px solid {BLUE};
                        padding-bottom:4px; margin-top:20px;">
            {num}.  {title}
        </h3>""",
        unsafe_allow_html=True
    )


def _h4(title):
    st.markdown(
        f"<h4 style='color:{BLUE}; margin-top:14px; margin-bottom:4px;'>{title}</h4>",
        unsafe_allow_html=True
    )


# ─── TABLA HTML helper ────────────────────────────────────────────────────────

def _html_table(headers, rows, col_widths=None):
    """Genera una tabla HTML con estilo booktabs mínimo."""
    w = col_widths or ["auto"] * len(headers)
    style_tbl = (
        "border-collapse:collapse; width:100%; font-size:0.88em; margin:8px 0;"
    )
    style_th = (
        f"background:{NAVY}; color:white !important; padding:7px 10px; text-align:left;"
    )
    style_td_even = "padding:6px 10px; background:#F9FAFB; color:#26384A !important;"
    style_td_odd  = "padding:6px 10px; background:#FFFFFF; color:#26384A !important;"
    html = f"<table style='{style_tbl}'><thead><tr>"
    for i, h in enumerate(headers):
        ww = f"width:{w[i]};" if col_widths else ""
        html += f"<th style='{style_th}{ww}'>{h}</th>"
    html += "</tr></thead><tbody>"
    for ri, row in enumerate(rows):
        s = style_td_even if ri % 2 == 0 else style_td_odd
        html += "<tr>"
        for cell in row:
            # Allow tuples (text, color) for colored cells
            if isinstance(cell, tuple):
                txt, clr = cell
                html += f"<td style='{s} color:{clr}; font-weight:bold;'>{txt}</td>"
            else:
                html += f"<td style='{s}'>{cell}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FUNCIÓN PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def render_guia_quirurgica(caso_activo: dict = None):
    """
    Renderiza la Guía Técnica Ache Innovation v0.2.

    Parameters
    ----------
    caso_activo : dict, optional
        Datos del caso activo del session_state. Claves útiles:
        - nombre_paciente, especie, raza, peso_kg, edad
        - extremidad (e.g. "Torácica izquierda")
        - nivel_amputacion (int 1-7)
        - causa (e.g. "Traumático")
        - estado_muñon (e.g. "cicatrizado")
        - bcs (int 1-9)
    """

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="ache-guide-minihero" style="background:#FFFFFF !important; border:1px solid #C9D8E8 !important; border-left:5px solid #F2AA24 !important; border-radius:16px !important; padding:16px 18px !important; margin:0 0 16px 0 !important; box-shadow:0 10px 24px rgba(23,53,85,.06) !important;">
            <div class="ache-guide-kicker" style="color:#173555 !important; -webkit-text-fill-color:#173555 !important; font-weight:900 !important; font-size:1.12rem !important; line-height:1.25 !important;">🩺 Guía técnica preliminar · v0.2</div>
            <div class="ache-guide-subtitle" style="color:#5B6E82 !important; -webkit-text-fill-color:#5B6E82 !important; font-weight:650 !important; margin-top:5px !important;">Evaluación de muñón protetizable · Ache Innovation</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ── Banner caso activo ────────────────────────────────────────────────────
    if caso_activo:
        nombre = caso_activo.get("nombre_paciente", "—")
        extremidad = caso_activo.get("extremidad", "—")
        nivel = caso_activo.get("nivel_amputacion", "—")
        peso = caso_activo.get("peso_kg", "—")
        st.info(
            f"**Caso activo:** {nombre}  ·  Extremidad: {extremidad}  "
            f"·  Nivel de amputación: {nivel}  ·  Peso: {peso} kg"
        )
    else:
        st.caption("ℹ Sin caso activo. Los checklists y la clasificación funcionan igual.")

    st.markdown("---")

    # ── Aviso de uso ──────────────────────────────────────────────────────────
    with st.expander("📋  Uso previsto y límites de este documento", expanded=False):
        st.markdown(
            "_Documento de apoyo para Ache Innovation, veterinarios, cirujanos, "
            "rehabilitadores y fabricantes. No es una guía quirúrgica autónoma. "
            "No reemplaza evaluación clínica, radiográfica, oncológica, anestésica "
            "ni criterio del veterinario o cirujano responsable._"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Navegación por tabs ───────────────────────────────────────────────────
    tabs = st.tabs([
        "⚕️ Clínico",
        "📐 Biomecánica & Niveles",
        "📊 Clasificación",
        "🔩 Diseño protésico",
        "🗓 Adaptación",
        "✅ Checklists",
        "📚 Referencia"
    ])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — CLÍNICO
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[0]:

        _section_header(1, "Principio clínico central")
        st.markdown(
            "> *« Si el veterinario o cirujano considera clínicamente viable preservar "
            "un muñón, ¿qué condiciones morfológicas, funcionales y de tejidos debería "
            "tener ese muñón para ser compatible con una prótesis externa? »*"
        )
        st.markdown(
            "La decisión quirúrgica debe priorizar salud, analgesia, márgenes oncológicos "
            "cuando correspondan, control de infección, calidad de vida y rehabilitación. "
            "La compatibilidad protésica es un factor **adicional**, no el dominante."
        )

        _section_header(2, "Clasificación inicial del caso")
        tipo = st.selectbox(
            "Origen del caso",
            ["Traumático", "Congénito / malformativo", "Oncológico",
             "Infeccioso", "Neurológico / funcional",
             "Post-amputación previa", "Desconocido"],
            index=0
        )
        if tipo == "Oncológico":
            _alert(
                "Alerta crítica oncológica",
                [
                    "En casos tumorales la preservación del muñón puede estar contraindicada "
                    "si compromete márgenes quirúrgicos o control de la enfermedad.",
                    "Derivar inmediatamente a evaluación oncológica veterinaria.",
                    "La longitud del muñón en contexto oncológico es decisión exclusiva del equipo quirúrgico."
                ]
            )

        _section_header(4, "Condiciones mínimas para muñón protetizable")
        condiciones = [
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
        ]
        for c in condiciones:
            st.markdown(f"• {c}")

        _section_header(5, "Contraindicaciones y alertas de alto riesgo")
        _alert(
            "El software debe alertar y derivar ante cualquiera de las siguientes:",
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

        _section_header(7, "Evaluación funcional: escalas validadas")
        _h4("7.1  Escalas para dolor crónico")
        _html_table(
            ["Escala", "Ítems", "Puntaje", "Uso recomendado"],
            [
                ["CBPI — Canine Brief Pain Inventory", "11 (sev. ×4 + interf. ×7)",
                 "Sev: 0-40 / Int: 0-60", "Baseline, 4 sem, 3 m, 6 m. Validada para OA y dolor oncológico."],
                ["HCPI — Helsinki Chronic Pain Index", "11", "0-44",
                 "Monitoreo de adaptación protésica a largo plazo."],
            ],
            col_widths=["25%", "22%", "18%", "35%"]
        )
        _h4("7.2  Dolor agudo / post-operatorio")
        _html_table(
            ["Escala", "Ítems", "Puntaje", "Uso recomendado"],
            [
                ["CMPS-SF (Glasgow Short Form)", "6 categorías",
                 "0-24 (umbral: >5)", "Post-op y evaluación del muñón previo al ajuste."],
            ],
            col_widths=["28%", "18%", "18%", "36%"]
        )
        _h4("7.3  Protocolo de evaluación mínima")
        for i, t in enumerate([
            "Baseline pre-protésico: CBPI + CMPS-SF + scoring observacional.",
            "4 semanas post-ajuste: CBPI + scoring observacional.",
            "3 meses: CBPI + HCPI + scoring + revisión de socket.",
            "6 meses y anuales: batería completa."
        ], 1):
            st.markdown(f"{i}. {t}")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — BIOMECÁNICA & NIVELES
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[1]:

        _section_header(3, "Niveles de amputación y sus implicaciones protésicas")

        member = st.radio(
            "Miembro a consultar",
            ["Torácico (anterior)", "Pelviano (posterior)"],
            horizontal=True
        )

        if "Torácico" in member:
            _html_table(
                ["Niv.", "Nombre", "Descripción", "Palanca", "Aptitud", "Observaciones"],
                [
                    ["1", "Cuarto anterior", "Escápula + húmero completos", "Ninguna",
                     ("No recomendada", RED), "Sin muñón aprovechable."],
                    ["2", "Desart. del hombro", "Húmero completo retirado", "Mínima",
                     ("Muy difícil", RED), "Encaje extremadamente complejo."],
                    ["3", "Transhumeral proximal", ">50% del húmero retirado", "Corta",
                     ("Factible *", ORANGE), "Requiere codo protésico."],
                    ["4", "Transhumeral medio/distal", "<50% del húmero retirado", "Moderada",
                     ("Factible", ORANGE), "Mejor palanca; codo protésico necesario."],
                    ["5", "Desart. del codo", "Húmero completo preservado", "Buena",
                     ("Buena", GREEN), "Suspensión estable; codo externo requerido."],
                    ["6", "Transradial (antebrazo)", "Radio/cúbito parcial o completo", "Óptima",
                     ("Óptima ✓", GREEN), "Mejor escenario; codo preservado."],
                    ["7", "Desart. carpo / parcial", "Carpo, metacarpo o dedos", "Completa",
                     ("Excelente ✓", GREEN), "Casos más simples; bota o pie parcial."],
                ],
                col_widths=["4%", "17%", "22%", "9%", "13%", "35%"]
            )
        else:
            _html_table(
                ["Niv.", "Nombre", "Descripción", "Palanca", "Aptitud", "Observaciones"],
                [
                    ["1", "Hemipelvectomía", "Pelvis + fémur retirados", "Ninguna",
                     ("No recomendada", RED), "Sin muñón."],
                    ["2", "Desart. de cadera", "Fémur completo retirado", "Mínima",
                     ("Muy difícil", RED), "Sin palanca ósea."],
                    ["3", "Transfemoral proximal", ">50% del fémur retirado", "Corta",
                     ("Factible *", ORANGE), "Requiere rodilla protésica (stifle)."],
                    ["4", "Transfemoral medio/distal", "<50% del fémur retirado", "Moderada",
                     ("Factible", ORANGE), "Rodilla protésica; mejor control."],
                    ["5", "Desart. del stifle", "Fémur completo preservado", "Buena",
                     ("Buena", GREEN), "Palanca excelente; stifle externo requerido."],
                    ["6", "Transtibial", "Tibia/fíbula parcial o completa", "Óptima",
                     ("Óptima ✓", GREEN), "Mejor escenario; stifle preservado = propulsión."],
                    ["7", "Desart. tarso / parcial", "Tarso, metatarso o dedos", "Completa",
                     ("Excelente ✓", GREEN), "Casos más simples; bota o pie parcial."],
                ],
                col_widths=["4%", "17%", "22%", "9%", "13%", "35%"]
            )

        st.caption(
            "* Factible con restricciones — requiere evaluación avanzada. "
            "Niveles 1-2: no recomendados para prótesis externas convencionales."
        )

        _section_header(6, "Biomecánica por extremidad y nivel")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Miembro torácico**")
            st.markdown(
                "Soporta ~60% del peso corporal. Una prótesis anterior bien ajustada "
                "redistribuye el 21% del peso corporal hacia la prótesis, reduciendo "
                "la carga sobre el contralateral del 49% al 35% _(Ref. 10)_."
            )
            st.markdown(
                "**Prioridades:** superficie de apoyo amplia, amortiguación, "
                "control medio-lateral, prevención de rotación del socket."
            )
        with col2:
            st.markdown(f"**Miembro pelviano**")
            st.markdown(
                "Principal generador de propulsión. La preservación del stifle es "
                "el factor más determinante en el diseño."
            )
            st.markdown(
                "**Prioridades:** retorno elástico, longitud funcional correcta, "
                "alineación cadera-stifle-tarso, tope de hiperextensión."
            )

        _alert(
            "Compensación en miembros remanentes",
            ["El riesgo de osteoartritis acelerada y lesiones tendinosas en los miembros "
             "sanos es real tras cualquier amputación.",
             "La prótesis no solo restaura movilidad: reduce la sobrecarga compensatoria "
             "a largo plazo. Incluir este argumento en el reporte para el tutor."],
            color=ORANGE,
            bg="#FDF8EE"
        )

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — CLASIFICACIÓN A/B/C/D
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[2]:

        _section_header(10, "Clasificación de compatibilidad protésica")
        st.markdown(
            "El sistema clasifica cada caso en uno de cuatro niveles. "
            "La clasificación debe ser **automática** y mostrar qué criterios "
            "activaron cada nivel."
        )

        # Evaluación rápida interactiva
        st.markdown("---")
        st.markdown("#### Evaluación rápida del caso actual")

        c1, c2 = st.columns(2)
        with c1:
            tumor = st.checkbox("Sospecha oncológica", value=False)
            infeccion = st.checkbox("Infección activa", value=False)
            herida = st.checkbox("Herida abierta / piel inestable", value=False)
            dolor_severo = st.checkbox("Dolor severo no controlado", value=False)
        with c2:
            longitud_corta = st.checkbox("Muñón <30% del segmento óseo", value=False)
            sin_cobertura = st.checkbox("Prominencias óseas sin cobertura", value=False)
            bcs_alto = st.checkbox("BCS 8-9 (obesidad severa)", value=False)
            sin_vet = st.checkbox("Sin veterinario responsable", value=False)

        c3, c4 = st.columns(2)
        with c3:
            longitud_borderline = st.checkbox("Muñón 30-40% del segmento (borderline)", value=False)
            cicatrizacion = st.checkbox("Cicatrización incompleta (<8 sem)", value=False)
            bcs_7 = st.checkbox("BCS 7 (sobrepeso leve)", value=False)
        with c4:
            sin_escala = st.checkbox("Sin escala de referencia en fotos", value=False)
            sin_medidas = st.checkbox("Sin medidas del muñón", value=False)
            info_incompleta = st.checkbox("Información clínica incompleta", value=False)

        # Lógica de clasificación
        alertas_c = [tumor, infeccion, herida, dolor_severo,
                     longitud_corta, sin_cobertura, bcs_alto, sin_vet]
        alertas_b = [longitud_borderline, cicatrizacion, bcs_7, sin_escala]
        alertas_d = [sin_medidas, info_incompleta]

        st.markdown("---")
        if any(alertas_c):
            _compat_box("C", "No recomendado sin evaluación avanzada",
                ["Uno o más criterios de alto riesgo están presentes.",
                 "Derivar a evaluación veterinaria antes de continuar con el diseño."],
                RED, "#FDF3F3")
        elif any(alertas_d):
            _compat_box("D", "Información insuficiente para clasificar",
                ["Faltan datos clínicos o morfológicos críticos.",
                 "El sistema debe solicitar los datos faltantes antes de continuar."],
                "#777777", "#F5F5F5")
        elif any(alertas_b):
            _compat_box("B", "Compatible con advertencias",
                ["El caso es potencialmente viable pero hay factores a resolver.",
                 "Revisar los ítems marcados antes del ajuste."],
                ORANGE, "#FDF8EE")
        else:
            _compat_box("A", "Potencialmente compatible",
                ["Sin alertas mayores visibles.",
                 "Continuar con el flujo de diseño."],
                GREEN, "#F0F7F0")

        st.markdown("---")
        st.markdown("#### Criterios completos por nivel")
        with st.expander("Ver criterios completos A / B / C / D"):
            _compat_box("A", "Potencialmente compatible",
                ["Sin sospecha oncológica.", "Sin infección activa, herida ni necrosis.",
                 "Dolor controlado.", "Longitud ≥30% del segmento.", "Piel cicatrizada o estable.",
                 "BCS 4-6/9.", "Veterinario responsable identificado.",
                 "Información completa. Fotos con escala válida.", "Tutor comprometido."],
                GREEN, "#F0F7F0")
            _compat_box("B", "Compatible con advertencias",
                ["Longitud 30-40% (borderline).", "Irregularidades menores de piel.",
                 "Cicatrización incompleta (<8 sem post-amputación).", "BCS 7/9.",
                 "Contractura articular leve.", "Forma subóptima del muñón.",
                 "Escala ausente en fotos.", "Información parcialmente completa."],
                ORANGE, "#FDF8EE")
            _compat_box("C", "No recomendado sin evaluación avanzada",
                ["Neoplasia activa.", "Infección activa.", "Piel deficiente o úlcera.",
                 "Herida abierta.", "Dolor severo.", "Longitud <30% o sin longitud aprovechable.",
                 "Prominencias sin cobertura.", "Neuroma severo.", "Contractura severa.",
                 "BCS 8-9.", "Sin veterinario o seguimiento."],
                RED, "#FDF3F3")
            _compat_box("D", "Información insuficiente",
                ["Fotos no permiten evaluación.", "Sin medidas del muñón.",
                 "Datos ausentes o contradictorios.",
                 "Imposible descartar oncología."],
                "#777777", "#F5F5F5")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — DISEÑO PROTÉSICO
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[3]:

        _section_header(9, "Datos mínimos del software")
        with st.expander("Ver campos requeridos por módulo"):
            _h4("Paciente")
            for b in ["Nombre, especie, sexo, edad.",
                      "Peso actual (obligatorio para diseño de carga).",
                      "Raza o mestizo. Condición corporal (BCS 1-9).",
                      "Nivel de actividad: sedentario / moderado / activo / deportivo.",
                      "Patologías conocidas."]:
                st.markdown(f"• {b}")
            _h4("Clínico")
            for b in ["Extremidad afectada y nivel de amputación (ver Sección 3).",
                      "Causa probable. Estado de cicatrización.",
                      "Dolor observado (0-10). Heridas / infección / necrosis.",
                      "Veterinario responsable identificado."]:
                st.markdown(f"• {b}")
            _h4("Morfológico")
            for b in ["Longitud útil del muñón (con escala).",
                      "Circunferencia proximal y distal.",
                      "Forma: cilíndrica / cónica / bulbosa / irregular.",
                      "Prominencias óseas. Estado de piel. Capacidad de carga.",
                      "Rango articular remanente."]:
                st.markdown(f"• {b}")

        _section_header(8, "Escaneo 3D y protocolo fotográfico")
        with st.expander("Criterios de calidad del escaneo"):
            _html_table(
                ["Parámetro", "Mínimo requerido", "Observaciones"],
                [
                    ["Cobertura del muñón", "4 ángulos ortogonales", "Gaps >10mm deben indicarse."],
                    ["Escala de referencia", "Marcador físico calibrado obligatorio",
                     "Sin escala el diseño no es válido. Bloquear el flujo."],
                    ["Resolución", "<3mm entre puntos para socket", "Para suela se acepta resolución menor."],
                    ["Estabilidad", "Animal cooperativo o sedado leve", "El movimiento invalida el escaneo."],
                    ["Pelo", "Humedecido o aplastado con gel", "Zona rapada si pelo >1cm."],
                    ["Formato", "STL u OBJ con escala", "Incluir metadatos de captura."],
                    ["Contralateral", "Recomendado si sano", "Referencia para longitud funcional objetivo."],
                ],
                col_widths=["22%", "28%", "50%"]
            )

        _section_header(11, "Módulos de diseño protésico externo")
        col_a, col_b = st.columns(2)
        with col_a:
            with st.expander("Socket (encaje)"):
                st.markdown(
                    "**Materiales:** Termoplástico (primera opción), laminado de resina, "
                    "impresión 3D (PLA frágil → PETG → TPU/PA para mayor exigencia).\n\n"
                    "**Liner:** Silicona (mejor calidad), EVA (económico), gel (prominencias).\n\n"
                    "**Suspensión:** Correa/arnés (primera opción), succión (muñón regular), "
                    "auto-suspensión anatómica (desarticulaciones distales).\n\n"
                    "**Zonas de alivio obligatorias:** olécranon, epicóndilos, cresta tibial, "
                    "cabeza de fíbula, rótula si presente."
                )
            with st.expander("Estructura principal"):
                st.markdown(
                    "Peso máximo orientativo: **2-3% del peso corporal**.\n\n"
                    "Materiales: aluminio (híbridas), PLA/PETG/PA (impresas), "
                    "compuestos para pacientes grandes o muy activos.\n\n"
                    "Socket y pie/terminal deben ser **reemplazables por separado**."
                )
        with col_b:
            with st.expander("Zona articular / flexible"):
                st.markdown(
                    "Transradial / transtibial: puede ser rígida si la articulación proximal es funcional.\n\n"
                    "Transhumeral / transfemoral: requiere articulación intermedia (codo o stifle).\n\n"
                    "Bisagra monoeje: simple y predecible. "
                    "Elemento elástico (carbono, resorte): retorno de energía."
                )
            with st.expander("Pie protésico y suela"):
                st.markdown(
                    "Diseño basado en el patrón de contacto natural.\n\n"
                    "Materiales: TPU flexible, silicona, caucho blando.\n\n"
                    "Suela: antideslizante, lavable y **reemplazable** (mayor desgaste).\n\n"
                    "Ángulo de quiebre: 45-55°, ajustable según marcha."
                )

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 5 — ADAPTACIÓN PROGRESIVA
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[4]:

        _section_header(12, "Protocolo de adaptación progresiva y seguimiento")
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
                ["Semanas 3-4", "1-2 h totales en 2-3 sesiones",
                 "Introducir superficies variadas. Monitoreo semanal por veterinario."],
                ["Semanas 5-6", "Hasta 3 h/día", "Sin supervisión constante si no hay complicaciones."],
                ["Semanas 7-8", "Uso diario según tolerancia",
                 "Tutor puede manejar independientemente si fue capacitado."],
                ["Mes 3+", "Uso habitual",
                 "Revisión trimestral o ante cambios de peso/actividad/irritación."],
            ],
            col_widths=["15%", "30%", "55%"]
        )

        _alert(
            "Señales de alarma: retirar la prótesis de inmediato",
            ["Eritema que no desaparece en 20 min tras retirar el socket.",
             "Cualquier herida, ampolla, úlcera o excoriación.",
             "Aumento de cojera o apoyo peor que sin prótesis.",
             "Signos de dolor durante colocación, uso o retiro.",
             "Cambio de coloración, temperatura o inflamación del muñón.",
             "Olor inusual del socket o del muñón.",
             "El perro intenta quitarse la prótesis persistentemente."]
        )

        _h4("Calendario de controles")
        for i, t in enumerate([
            "Día 7 post-ajuste: primer control (crítico). Revisar piel, suspensión y socket.",
            "Día 14: segundo control. Confirmar progresión del protocolo.",
            "Mes 1: evaluación completa con CBPI y ajustes de socket.",
            "Mes 3: reasignación de socket si hubo cambios de peso o maduración.",
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
    # TAB 6 — CHECKLISTS INTERACTIVOS
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
            "¿El paciente requiere rehabilitación física previa al ajuste?",
            "¿El tutor puede cumplir el protocolo de adaptación y controles?",
            "¿Se evaluó el impacto a largo plazo en los miembros contralaterales?",
        ]
        vet_checked = []
        for item in vet_items:
            checked = st.checkbox(item, key=f"vet_{item[:30]}")
            vet_checked.append(checked)

        vet_total = sum(vet_checked)
        st.progress(vet_total / len(vet_items))
        st.caption(f"{vet_total} / {len(vet_items)} ítems revisados")

        st.markdown("---")

        _section_header(14, "Checklist Ache / fabricación")
        fab_items = [
            "Medidas del muñón con escala confiable y validada.",
            "Escaneo 3D con cobertura suficiente y marcadores de calibración.",
            "Fotos suficientes, bien orientadas y en condiciones aceptables.",
            "Peso actual confirmado (fecha de la medición).",
            "Extremidad y lado confirmados con el equipo clínico.",
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
        fab_checked = []
        for item in fab_items:
            checked = st.checkbox(item, key=f"fab_{item[:30]}")
            fab_checked.append(checked)

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
            color=NAVY,
            bg="#EAF2FB"
        )

        _section_header(17, "Glosario de términos clave")
        glosario = {
            "BCS": "Body Condition Score (1-9). BCS 4-5: ideal; 1-3: delgadez; 8-9: obesidad.",
            "CBPI": "Canine Brief Pain Inventory. Cuestionario tutor de 11 ítems para dolor crónico.",
            "Control rotacional": "Capacidad del socket de resistir la rotación del muñón durante la marcha.",
            "Encaje / socket": "Componente que aloja el muñón. Su ajuste determina comodidad y función.",
            "ITAP": "Intraosseous Transcutaneous Amputation Prosthesis. Osseointegración — diferente al socket externo.",
            "Liner / forro": "Capa suave (silicona, EVA, gel) entre el muñón y el socket.",
            "Longitud útil": "Porción del muñón usable para controlar la prótesis.",
            "Neuroma": "Crecimiento anormal nervioso en el extremo seccionado. Puede causar dolor severo al contacto.",
            "Palanca ósea": "Longitud del segmento óseo residual. A mayor longitud, mejor control.",
            "Retorno elástico": "Capacidad del pie de almacenar y liberar energía durante el despegue.",
            "Suspensión": "Sistema que mantiene la prótesis adherida: correa/arnés, succión, auto-suspensión.",
            "Transtibial": "Amputación debajo del stifle (rodilla canina). Mejor escenario pelviano.",
            "Transradial": "Amputación debajo del codo. Mejor escenario torácico.",
            "Tutor": "Propietario/cuidador responsable. Rol activo en adaptación e higiene.",
        }
        for term, defn in glosario.items():
            st.markdown(f"**{term}:** {defn}")

        _section_header(18, "Bibliografía seleccionada")
        st.caption("Referencias verificadas en PubMed. ⚠ = PMID pendiente de verificar.")
        refs = [
            ("1", "AAHA.", "2022 AAHA Pain Management Guidelines for Dogs and Cats.",
             "https://www.aaha.org/resources/2022-aaha-pain-management-guidelines-for-dogs-and-cats/"),
            ("2", "WSAVA Global Pain Council.", "WSAVA Pain Guidelines.",
             "https://wsava.org/global-guidelines/pain-guidelines/"),
            ("3", "Culp WT et al.", "Surgical approaches to canine appendicular osteosarcoma part 1. PMC12671202.",
             "https://pubmed.ncbi.nlm.nih.gov/41340931/"),
            ("4", "Culp WT et al.", "Surgical approaches to canine appendicular osteosarcoma part 2. PMC12755153.",
             "https://pubmed.ncbi.nlm.nih.gov/41479421/"),
            ("7", "Noronha de Souza MM et al.",
             "Impacts of exoprosthesis use in dogs with partial amputation: systematic review. PMC12631277.",
             "https://pubmed.ncbi.nlm.nih.gov/41280415/"),
            ("10", "Autor et al.",
             "Effects of a custom forelimb prosthesis on weight distribution and gait. PMC13000723.",
             "https://pubmed.ncbi.nlm.nih.gov/41868109/"),
            ("12", "Autor et al.",
             "Clinical Application of 3D Printing in Canine Full Limb Prosthetics. PMC12767463.",
             "https://pubmed.ncbi.nlm.nih.gov/41497371/"),
        ]
        for num, authors, title, url in refs:
            st.markdown(f"**{num}.** {authors} *{title}* [{url}]({url})")

        st.markdown("---")
        st.markdown(
            "_Ache Innovation desarrolla herramientas de parametrización morfológica para asistir "
            "el diseño de prótesis externas veterinarias. El sistema organiza información anatómica, "
            "biomecánica y protésica para facilitar la comunicación entre veterinario, cirujano, "
            "rehabilitador, fabricante y tutor. **No reemplaza la evaluación clínica ni quirúrgica.**_"
        )
