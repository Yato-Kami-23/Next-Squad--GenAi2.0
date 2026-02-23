import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


# ── Color Palette ────────────────────────────────────────────────────────────
DEEP_BLUE   = colors.HexColor("#0F2D5C")
MID_BLUE    = colors.HexColor("#1A56A0")
ACCENT      = colors.HexColor("#F0A500")
LIGHT_GREY  = colors.HexColor("#F4F6FA")
MED_GREY    = colors.HexColor("#DEE3ED")
WHITE       = colors.white
TEXT_DARK   = colors.HexColor("#1A1A2E")


def build_styles():
    base = getSampleStyleSheet()
    styles = {}

    styles["cover_title"] = ParagraphStyle(
        "cover_title", fontSize=28, leading=34, textColor=WHITE,
        fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=6
    )
    styles["cover_sub"] = ParagraphStyle(
        "cover_sub", fontSize=13, leading=18, textColor=colors.HexColor("#CBD5E8"),
        fontName="Helvetica", alignment=TA_CENTER, spaceAfter=4
    )
    styles["section_title"] = ParagraphStyle(
        "section_title", fontSize=15, leading=20, textColor=DEEP_BLUE,
        fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6
    )
    styles["module_title"] = ParagraphStyle(
        "module_title", fontSize=12, leading=16, textColor=WHITE,
        fontName="Helvetica-Bold", alignment=TA_LEFT
    )
    styles["body"] = ParagraphStyle(
        "body", fontSize=10, leading=15, textColor=TEXT_DARK,
        fontName="Helvetica", spaceAfter=4
    )
    styles["bullet"] = ParagraphStyle(
        "bullet", fontSize=10, leading=14, textColor=TEXT_DARK,
        fontName="Helvetica", leftIndent=12, spaceAfter=2,
        bulletIndent=4, bulletFontName="Helvetica"
    )
    styles["label"] = ParagraphStyle(
        "label", fontSize=9, leading=12, textColor=MID_BLUE,
        fontName="Helvetica-Bold", spaceAfter=2
    )
    styles["tag"] = ParagraphStyle(
        "tag", fontSize=9, leading=12, textColor=DEEP_BLUE,
        fontName="Helvetica-Bold"
    )
    return styles


