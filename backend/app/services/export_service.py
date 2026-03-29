"""PDF report generation service using ReportLab."""

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)


# Color palette
PRIMARY = colors.HexColor("#1E40AF")
PRIMARY_LIGHT = colors.HexColor("#3B82F6")
DARK = colors.HexColor("#1F2937")
MUTED = colors.HexColor("#6B7280")
SUCCESS = colors.HexColor("#10B981")
WARNING = colors.HexColor("#F59E0B")
DANGER = colors.HexColor("#EF4444")
BG_LIGHT = colors.HexColor("#F9FAFB")
WHITE = colors.white


def _get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        "ReportTitle", parent=styles["Title"],
        fontSize=22, textColor=PRIMARY, spaceAfter=4,
        fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        "ReportSubtitle", parent=styles["Normal"],
        fontSize=9, textColor=MUTED, spaceAfter=16,
    ))
    styles.add(ParagraphStyle(
        "SectionHeading", parent=styles["Heading2"],
        fontSize=13, textColor=DARK, spaceBefore=18, spaceAfter=8,
        fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        "BodyText", parent=styles["Normal"],
        fontSize=9, textColor=DARK, leading=13,
    ))
    styles.add(ParagraphStyle(
        "SmallMuted", parent=styles["Normal"],
        fontSize=8, textColor=MUTED, leading=11,
    ))
    styles.add(ParagraphStyle(
        "FooterStyle", parent=styles["Normal"],
        fontSize=7, textColor=MUTED, alignment=1,
    ))
    return styles


def _build_table(data: list[list], col_widths=None, header: bool = True) -> Table:
    """Build a styled table."""
    table = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    style_cmds = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (-1, -1), DARK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
    ]
    if header and len(data) > 0:
        style_cmds.extend([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ])
    # Alternate row colors
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), BG_LIGHT))
    table.setStyle(TableStyle(style_cmds))
    return table


