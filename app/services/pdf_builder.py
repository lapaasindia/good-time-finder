"""
PDF report builder.
"""
from __future__ import annotations

import io
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


FONT_CANDIDATES = [
    Path(__file__).parent.parent / "fonts" / "NotoSansDevanagari-Regular.ttf",
    Path("/System/Library/Fonts/Supplemental/Noto Sans Devanagari.ttf"),
]


def _register_optional_hindi_font() -> str | None:
    for path in FONT_CANDIDATES:
        if not path.exists():
            continue
        try:
            pdfmetrics.registerFont(TTFont("NotoHindi", str(path)))
            pdfmetrics.registerFontFamily("NotoHindi", normal="NotoHindi")
            return "NotoHindi"
        except Exception:
            continue
    return None


HINDI_FONT = _register_optional_hindi_font()


def _draw_page_chrome(canvas, doc) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d8dee9"))
    canvas.setLineWidth(1)
    canvas.line(doc.leftMargin, doc.pagesize[1] - 36, doc.pagesize[0] - doc.rightMargin, doc.pagesize[1] - 36)
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 24, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()


def _safe(text: object) -> str:
    if text is None:
        return ""
    return escape(str(text))


def _chip(text: str, bg: str, fg: str = "#111827") -> Table:
    cell = Paragraph(
        f'<font color="{fg}"><b>{_safe(text)}</b></font>',
        ParagraphStyle(
            "ChipText",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=10,
            alignment=1,
        ),
    )
    table = Table([[cell]], colWidths=[1.35 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg)),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor(bg)),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def _bullet_lines(items: list[str], style: ParagraphStyle) -> list[Paragraph]:
    if not items:
        return [Paragraph("None highlighted.", style)]
    return [Paragraph(f"- {_safe(item)}", style) for item in items]


def _stat_grid(stats: list[tuple[str, str]], label_style: ParagraphStyle, value_style: ParagraphStyle) -> Table:
    cells = []
    for label, value in stats:
        cells.append(
            Paragraph(
                f'<font color="#6b7280">{_safe(label)}</font><br/><font color="#111827"><b>{_safe(value)}</b></font>',
                value_style,
            )
        )
    rows = [cells[i : i + 2] for i in range(0, len(cells), 2)]
    if rows and len(rows[-1]) == 1:
        rows[-1].append(Paragraph("", label_style))
    table = Table(rows, colWidths=[3.0 * inch, 3.0 * inch], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#e5e7eb")),
                ("INNERGRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#e5e7eb")),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return table


