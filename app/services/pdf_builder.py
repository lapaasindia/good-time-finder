"""
PDF Report Builder with Bilingual Support (Hindi + English).
Generates a comprehensive astrological report.
"""
from __future__ import annotations

import io
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Define path to the Hindi-supporting font
FONT_PATH = Path(__file__).parent.parent / "fonts" / "NotoSansDevanagari-Regular.ttf"

def register_fonts():
    try:
        pdfmetrics.registerFont(TTFont("NotoHindi", str(FONT_PATH)))
    except Exception as e:
        print(f"Failed to load font: {e}")

# Register fonts globally when module loads
register_fonts()

def _draw_dark_bg(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor('#131313'))
    canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1, stroke=0)
    canvas.restoreState()

def build_pdf_report(report_data: dict) -> bytes:
    """Builds a PDF file in memory from the report dictionary."""
    buffer = io.BytesBytesIO() if hasattr(io, "BytesBytesIO") else io.BytesIO()
    doc = BaseDocTemplate(
        buffer, pagesize=letter,
        rightMargin=48, leftMargin=48,
        topMargin=48, bottomMargin=48
    )
    
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='background', frames=frame, onPage=_draw_dark_bg)
    doc.addPageTemplates([template])
    
    styles = getSampleStyleSheet()
    
    # Custom styles (Indies Education Design System)
    title_style = ParagraphStyle(
        'MainTitle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=28, spaceAfter=8, textColor=colors.HexColor('#97d94f')
    )
    subtitle_style = ParagraphStyle(
        'SubTitle', parent=styles['Title'], fontName='Helvetica', fontSize=14, spaceAfter=40, textColor=colors.HexColor('#a3a3a3')
    )
    h1_style = ParagraphStyle(
        'Heading1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=20, spaceAfter=16, textColor=colors.HexColor('#e5e2e1')
    )
    h2_style = ParagraphStyle(
        'Heading2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=15, spaceAfter=12, textColor=colors.HexColor('#97d94f')
    )
    normal_en = ParagraphStyle(
        'NormalEn', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=16, spaceAfter=8, textColor=colors.HexColor('#e5e2e1')
    )
    normal_hi = ParagraphStyle(
        'NormalHi', parent=styles['Normal'], fontName='NotoHindi', fontSize=13, leading=18, spaceAfter=8, textColor=colors.HexColor('#a3a3a3')
    )
    mixed_style = ParagraphStyle(
        'Mixed', parent=styles['Normal'], fontName='NotoHindi', fontSize=12, leading=17, spaceAfter=8, textColor=colors.HexColor('#e5e2e1')
    )

    story = []

    # ── Cover Page ──
    story.append(Paragraph("Comprehensive Astrology Report", title_style))
    story.append(Paragraph("सम्पूर्ण ज्योतिषीय जीवन फल (Bilingual Edition)", mixed_style))
    story.append(Spacer(1, 30))
    
    pi = report_data.get("personal_info", {})
    story.append(Paragraph(f"<b>Name / नाम:</b> {pi.get('name')}", mixed_style))
    story.append(Paragraph(f"<b>Birth Date / जन्म तिथि:</b> {pi.get('dob')}", mixed_style))
    story.append(Paragraph(f"<b>Lagna / लग्न:</b> {pi.get('lagna')}", mixed_style))
    story.append(Paragraph(f"<b>Moon Sign / चंद्र राशि:</b> {pi.get('moon_sign')}", mixed_style))
    story.append(Paragraph(f"<b>Nakshatra / नक्षत्र:</b> {pi.get('nakshatra')}", mixed_style))
    story.append(PageBreak())

    # ── 1. Personality Profile ──
    story.append(Paragraph("1. Personality Profile / व्यक्तित्व विश्लेषण", h1_style))
    pers = report_data.get("personality", {}).get("lagna_based", {})
    
    story.append(Paragraph("<b>Nature / स्वभाव:</b>", normal_en))
    story.append(Paragraph(pers.get("nature_en", ""), normal_en))
    story.append(Paragraph(pers.get("nature_hi", ""), normal_hi))
    
    story.append(Paragraph("<b>Career / करियर:</b>", normal_en))
    story.append(Paragraph(pers.get("career_en", ""), normal_en))
    story.append(Paragraph(pers.get("career_hi", ""), normal_hi))
    
    story.append(Paragraph("<b>Health / स्वास्थ्य:</b>", normal_en))
    story.append(Paragraph(pers.get("health_en", ""), normal_en))
    story.append(Paragraph(pers.get("health_hi", ""), normal_hi))
    
    story.append(Paragraph("<b>Relationships / रिश्ते:</b>", normal_en))
    story.append(Paragraph(pers.get("relationship_en", ""), normal_en))
    story.append(Paragraph(pers.get("relationship_hi", ""), normal_hi))
    story.append(Spacer(1, 20))

    # ── 2. Astrological Synthesis (The Jury) ──
    story.append(PageBreak())
    story.append(Paragraph("2. Astrological Synthesis / ज्योतिषीय निष्कर्ष", h1_style))
    
    for syn in report_data.get("synthesis", []):
        story.append(Paragraph(f"<b>{syn['domain_en']} / {syn['domain_hi']}</b>", h2_style))
        story.append(Paragraph(f"<b>Summary:</b> {syn['summary_en']}", normal_en))
        story.append(Paragraph(f"<b>निष्कर्ष:</b> {syn['summary_hi']}", normal_hi))
        story.append(Paragraph("<i>Key Astrological Factors:</i>", normal_en))
        for f_en, f_hi in zip(syn.get("key_factors_en", []), syn.get("key_factors_hi", [])):
            story.append(Paragraph(f"• {f_en}", normal_en))
            story.append(Paragraph(f"  ({f_hi})", normal_hi))
        story.append(Spacer(1, 15))

    story.append(PageBreak())

    # ── 3. Planetary Placements & Meanings ──
    story.append(Paragraph("3. Planets & Their Meaning / ग्रहों की स्थिति और अर्थ", h1_style))
    
    for planet_data in report_data.get("planetary_positions", []):
        story.append(Paragraph(f"<b>{planet_data['planet']} (in {planet_data['sign']}, House {planet_data['house']})</b>", h2_style))
        story.append(Paragraph(f"Strength/बल: {planet_data['strength']}", normal_en))
        
        if planet_data.get("avastha_en"):
            story.append(Paragraph(f"Avastha (Age State): {planet_data['avastha_en']} / {planet_data['avastha_hi']}", mixed_style))
        
        story.append(Paragraph(f"<i>Nature / प्रकृति:</i>", normal_en))
        story.append(Paragraph(planet_data.get("nature_en", ""), normal_en))
        story.append(Paragraph(planet_data.get("nature_hi", ""), normal_hi))
        
        story.append(Paragraph(f"<i>Significations / कारक:</i>", normal_en))
        story.append(Paragraph(planet_data.get("significations_en", ""), normal_en))
        story.append(Paragraph(planet_data.get("significations_hi", ""), normal_hi))
        story.append(Spacer(1, 10))

    story.append(PageBreak())

    # ── 4. Houses Analysis ──
    story.append(Paragraph("4. House Meanings / भाव विश्लेषण", h1_style))
    
    for house_data in report_data.get("houses_info", []):
        name_en = house_data.get('name_en', '')
        name_hi = house_data.get('name_hi', '')
        story.append(Paragraph(f"<b>{name_en} / {name_hi}</b>", h2_style))
        
        occ = ", ".join(house_data.get("occupants", []))
        if not occ:
            occ = "None (Empty House)"
            
        story.append(Paragraph(f"Occupants/ग्रह: {occ}", normal_en))
        
        aspects = ", ".join(house_data.get("aspected_by", []))
        if aspects:
            story.append(Paragraph(f"Aspected By/दृष्टि: {aspects}", normal_en))
            
        story.append(Paragraph(house_data.get("domain_en", ""), normal_en))
        story.append(Paragraph(house_data.get("domain_hi", ""), normal_hi))
        story.append(Spacer(1, 8))

    story.append(PageBreak())

    # ── 5. Yogas & Doshas ──
    story.append(Paragraph("5. Key Yogas & Special Conditions / योग एवं दोष", h1_style))
    
    story.append(Paragraph("<b>Natal Yogas / जन्मकालीन योग:</b>", h2_style))
    for y in report_data.get("yogas", []):
        story.append(Paragraph(f"• <b>{y['name']}</b> - {y['description']}", normal_en))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Special Conditions / विशेष स्थितियां:</b>", h2_style))
    doshas = report_data.get("doshas", {})
    if doshas.get("kaal_sarp_dosha"):
        story.append(Paragraph(f"⚠ Kaal Sarp Dosha ({doshas.get('kaal_sarp_type')}) is active.", normal_en))
    if doshas.get("mangal_dosha"):
        story.append(Paragraph(f"⚠ Mangal Dosha is active.", normal_en))
    
    retro = [p for p, data in doshas.get("retrograde", {}).items() if data.get("retrograde")]
    if retro:
        story.append(Paragraph(f"Retrograde Planets (Vakri): {', '.join(retro)}", normal_en))
    
    combust = [p for p, data in doshas.get("combustion", {}).items() if data.get("combust")]
    if combust:
        story.append(Paragraph(f"Combust Planets (Asta): {', '.join(combust)}", normal_en))
        
    story.append(PageBreak())

    # ── 6. Dasha Timeline & Sade Sati & Transits ──
    story.append(Paragraph("6. Dasha, Sade Sati & Current Transits", h1_style))
    dasha = report_data.get("current_dasha", {})
    story.append(Paragraph(f"<b>Current Active Dasha:</b> {dasha.get('maha', 'N/A')} Mahadasha, {dasha.get('antar', 'N/A')} Antardasha", normal_en))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Upcoming Mahadashas (Life Chapters)</b>", h2_style))
    d_data = [["Planet", "Start Date", "End Date"]]
    for d in report_data.get("dasha_list", []):
        d_data.append([d['planet'], d['start'], d['end']])
        
    t = Table(d_data, colWidths=[120, 120, 120])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2a2a2a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#e5e2e1')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#131313')),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#a3a3a3')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#2a2a2a'))
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    # Sade Sati
    sade = report_data.get("sade_sati", {})
    if hasattr(sade, "is_active"): # Handle object vs dict
        is_active = sade.is_active
        current_phase = getattr(sade, "current_phase", "Unknown")
        next_occurrence = getattr(sade, "next_occurrence", "Unknown")
    elif isinstance(sade, dict):
        is_active = sade.get("is_active")
        current_phase = sade.get("current_phase", "Unknown")
        next_occurrence = sade.get("next_occurrence", "Unknown")
    else:
        is_active = False
        current_phase = "Unknown"
        next_occurrence = "Unknown"

    story.append(Paragraph("<b>Sade Sati (Saturn Transit)</b>", h2_style))
    if is_active:
        story.append(Paragraph(f"⚠️ <b>Currently Active</b> (Phase: {current_phase})", normal_en))
    else:
        story.append(Paragraph(f"Not currently active. Next phase starts: {next_occurrence}", normal_en))
    story.append(Spacer(1, 20))

    # Gochara (Transits)
    transits = report_data.get("transits", {})
    story.append(Paragraph("<b>Current Transits (Gochara) from Moon</b>", h2_style))
    tr_data = [["Planet", "House from Moon", "Score"]]
    for p, v in transits.items():
        tr_data.append([p, str(v['house_from_moon']), str(v['score'])])
        
    t2 = Table(tr_data, colWidths=[120, 120, 120])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2a2a2a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#e5e2e1')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#131313')),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#a3a3a3')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#2a2a2a'))
    ]))
    story.append(t2)
    story.append(Spacer(1, 20))

    # ── 7. Comprehensive Remedies ──
    story.append(PageBreak())
    story.append(Paragraph("7. Comprehensive Remedies / सम्पूर्ण उपाय", h1_style))
    
    remedies = report_data.get("remedies", {})

    # Gemstones
    story.append(Paragraph("<b>Gemstone Prescriptions / रत्न सुझाव</b>", h2_style))
    gems = remedies.get("gemstones", {})
    if not gems:
        story.append(Paragraph("No gemstone recommended.", normal_en))
    for p, gem_info in gems.items():
        story.append(Paragraph(f"<b>{p}</b>: {gem_info['gem_en']} / {gem_info['gem_hi']}", mixed_style))
        story.append(Paragraph(f"Status: {gem_info['status']} ({gem_info['status_hi']})", mixed_style))
        story.append(Paragraph(f"Reason: {gem_info['reason']}", normal_en))
        story.append(Spacer(1, 5))
    story.append(Spacer(1, 10))

    # Rudraksha
    story.append(Paragraph("<b>Rudraksha Recommendations / रुद्राक्ष सुझाव</b>", h2_style))
    rudras = remedies.get("rudraksha", [])
    if not rudras:
        story.append(Paragraph("No specific Rudraksha required.", normal_en))
    for r in rudras:
        story.append(Paragraph(f"<b>{r['planet']}</b>: {r['rudraksha_en']} / {r['rudraksha_hi']}", mixed_style))
        story.append(Paragraph(f"Benefit: {r['benefit_en']}", normal_en))
        story.append(Paragraph(f"लाभ: {r['benefit_hi']}", normal_hi))
        story.append(Spacer(1, 5))
    story.append(Spacer(1, 10))

    # Vastu
    story.append(Paragraph("<b>Astro-Vastu / वास्तु सुझाव</b>", h2_style))
    vastu = remedies.get("vastu", {})
    if vastu:
        story.append(Paragraph(f"Strongest Planet: <b>{vastu.get('planet')}</b>", normal_en))
        story.append(Paragraph(f"Lucky Direction: {vastu.get('direction_en')} / {vastu.get('direction_hi')}", mixed_style))
        story.append(Paragraph(vastu.get('benefit_en', ''), normal_en))
        story.append(Paragraph(vastu.get('benefit_hi', ''), normal_hi))
    story.append(Spacer(1, 15))
    
    # Lal Kitab
    story.append(PageBreak())
    story.append(Paragraph("<b>Lal Kitab Remedies & Donations / लाल किताब उपाय एवं दान</b>", h2_style))
    
    for lk in remedies.get("lal_kitab", []):
        story.append(Paragraph(f"<b>{lk['planet']} in House {lk['house']}</b>", h2_style))
        story.append(Paragraph(lk["effect_en"], normal_en))
        story.append(Paragraph(lk["effect_hi"], normal_hi))
        
        story.append(Paragraph("<i>Remedies / उपाय:</i>", normal_hi))
        story.append(Paragraph("EN: " + ", ".join(lk["remedies_en"]), normal_en))
        story.append(Paragraph("HI: " + ", ".join(lk["remedies_hi"]), normal_hi))
        
        story.append(Paragraph("<i>Donations / दान:</i>", normal_hi))
        story.append(Paragraph("EN: " + ", ".join(lk["donate_en"]), normal_en))
        story.append(Paragraph("HI: " + ", ".join(lk["donate_hi"]), normal_hi))
        
        story.append(Paragraph("<i>Avoid / परहेज़:</i>", normal_hi))
        story.append(Paragraph("EN: " + ", ".join(lk["avoid_en"]), normal_en))
        story.append(Paragraph("HI: " + ", ".join(lk["avoid_hi"]), normal_hi))
        story.append(Spacer(1, 15))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
