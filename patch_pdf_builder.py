import re

with open('app/services/pdf_builder.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I want to add Dasha and Gochara sections to the PDF
dasha_old = """    # ── 6. Current Dasha ──
    story.append(Paragraph("6. Current Dasha / वर्तमान दशा", h1_style))
    dasha = report_data.get("current_dasha", {})
    story.append(Paragraph(f"Mahadasha (महादशा): {dasha.get('maha', 'N/A')}", normal_en))
    story.append(Paragraph(f"Antardasha (अन्तर्दशा): {dasha.get('antar', 'N/A')}", normal_en))
    story.append(Spacer(1, 20))"""

dasha_new = """    # ── 6. Dasha Timeline & Sade Sati & Transits ──
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
    story.append(Paragraph("<b>Sade Sati (Saturn Transit)</b>", h2_style))
    if sade.get("is_active"):
        story.append(Paragraph(f"⚠️ <b>Currently Active</b> (Phase: {sade.get('current_phase')})", normal_en))
    else:
        story.append(Paragraph(f"Not currently active. Next phase starts: {sade.get('next_occurrence', 'Unknown')}", normal_en))
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
    story.append(Spacer(1, 20))"""

content = content.replace(dasha_old, dasha_new)

with open('app/services/pdf_builder.py', 'w', encoding='utf-8') as f:
    f.write(content)