def build_pdf_report(report_data: dict) -> bytes:
    """Build a polished PDF report in memory."""
    buffer = io.BytesIO()
    doc = BaseDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=42,
        rightMargin=42,
        topMargin=48,
        bottomMargin=42,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="report", frames=[frame], onPage=_draw_page_chrome)])

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["BodyText"],
        fontName=HINDI_FONT or "Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#334155"),
        spaceAfter=12,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=10,
        spaceBefore=8,
    )
    card_title_style = ParagraphStyle(
        "CardTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1d4ed8"),
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.2,
        leading=14.5,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=6,
    )
    muted_style = ParagraphStyle(
        "Muted",
        parent=body_style,
        fontSize=9.2,
        leading=13,
        textColor=colors.HexColor("#6b7280"),
    )
    small_style = ParagraphStyle(
        "Small",
        parent=body_style,
        fontSize=8.8,
        leading=12,
        textColor=colors.HexColor("#374151"),
        spaceAfter=4,
    )
    value_style = ParagraphStyle(
        "Value",
        parent=body_style,
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#111827"),
    )

    story = []
    personal = report_data.get("personal_info", {})
    summary = report_data.get("executive_summary", {})
    reader_guide = report_data.get("reader_guide", {})
    chart_basics = report_data.get("chart_basics", {})
    chart_signature = report_data.get("chart_signature", {})
    timing = report_data.get("timing_overview", {})
    current_dasha = report_data.get("current_dasha", {})
    sade_sati = report_data.get("sade_sati", {})
    action_plan = report_data.get("action_plan", {})

    story.append(Paragraph("Comprehensive Astrology Report", title_style))
    if HINDI_FONT:
        story.append(Paragraph("Samagra Jyotish Report", subtitle_style))
    story.append(
        Paragraph(
            f'<font color="#6b7280">{_safe(personal.get("name", "Native"))}</font><br/>'
            f'<font color="#111827"><b>{_safe(summary.get("headline", ""))}</b></font>',
            body_style,
        )
    )
    story.append(Spacer(1, 10))

    hero_stats = [
        ("Birth Details", f'{personal.get("dob", "N/A")} | {personal.get("timezone", "N/A")}'),
        ("Core Placements", f'{personal.get("lagna", "N/A")} Lagna | {personal.get("moon_sign", "N/A")} Moon'),
        ("Nakshatra", personal.get("nakshatra", "N/A")),
        ("Current Cycle", current_dasha.get("summary", timing.get("current_cycle", "N/A"))),
        (
            "Sade Sati",
            sade_sati.get("summary", "N/A"),
        ),
        ("Coordinates", personal.get("place", "N/A")),
    ]
    story.append(_stat_grid(hero_stats, muted_style, value_style))
    story.append(Spacer(1, 14))

    overview_box = Table(
        [[Paragraph(_safe(summary.get("overview", "")), body_style)]],
        colWidths=[doc.width],
        hAlign="LEFT",
    )
    overview_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eef6ff")),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#bfdbfe")),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    story.append(overview_box)
    story.append(Spacer(1, 18))

    if reader_guide:
        story.append(Paragraph("How To Read This Report", section_style))
        story.append(Paragraph(_safe(reader_guide.get("overview", "")), body_style))
        story.append(Paragraph("Quick guide", card_title_style))
        story.extend(_bullet_lines(reader_guide.get("how_to_use", []), body_style))
        terms = [
            f"{item.get('term')}: {item.get('meaning')}"
            for item in reader_guide.get("terms", [])
        ]
        if terms:
            story.append(Paragraph("Plain-English glossary", card_title_style))
            story.extend(_bullet_lines(terms[:6], small_style))
        story.append(Spacer(1, 10))

    if chart_basics:
        story.append(Paragraph("Your Chart In Plain English", section_style))
        story.append(Paragraph(_safe(chart_basics.get("plain_english", "")), body_style))
        story.append(
            Paragraph(
                f"<b>Identity:</b> {_safe(chart_basics.get('identity', ''))}",
                body_style,
            )
        )
        story.append(
            Paragraph(
                f"<b>Work style:</b> {_safe(chart_basics.get('work_style', ''))}",
                body_style,
            )
        )
        story.append(
            Paragraph(
                f"<b>Relationships:</b> {_safe(chart_basics.get('relationships', ''))}",
                body_style,
            )
        )
        story.append(
            Paragraph(
                f"<b>Well-being:</b> {_safe(chart_basics.get('wellbeing', ''))}",
                body_style,
            )
        )
        story.append(Spacer(1, 10))

    story.append(Paragraph("Executive Summary", section_style))
    story.append(Paragraph("Strengths", card_title_style))
    story.extend(_bullet_lines(summary.get("strengths", []), body_style))
    story.append(Paragraph("Cautions", card_title_style))
    story.extend(_bullet_lines(summary.get("cautions", []), body_style))
    story.append(Paragraph("Timing Highlights", card_title_style))
    story.extend(_bullet_lines(summary.get("timing_highlights", []), body_style))
    story.append(Spacer(1, 10))

    dominant = chart_signature.get("dominant_planets", [])
    sensitive = chart_signature.get("sensitive_planets", [])
    if dominant or sensitive:
        story.append(Paragraph("Chart Signature", section_style))
        signature_rows = [["Dominant planets", "Sensitive planets"]]
        signature_rows.append(
            [
                "<br/>".join(
                    f"{_safe(item['planet'])} - {_safe(item['band'])} ({item['strength']:.2f})"
                    for item in dominant
                )
                or "None highlighted.",
                "<br/>".join(
                    f"{_safe(item['planet'])} - {_safe(item['band'])} ({item['strength']:.2f})"
                    for item in sensitive
                )
                or "None highlighted.",
            ]
        )
        signature_table = Table(
            [
                [
                    Paragraph("<b>Dominant planets</b>", body_style),
                    Paragraph("<b>Sensitive planets</b>", body_style),
                ],
                [
                    Paragraph(signature_rows[1][0], small_style),
                    Paragraph(signature_rows[1][1], small_style),
                ],
            ],
            colWidths=[3.0 * inch, 3.0 * inch],
            hAlign="LEFT",
        )
        signature_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#e5e7eb")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#e5e7eb")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(signature_table)
        story.append(Spacer(1, 14))

    story.append(Paragraph("Life Domain Synthesis", section_style))
    for syn in report_data.get("synthesis", []):
        badge_color = {
            "Exceptional": "#bbf7d0",
            "Strong": "#dbeafe",
            "Moderate": "#fde68a",
            "Strained": "#fed7aa",
            "Challenging": "#fecaca",
        }.get(syn.get("score_band"), "#e5e7eb")
        domain_header = Table(
            [
                [
                    Paragraph(f"<b>{_safe(syn.get('domain_en'))}</b>", body_style),
                    _chip(f"{syn.get('score_band')} | {syn.get('score')}", badge_color),
                ]
            ],
            colWidths=[4.6 * inch, 1.4 * inch],
            hAlign="LEFT",
        )
        domain_header.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ffffff")),
                    ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#dbe3ef")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        story.append(domain_header)
        story.append(Paragraph(_safe(syn.get("summary_en", "")), body_style))
        if syn.get("plain_english"):
            story.append(Paragraph(_safe(syn.get("plain_english", "")), small_style))
            
        # Draw 12 month timeline if available
        timeline = syn.get("timeline", [])
        if timeline:
            tl_cells = []
            for m in timeline:
                c_color = {
                    "Exceptional": "#22c55e",
                    "Strong": "#3b82f6",
                    "Moderate": "#eab308",
                    "Strained": "#f97316",
                    "Challenging": "#ef4444"
                }.get(m.get("band"), "#9ca3af")
                # Just month prefix (e.g. Jan)
                m_label = m.get("month", "")[:3]
                
                # A mini colored box for each month
                from reportlab.platypus import KeepInFrame
                cell_p = Paragraph(f'<font color="white" size="6"><b>{m_label}</b></font>', styles["Normal"])
                tl_cells.append(cell_p)
                
            if tl_cells:
                tl_table = Table([tl_cells], colWidths=[0.45 * inch] * len(tl_cells), hAlign="LEFT")
                # Create styles mapping for the background colors
                style_commands = [
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#ffffff")),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
                for i, m in enumerate(timeline):
                    c_color = {
                        "Exceptional": "#22c55e",
                        "Strong": "#3b82f6",
                        "Moderate": "#eab308",
                        "Strained": "#f97316",
                        "Challenging": "#ef4444"
                    }.get(m.get("band"), "#9ca3af")
                    style_commands.append(("BACKGROUND", (i, 0), (i, 0), colors.HexColor(c_color)))
                    
                tl_table.setStyle(TableStyle(style_commands))
                story.append(Spacer(1, 4))
                story.append(Paragraph("<b>12-Month Outlook:</b>", small_style))
                story.append(tl_table)
                story.append(Spacer(1, 4))
        
        focus_now = syn.get("focus_now", [])
        info_line = []
        if syn.get("confidence"):
            info_line.append(f"Confidence: {syn.get('confidence')}")
        if focus_now:
            info_line.append(f"Focus now: {', '.join(focus_now[:2])}")
        if info_line:
            story.append(Paragraph(_safe(" | ".join(info_line)), muted_style))
            
        story.append(Paragraph("<b>Why this score:</b>", small_style))
        story.extend(_bullet_lines(syn.get("key_factors_en", [])[:4], small_style))
        story.append(Spacer(1, 8))

    story.append(PageBreak())
    story.append(Paragraph("Planet Snapshot", section_style))
    planet_rows = [["Planet", "Placement", "Strength", "Notes"]]
    for planet in report_data.get("planetary_positions", []):
        flags = ", ".join(planet.get("flags", [])) or "None"
        placement = f"{planet.get('sign')} | House {planet.get('house')}"
        strength = f"{planet.get('strength_band')} ({planet.get('strength')})"
        note = f"Avastha: {planet.get('avastha_en') or 'N/A'} | Flags: {flags}"
        planet_rows.append([planet.get("planet"), placement, strength, note])
    planet_table = Table(
        planet_rows,
        colWidths=[0.9 * inch, 1.65 * inch, 1.25 * inch, 2.2 * inch],
        repeatRows=1,
        hAlign="LEFT",
    )
    planet_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#d1d5db")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("LEADING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(planet_table)
    story.append(Spacer(1, 10))
    for planet in report_data.get("planetary_positions", [])[:7]:
        story.append(Paragraph(f"<b>{_safe(planet.get('planet'))}</b>", card_title_style))
        story.append(Paragraph(_safe(planet.get("interpretation_en", "")), body_style))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Houses At A Glance", section_style))
    house_rows = [["House", "Occupants", "Interpretation"]]
    for house in report_data.get("houses_info", []):
        occupants = ", ".join(house.get("occupants", [])) or "None"
        house_rows.append([f"{house.get('house')}", occupants, house.get("interpretation_en", "")])
    house_table = Table(
        house_rows,
        colWidths=[0.5 * inch, 1.35 * inch, 4.15 * inch],
        repeatRows=1,
        hAlign="LEFT",
    )
    house_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eff6ff")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#dbeafe")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LEADING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(house_table)

    story.append(PageBreak())
    story.append(Paragraph("Yogas And Conditions", section_style))
    story.append(Paragraph("Strong yogas", card_title_style))
    story.extend(
        _bullet_lines(
            [
                f"{item.get('name')} ({item.get('score')}): {item.get('description')}"
                for item in report_data.get("yogas", [])[:8]
            ],
            body_style,
        )
    )
    story.append(Paragraph("Active chart pressures", card_title_style))
    active_doshas = [
        detail for detail in report_data.get("doshas", {}).get("dosha_details", []) if detail.get("present")
    ]
    story.extend(
        _bullet_lines(
            [f"{item.get('name')}: {item.get('description')}" for item in active_doshas[:6]],
            body_style,
        )
    )

    story.append(Spacer(1, 12))
    story.append(Paragraph("Timing Outlook", section_style))
    timing_band = timing.get("timing_band")
    if timing_band:
        timing_color = {
            "Excellent": "#bbf7d0",
            "Supportive": "#dbeafe",
            "Mixed": "#fde68a",
            "Needs care": "#fecaca",
        }.get(timing_band, "#e5e7eb")
        story.append(_chip(timing_band, timing_color))
        story.append(Spacer(1, 6))
    if timing.get("plain_english"):
        story.append(Paragraph(_safe(timing.get("plain_english", "")), body_style))
    story.append(Paragraph(_safe(timing.get("current_cycle", "")), body_style))
    if timing.get("best_for_now"):
        story.append(Paragraph("Best used for", card_title_style))
        story.extend(_bullet_lines(timing.get("best_for_now", []), body_style))
    if timing.get("caution_for_now"):
        story.append(Paragraph("Use more care with", card_title_style))
        story.extend(_bullet_lines(timing.get("caution_for_now", []), body_style))

    next_dashas = timing.get("next_dashas", [])
    if next_dashas:
        dasha_rows = [["Planet", "Start", "End"]]
        for item in next_dashas:
            dasha_rows.append([item.get("planet"), item.get("start"), item.get("end")])
        dasha_table = Table(dasha_rows, colWidths=[1.2 * inch, 2.0 * inch, 2.0 * inch], hAlign="LEFT")
        dasha_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
                    ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#e5e7eb")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(dasha_table)
        story.append(Spacer(1, 8))

    transits = timing.get("supportive_transits", []) + timing.get("challenging_transits", [])
    if transits:
        transit_rows = [["Planet", "House From Moon", "Score", "Tone"]]
        for item in timing.get("supportive_transits", []):
            transit_rows.append([item["planet"], item["house_from_moon"], f'{item["score"]:.2f}', "Supportive"])
        for item in timing.get("challenging_transits", []):
            transit_rows.append([item["planet"], item["house_from_moon"], f'{item["score"]:.2f}', "Challenging"])
        transit_table = Table(transit_rows, colWidths=[1.4 * inch, 1.6 * inch, 1.0 * inch, 1.4 * inch], hAlign="LEFT")
        transit_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#d1d5db")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(transit_table)

    # Phase 5.5: Dasha × Domain Activation Matrix
    dasha_matrix = report_data.get("dasha_domain_matrix", [])
    if dasha_matrix:
        story.append(Spacer(1, 14))
        story.append(Paragraph("Current Dasha Activation", section_style))
        dm_rows = [["Domain", "Maha", "Antar", "Pratyantar", "Composite"]]
        for row in dasha_matrix:
            maha_info = row.get("maha", {})
            antar_info = row.get("antar", {})
            prat_info = row.get("pratyantar", {})
            dm_rows.append([
                row.get("domain", "").title(),
                f"{maha_info.get('band', 'N/A')} ({maha_info.get('activation', 0):.1f})",
                f"{antar_info.get('band', 'N/A')} ({antar_info.get('activation', 0):.1f})",
                f"{prat_info.get('band', 'N/A')} ({prat_info.get('activation', 0):.1f})",
                f"{row.get('composite', 0):.2f}",
            ])
        dm_table = Table(
            dm_rows,
            colWidths=[1.2 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch, 0.9 * inch],
            repeatRows=1,
            hAlign="LEFT",
        )
        dm_style_commands = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#d1d5db")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("LEADING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]
        # Color-code composite column by activation level
        for i, row in enumerate(dasha_matrix, start=1):
            comp = row.get("composite", 0)
            if comp >= 1.5:
                bg = "#bbf7d0"
            elif comp >= 0.8:
                bg = "#dbeafe"
            elif comp >= 0.0:
                bg = "#fef9c3"
            else:
                bg = "#fecaca"
            dm_style_commands.append(("BACKGROUND", (4, i), (4, i), colors.HexColor(bg)))
        dm_table.setStyle(TableStyle(dm_style_commands))
        story.append(dm_table)
        story.append(Spacer(1, 8))

    story.append(PageBreak())
    story.append(Paragraph("Remedies And Practical Focus", section_style))
    if action_plan:
        story.append(Paragraph("Action plan", card_title_style))
        story.append(Paragraph("Lean into", card_title_style))
        story.extend(_bullet_lines(action_plan.get("lean_into", []), body_style))
        story.append(Paragraph("Watch for", card_title_style))
        story.extend(_bullet_lines(action_plan.get("watch_for", []), body_style))
        story.append(Paragraph("Next steps", card_title_style))
        story.extend(_bullet_lines(action_plan.get("next_steps", []), body_style))
        story.append(Spacer(1, 10))

    remedy_focus = report_data.get("remedy_focus", {})
    story.append(Paragraph("Priority actions", card_title_style))
    story.extend(_bullet_lines(remedy_focus.get("priority_actions", []), body_style))
    story.append(Paragraph("Supportive items", card_title_style))
    story.extend(_bullet_lines(remedy_focus.get("supportive_items", []), body_style))
    story.append(Paragraph("Avoidances", card_title_style))
    story.extend(_bullet_lines(remedy_focus.get("avoidances", []), body_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Lal Kitab quick remedies", card_title_style))
    for item in report_data.get("remedies", {}).get("lal_kitab", [])[:4]:
        story.append(
            Paragraph(
                f"<b>{_safe(item.get('planet'))} in house {_safe(item.get('house'))}</b>: "
                f"{_safe(item.get('effect_en'))}",
                body_style,
            )
        )
        remedies_line = ", ".join(item.get("remedies_en", [])[:3]) or "No specific remedy listed."
        story.append(Paragraph(f"Suggested: {_safe(remedies_line)}", small_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