def _escape(text: str) -> str:
    """Escape XML special characters for ReportLab Paragraphs."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def generate_pdf_report(scan_response: dict) -> bytes:
    """Generate a professional PDF report from scan response data."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        topMargin=0.6 * inch, bottomMargin=0.6 * inch,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
    )
    styles = _get_styles()
    story: list = []

    ats = scan_response.get("ats_score", {})
    ai = scan_response.get("ai_score", {})
    combined = scan_response.get("combined", {})
    fixes = scan_response.get("fixes", [])
    readability = scan_response.get("readability", {})
    text_analytics = scan_response.get("text_analytics", {})
    heatmap = ai.get("heatmap", [])
    signals = ai.get("signals", [])

    # -- Header --
    story.append(Paragraph("ResumeShield Analysis Report", styles["ReportTitle"]))
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    story.append(Paragraph(f"Generated on {timestamp}", styles["ReportSubtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY_LIGHT, spaceAfter=12))

    # -- Score Summary --
    story.append(Paragraph("Score Summary", styles["SectionHeading"]))

    ats_score = ats.get("overall_score", 0)
    ats_grade = ats.get("grade", "N/A")
    ai_score = ai.get("overall_score", 0)
    ai_risk = ai.get("risk_level", "Unknown")
    readiness_score = combined.get("interview_readiness_score", 0)
    readiness_level = combined.get("readiness_level", "N/A")

    score_data = [
        ["Metric", "Score", "Details"],
        ["ATS Score", f"{ats_score}/100", f"Grade: {ats_grade}"],
        ["AI Detection Score", f"{ai_score}/100", f"Risk: {ai_risk}"],
        ["Interview Readiness", f"{readiness_score}/100", readiness_level.replace("_", " ").title()],
        ["Competitor Percentile", f"Top {100 - combined.get('competitor_percentile', 50)}%", ""],
    ]
    story.append(_build_table(score_data, col_widths=[2.2 * inch, 1.3 * inch, 3.2 * inch]))
    story.append(Spacer(1, 8))

    # -- ATS Breakdown --
    story.append(Paragraph("ATS Score Breakdown", styles["SectionHeading"]))

    ats_breakdown = [
        ["Component", "Score"],
        ["Keyword Match", f"{ats.get('keyword_match_score', 0)}/100"],
        ["Keyword Placement", f"{ats.get('keyword_placement_score', 0)}/100"],
        ["Section Structure", f"{ats.get('section_score', 0)}/100"],
        ["Formatting", f"{ats.get('formatting_score', 0)}/100"],
        ["Relevance", f"{ats.get('relevance_score', 0)}/100"],
    ]
    story.append(_build_table(ats_breakdown, col_widths=[4.0 * inch, 2.7 * inch]))

    # Missing keywords
    missing = ats.get("missing_keywords", [])
    if missing:
        story.append(Spacer(1, 6))
        kw_text = ", ".join(_escape(k) for k in missing[:20])
        suffix = "..." if len(missing) > 20 else ""
        story.append(Paragraph(
            f"<b>Missing Keywords:</b> {kw_text}{suffix}",
            styles["BodyText"],
        ))
    story.append(Spacer(1, 4))

    # -- AI Detection Signals --
    story.append(Paragraph("AI Detection Signals", styles["SectionHeading"]))

    if signals:
        sig_data = [["Signal", "Score", "Max", "Pct", "Details"]]
        for s in signals:
            name = _escape(s.get("name", ""))
            score = s.get("score", 0)
            max_s = s.get("max_score", 0)
            pct = s.get("percentage", 0)
            details = _escape(s.get("details", ""))
            if len(details) > 60:
                details = details[:57] + "..."
            sig_data.append([name, f"{score:.1f}", f"{max_s:.1f}", f"{pct:.0f}%", details])
        story.append(_build_table(
            sig_data,
            col_widths=[1.7 * inch, 0.6 * inch, 0.6 * inch, 0.6 * inch, 3.2 * inch],
        ))
    else:
        story.append(Paragraph("No signals detected.", styles["SmallMuted"]))
    story.append(Spacer(1, 4))

    # -- Heatmap Summary --
    if heatmap:
        story.append(Paragraph("Detection Heatmap", styles["SectionHeading"]))
        heat_data = [["Sentence", "Risk", "Flags"]]
        for h in heatmap[:30]:
            text = _escape(h.get("text", ""))
            if len(text) > 80:
                text = text[:77] + "..."
            risk = h.get("risk", "")
            flags = ", ".join(h.get("flags", [])[:3])
            heat_data.append([text, risk, flags])
        story.append(_build_table(
            heat_data,
            col_widths=[3.8 * inch, 0.9 * inch, 2.0 * inch],
        ))
        story.append(Spacer(1, 4))

    # -- Fix Suggestions --
    if fixes:
        story.append(Paragraph("Fix Suggestions", styles["SectionHeading"]))
        for i, fix in enumerate(fixes, 1):
            priority = fix.get("priority", "medium")
            title = _escape(fix.get("title", ""))
            desc = _escape(fix.get("description", ""))
            category = _escape(fix.get("category", ""))
            impact = _escape(fix.get("estimated_impact", ""))

            priority_display = priority.upper()
            line = f"<b>{i}. [{priority_display}] {title}</b>"
            if category:
                line += f"  <i>({category})</i>"
            story.append(Paragraph(line, styles["BodyText"]))
            story.append(Paragraph(desc, styles["SmallMuted"]))
            if impact:
                story.append(Paragraph(f"Impact: {impact}", styles["SmallMuted"]))
            story.append(Spacer(1, 4))

    # -- Readability --
    story.append(Paragraph("Readability", styles["SectionHeading"]))
    read_data = [
        ["Metric", "Value"],
        ["Flesch-Kincaid Grade", str(readability.get("flesch_kincaid_grade", "N/A"))],
        ["Reading Time", f"{readability.get('reading_time_seconds', 0)}s"],
        ["Word Count", str(readability.get("word_count", 0))],
        ["Sentence Count", str(readability.get("sentence_count", 0))],
        ["Avg Sentence Length", str(readability.get("avg_sentence_length", 0))],
        ["Avg Word Length", str(readability.get("avg_word_length", 0))],
        ["Vocabulary Richness", f"{readability.get('vocabulary_richness', 0):.2f}"],
    ]
    story.append(_build_table(read_data, col_widths=[3.5 * inch, 3.2 * inch]))
    story.append(Spacer(1, 4))

    # -- Text Analytics --
    story.append(Paragraph("Text Analytics", styles["SectionHeading"]))
    ta_data = [
        ["Metric", "Value"],
        ["Word Count", str(text_analytics.get("word_count", 0))],
        ["Character Count", str(text_analytics.get("character_count", 0))],
        ["Sentence Count", str(text_analytics.get("sentence_count", 0))],
        ["Paragraph Count", str(text_analytics.get("paragraph_count", 0))],
        ["Vocabulary Richness", f"{text_analytics.get('vocabulary_richness', 0):.2f}"],
        ["Longest Sentence", f"{text_analytics.get('longest_sentence', 0)} words"],
        ["Shortest Sentence", f"{text_analytics.get('shortest_sentence', 0)} words"],
    ]
    story.append(_build_table(ta_data, col_widths=[3.5 * inch, 3.2 * inch]))

    # Top words
    top_words = text_analytics.get("top_words", [])
    if top_words:
        story.append(Spacer(1, 6))
        words_str = ", ".join(f"{_escape(str(w[0]))} ({w[1]})" for w in top_words[:10])
        story.append(Paragraph(f"<b>Top Words:</b> {words_str}", styles["BodyText"]))

    # -- Footer --
    story.append(Spacer(1, 24))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MUTED, spaceAfter=6))
    story.append(Paragraph("Generated by ResumeShield v3.0", styles["FooterStyle"]))

    doc.build(story)
    return buf.getvalue()
