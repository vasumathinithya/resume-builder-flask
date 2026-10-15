
import os
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)


# --------------------------------------------------
# PDF COLORS
# --------------------------------------------------

NAVY = colors.HexColor("#172554")
BLUE = colors.HexColor("#1E3A8A")
TEXT = colors.HexColor("#374151")
MUTED = colors.HexColor("#4B5563")
LINE = colors.HexColor("#DBE3F0")


# --------------------------------------------------
# PDF STYLES
# --------------------------------------------------

styles = getSampleStyleSheet()

name_style = ParagraphStyle(
    "ResumeName",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=21,
    leading=26,
    textColor=NAVY,
    alignment=TA_CENTER,
    spaceAfter=7,
)

contact_style = ParagraphStyle(
    "ResumeContact",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=13,
    textColor=MUTED,
    alignment=TA_CENTER,
)

section_heading_style = ParagraphStyle(
    "ResumeSectionHeading",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=10.5,
    leading=14,
    textColor=BLUE,
    alignment=TA_LEFT,
    spaceAfter=5,
)

body_style = ParagraphStyle(
    "ResumeBody",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    leading=15,
    textColor=TEXT,
    spaceAfter=2,
    splitLongWords=1,
)

bullet_style = ParagraphStyle(
    "ResumeBullet",
    parent=body_style,
    leftIndent=12,
    firstLineIndent=-9,
    spaceAfter=3,
)

education_left_style = ParagraphStyle(
    "EducationLeft",
    parent=body_style,
    leading=15,
)

education_right_style = ParagraphStyle(
    "EducationRight",
    parent=body_style,
    alignment=TA_RIGHT,
    leading=15,
)


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def safe_text(value):
    """Convert a value into text that ReportLab can display safely."""
    if value is None:
        return ""
    return escape(str(value))


def add_section(story, title, content):
    """Add a heading, blue divider, and section content."""

    if not content or not str(content).strip():
        return

    story.append(Spacer(1, 9))

    story.append(
        Paragraph(safe_text(title.upper()), section_heading_style)
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=0.6,
            color=LINE,
            spaceBefore=0,
            spaceAfter=7,
        )
    )

    # Preserve the user's separate lines.
    lines = str(content).replace("\r\n", "\n").replace("\r", "\n").split("\n")

    for line in lines:
        stripped = line.strip()

        if not stripped:
            story.append(Spacer(1, 3))
            continue

        # Convert typed bullets into PDF bullets.
        if stripped.startswith(("•", "▪", "■", "-", "*")):
            text = stripped.lstrip("•▪■-* ").strip()

            if text:
                story.append(
                    Paragraph(
                        "&#8226;&nbsp;&nbsp;" + safe_text(text),
                        bullet_style,
                    )
                )
            continue

        story.append(Paragraph(safe_text(stripped), body_style))


def add_education_section(story, content):
    """
    Display education entries with the main details on the left
    and dates / grades on the right when entries use spacing or tabs.
    """

    if not content or not str(content).strip():
        return

    story.append(Spacer(1, 9))
    story.append(
        Paragraph("EDUCATION", section_heading_style)
    )
    story.append(
        HRFlowable(
            width="100%",
            thickness=0.6,
            color=LINE,
            spaceAfter=7,
        )
    )

    lines = str(content).replace("\r\n", "\n").replace("\r", "\n").split("\n")

    for line in lines:
        if not line.strip():
            story.append(Spacer(1, 3))
            continue

        # Tabs or two-or-more spaces can separate the right column.
        parts = re.split(r"\t+|\s{2,}", line.strip(), maxsplit=1)

        if len(parts) == 2:
            left_text, right_text = parts

            row = [[
                Paragraph(safe_text(left_text), education_left_style),
                Paragraph(safe_text(right_text), education_right_style),
            ]]

            table = Table(
                row,
                colWidths=["72%", "28%"],
                hAlign="LEFT",
            )

            table.setStyle(
                TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 1),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ])
            )

            story.append(table)
        else:
            story.append(
                Paragraph(safe_text(line.strip()), body_style)
            )


# --------------------------------------------------
# MAIN PDF GENERATOR
# --------------------------------------------------

def generate_pdf(resume, output_path):
    """
    Generate a professional resume PDF.

    resume: dictionary containing the saved resume details.
    output_path: destination path for the PDF file.
    """

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    document = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=15 * mm,
        bottomMargin=18 * mm,
        title=f"{resume.get('name', 'Resume')} - Resume",
        author=str(resume.get("name", "")),
    )

    story = []

    # --------------------------
    # Header
    # --------------------------

    name = resume.get("name", "") or "Your Name"

    story.append(Paragraph(safe_text(name.upper()), name_style))

    contact_items = [
        resume.get("email", ""),
        resume.get("phone", ""),
        resume.get("address", ""),
    ]
    contact_items = [
        safe_text(item.strip())
        for item in contact_items
        if item and str(item).strip()
    ]

    if contact_items:
        story.append(
            Paragraph(" | ".join(contact_items), contact_style)
        )

    links = []

    linkedin = str(resume.get("linkedin", "") or "").strip()
    github = str(resume.get("github", "") or "").strip()

    if linkedin:
        links.append("LinkedIn: " + safe_text(linkedin))

    if github:
        links.append("GitHub: " + safe_text(github))

    if links:
        story.append(Spacer(1, 3))
        story.append(
            Paragraph(" | ".join(links), contact_style)
        )

    story.append(Spacer(1, 16))

    # --------------------------
    # Selected standard sections
    # --------------------------

    section_titles = {
        "summary": "Career Objective",
        "education": "Education",
        "skills": "Technical Skills",
        "projects": "Academic Projects",
        "experience": "Experience",
        "certifications": "Certifications",
        "achievements": "Achievements",
        "languages": "Languages",
    }

    selected_sections = resume.get("selected_sections", [])

    if isinstance(selected_sections, str):
        import json

        try:
            selected_sections = json.loads(selected_sections)
        except (json.JSONDecodeError, TypeError):
            selected_sections = []

    if not isinstance(selected_sections, list):
        selected_sections = []

    for key, title in section_titles.items():
        if key not in selected_sections:
            continue

        content = resume.get(key, "")

        if not content or not str(content).strip():
            continue

        if key == "education":
            add_education_section(story, content)
        else:
            add_section(story, title, content)

    # --------------------------
    # Custom sections
    # --------------------------

    custom_sections = resume.get("custom_sections", [])

    if isinstance(custom_sections, str):
        import json

        try:
            custom_sections = json.loads(custom_sections)
        except (json.JSONDecodeError, TypeError):
            custom_sections = []

    if isinstance(custom_sections, list):
        for custom in custom_sections:
            if not isinstance(custom, dict):
                continue

            title = str(custom.get("title", "") or "").strip()
            content = str(custom.get("content", "") or "").strip()

            if title and content:
                add_section(story, title, content)

    # --------------------------
    # Page number footer
    # --------------------------

    def draw_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawCentredString(
            A4[0] / 2,
            9 * mm,
            f"{doc.page}",
        )
        canvas.restoreState()

    document.build(
        story,
        onFirstPage=draw_page_number,
        onLaterPages=draw_page_number,
    )

    return output_path