def generate_pdf(curriculum: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=16*mm, bottomMargin=16*mm,
        title=curriculum.get("course_title", "Curriculum")
    )

    styles = build_styles()
    story = []
    W = A4[0] - 36*mm  # usable width

    # ── Cover Page ───────────────────────────────────────────────────────────
    cover_data = [[
        Paragraph(curriculum.get("course_title", "Curriculum Report"), styles["cover_title"]),
    ]]
    cover_table = Table(cover_data, colWidths=[W])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), DEEP_BLUE),
        ("ROUNDEDCORNERS", [8]),
        ("TOPPADDING",  (0,0), (-1,-1), 28),
        ("BOTTOMPADDING",(0,0), (-1,-1), 28),
        ("LEFTPADDING", (0,0), (-1,-1), 16),
        ("RIGHTPADDING",(0,0), (-1,-1), 16),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 8))

    # Meta pills
    meta_items = [
        curriculum.get("education_level",""),
        f"{curriculum.get('duration_weeks',0)} Weeks",
        curriculum.get("subject_area",""),
        f"AI: {curriculum.get('provider','').capitalize()}",
    ]
    meta_cells = [[Paragraph(f"  {m}  ", styles["tag"]) for m in meta_items]]
    meta_tbl = Table(meta_cells, colWidths=[W/4]*4)
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), LIGHT_GREY),
        ("ALIGN",       (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING",  (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("ROUNDEDCORNERS",[4]),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 10))

    # ── Course Description ────────────────────────────────────────────────────
    story.append(Paragraph("Course Overview", styles["section_title"]))
    story.append(HRFlowable(width=W, thickness=2, color=ACCENT, spaceAfter=6))
    story.append(Paragraph(curriculum.get("course_description",""), styles["body"]))
    story.append(Spacer(1, 6))

    # Assessment strategy
    story.append(Paragraph("Assessment Strategy", styles["label"]))
    story.append(Paragraph(curriculum.get("assessment_strategy",""), styles["body"]))
    story.append(Spacer(1, 8))

    # ── Learning Outcomes ─────────────────────────────────────────────────────
    story.append(Paragraph("Learning Outcomes", styles["section_title"]))
    story.append(HRFlowable(width=W, thickness=2, color=ACCENT, spaceAfter=6))

    lo_rows = [["Code", "Learning Outcome", "Bloom's Level"]]
    for lo in curriculum.get("learning_outcomes", []):
        lo_rows.append([
            Paragraph(lo.get("code",""), styles["label"]),
            Paragraph(lo.get("description",""), styles["body"]),
            Paragraph(lo.get("bloom_level",""), styles["body"]),
        ])

    lo_tbl = Table(lo_rows, colWidths=[14*mm, W - 42*mm, 28*mm])
    lo_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0), DEEP_BLUE),
        ("TEXTCOLOR",    (0,0), (-1,0), WHITE),
        ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,0), 9),
        ("ALIGN",        (0,0), (-1,0), "CENTER"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, LIGHT_GREY]),
        ("GRID",         (0,0), (-1,-1), 0.5, MED_GREY),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
    ]))
    story.append(lo_tbl)
    story.append(Spacer(1, 10))

    # ── Modules ───────────────────────────────────────────────────────────────
    story.append(Paragraph("Curriculum Modules", styles["section_title"]))
    story.append(HRFlowable(width=W, thickness=2, color=ACCENT, spaceAfter=8))

    for module in curriculum.get("modules", []):
        # Module header bar
        mod_header = Table(
            [[Paragraph(f"Module {module.get('module_number','')}:  {module.get('title','')}", styles["module_title"])]],
            colWidths=[W]
        )
        mod_header.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), MID_BLUE),
            ("TOPPADDING",   (0,0),(-1,-1), 8),
            ("BOTTOMPADDING",(0,0),(-1,-1), 8),
            ("LEFTPADDING",  (0,0),(-1,-1), 10),
        ]))
        story.append(mod_header)
        story.append(Spacer(1, 4))
        story.append(Paragraph(module.get("description",""), styles["body"]))

        week_range = module.get("weeks", [])
        if week_range:
            story.append(Paragraph(
                f"Weeks: {week_range[0]} – {week_range[-1]}  |  "
                f"Outcomes: {', '.join(module.get('learning_outcomes',[]))}",
                styles["label"]
            ))

        # Topics table
        topic_rows = [["Week", "Topic", "Subtopics", "Assessment"]]
        for t in module.get("topics", []):
            subs = "\n".join(f"• {s}" for s in t.get("subtopics", []))
            topic_rows.append([
                Paragraph(str(t.get("week","")), styles["body"]),
                Paragraph(t.get("title",""), styles["body"]),
                Paragraph(subs, styles["body"]),
                Paragraph(t.get("assessment_type",""), styles["body"]),
            ])

        t_tbl = Table(topic_rows, colWidths=[12*mm, 40*mm, W-92*mm, 30*mm])
        t_tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,0), DEEP_BLUE),
            ("TEXTCOLOR",    (0,0),(-1,0), WHITE),
            ("FONTNAME",     (0,0),(-1,0), "Helvetica-Bold"),
            ("FONTSIZE",     (0,0),(-1,0), 8),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, LIGHT_GREY]),
            ("GRID",         (0,0),(-1,-1), 0.4, MED_GREY),
            ("VALIGN",       (0,0),(-1,-1), "TOP"),
            ("TOPPADDING",   (0,0),(-1,-1), 4),
            ("BOTTOMPADDING",(0,0),(-1,-1), 4),
            ("LEFTPADDING",  (0,0),(-1,-1), 5),
            ("FONTSIZE",     (0,1),(-1,-1), 8),
        ]))
        story.append(t_tbl)
        story.append(Spacer(1, 10))

    # ── Recommended Topics & Industry Alignment ──────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Recommended Additional Topics", styles["section_title"]))
    story.append(HRFlowable(width=W, thickness=2, color=ACCENT, spaceAfter=6))
    for topic in curriculum.get("recommended_topics", []):
        story.append(Paragraph(f"• {topic}", styles["bullet"]))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Industry Alignment", styles["section_title"]))
    story.append(HRFlowable(width=W, thickness=2, color=ACCENT, spaceAfter=6))

    skills = curriculum.get("industry_alignment", [])
    if skills:
        skill_rows = [[Paragraph(s, styles["body"]) for s in skills[i:i+3]]
                      for i in range(0, len(skills), 3)]
        # pad last row
        while len(skill_rows[-1]) < 3:
            skill_rows[-1].append(Paragraph("", styles["body"]))

        skill_tbl = Table(skill_rows, colWidths=[W/3]*3)
        skill_tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), LIGHT_GREY),
            ("GRID",         (0,0),(-1,-1), 0.4, MED_GREY),
            ("TOPPADDING",   (0,0),(-1,-1), 6),
            ("BOTTOMPADDING",(0,0),(-1,-1), 6),
            ("LEFTPADDING",  (0,0),(-1,-1), 8),
        ]))
        story.append(skill_tbl)

    # ── Footer note ───────────────────────────────────────────────────────────
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width=W, thickness=1, color=MED_GREY))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Generated by CurricuForge · AI-Powered Curriculum Design System",
        ParagraphStyle("footer", fontSize=8, textColor=colors.grey,
                       fontName="Helvetica", alignment=TA_CENTER)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
