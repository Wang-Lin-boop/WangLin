#!/usr/bin/env python3
"""Build the website CV from the publication data used by the site."""

from __future__ import annotations

import html
import io
import json
from pathlib import Path

from PIL import Image as PILImage, ImageDraw
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
PUBLICATIONS = ROOT / "data" / "publications.json"
PROFILE_IMAGE = ROOT / "images" / "profile.png"
OUROBOROS_IMAGE = ROOT / "images" / "research" / "cv-ouroboros.png"
GEMINIMOL_IMAGE = ROOT / "images" / "research" / "cv-geminimol-screening.png"
PPI_MINER_IMAGE = ROOT / "images" / "research" / "cv-ppi-miner-crbn.png"
OUTPUT = ROOT / "assets" / "Lin_Wang_CV.pdf"

WEBSITE = "https://wang-lin-boop.github.io/WangLin/"
GITHUB = "https://github.com/Wang-Lin-boop"
SCHOLAR = "https://scholar.google.com/citations?user=lFYS_EQAAAAJ"
ORCID = "https://orcid.org/0000-0003-2482-7638"
EMAIL = "Wanglin1102@outlook.com"

INK = colors.HexColor("#172534")
BODY = colors.HexColor("#314657")
MUTED = colors.HexColor("#6B7D8D")
BLUE = colors.HexColor("#145E96")
RULE = colors.HexColor("#CCD8E1")


# Contribution marks are kept from the previous CV. Publication order and
# author order still come from data/publications.json.
AUTHOR_MARKS = {
    "wang2026cocobind": {
        "Shihang Wang": "#",
        "Lin Wang": "#*",
        "Lin Huang": "*",
        "Huanxiang Liu": "*",
        "Yang Zhang": "*",
        "Xiaojun Yao": "*",
    },
    "liu2026integrating": {
        "Yadong Liu": "*",
        "Tianyi Zang": "*",
        "Lin Wang": "*",
        "Yang Zhang": "*",
    },
    "wang2025discovery": {
        "Shi-hang Wang": "#",
        "Yue Zeng": "#",
        "Hao Yang": "#",
        "Si-yuan Tian": "#",
        "Yong-qi Zhou": "#",
        "Lin Wang": "#",
        "Zhao-bing Gao": "*",
        "Fang Bai": "*",
    },
    "liang2025mcr3": {"Lujie Liang": "#", "Yaxin Li": "#", "Lin Wang": "#"},
    "li2025nadph": {
        "Edward RH Walter": "*",
        "Lin Wang": "*",
        "Nicholas J Long": "*",
        "Lijun Jiang": "*",
    },
    "wang2025phenomodel": {
        "Shihang Wang": "#",
        "Qilei Han": "#",
        "Weichen Qin": "#",
        "Lin Wang": "#",
    },
    "liang2023new": {"Lujie Liang": "#", "Lan-Lan Zhong": "#", "Lin Wang": "#"},
    "wang2023deepsa": {"Shihang Wang": "#", "Lin Wang": "#"},
    "han2023discovery": {"Kai Li": "*", "Fang Bai": "*"},
    "mei2023discovery": {"Xingyu Zhang": "*", "Xianglei Zhang": "*"},
    "zhu2023propofol": {"Tao Xu": "*", "Ti-Fei Yuan": "*"},
    "wang2022discovery": {
        "Lin Wang": "#",
        "Yan Wu": "#",
        "Sheng Yao": "#",
        "Huan Ge": "#",
        "Wei Zhu": "*",
    },
    "wang2021probing": {
        "Qian Wang": "#*",
        "Lin Wang": "#",
        "Yumin Zhang": "#",
        "Fang Bai": "*",
    },
}


def register_fonts() -> None:
    font_dir = Path("C:/Windows/Fonts")
    pdfmetrics.registerFont(TTFont("Arial", font_dir / "arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", font_dir / "arialbd.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Italic", font_dir / "ariali.ttf"))
    pdfmetrics.registerFont(TTFont("MicrosoftYaHei", font_dir / "msyh.ttc"))


def circular_profile() -> io.BytesIO:
    with PILImage.open(PROFILE_IMAGE).convert("RGB") as source:
        side = min(source.size)
        left = (source.width - side) // 2
        top = (source.height - side) // 2
        image = source.crop((left, top, left + side, top + side)).resize((640, 640))
        mask = PILImage.new("L", image.size, 0)
        ImageDraw.Draw(mask).ellipse((0, 0, image.width - 1, image.height - 1), fill=255)
        output = io.BytesIO()
        image.putalpha(mask)
        image.save(output, format="PNG")
        output.seek(0)
        return output


def research_image(path: Path, max_width: float, max_height: float) -> Image:
    with PILImage.open(path) as source:
        if "A" in source.getbands():
            bounds = source.getchannel("A").getbbox()
        else:
            bounds = source.getbbox()
        cropped = source.crop(bounds) if bounds else source.copy()
        width, height = cropped.size
        scale = min(max_width / width, max_height / height)
        output = io.BytesIO()
        cropped.save(output, format="PNG")
        output.seek(0)

    image = Image(output, width=width * scale, height=height * scale)
    image.hAlign = "CENTER"
    return image


def link(label: str, url: str) -> str:
    return f'<link href="{html.escape(url, quote=True)}" color="#145E96">{html.escape(label)}</link>'


def styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "name": ParagraphStyle(
            "Name",
            parent=sample["Normal"],
            fontName="Arial-Bold",
            fontSize=23,
            leading=25,
            textColor=INK,
            spaceAfter=1.5 * mm,
        ),
        "chinese_name": ParagraphStyle(
            "ChineseName",
            parent=sample["Normal"],
            fontName="MicrosoftYaHei",
            fontSize=11,
            leading=14,
            textColor=MUTED,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=10.1,
            leading=12,
            textColor=BODY,
            spaceAfter=2.5 * mm,
        ),
        "contact": ParagraphStyle(
            "Contact",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=7.8,
            leading=10,
            textColor=MUTED,
        ),
        "summary": ParagraphStyle(
            "Summary",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=8.6,
            leading=11.5,
            textColor=INK,
            spaceAfter=3 * mm,
        ),
        "section": ParagraphStyle(
            "Section",
            parent=sample["Normal"],
            fontName="Arial-Bold",
            fontSize=12.4,
            leading=14,
            textColor=BLUE,
            spaceBefore=2.2 * mm,
            spaceAfter=1.2 * mm,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=8.25,
            leading=10.5,
            leftIndent=4 * mm,
            firstLineIndent=-3 * mm,
            bulletIndent=0,
            textColor=INK,
            spaceAfter=0.5 * mm,
        ),
        "date": ParagraphStyle(
            "Date",
            parent=sample["Normal"],
            fontName="Arial-Bold",
            fontSize=8.2,
            leading=10,
            textColor=BLUE,
        ),
        "entry_title": ParagraphStyle(
            "EntryTitle",
            parent=sample["Normal"],
            fontName="Arial-Bold",
            fontSize=8.7,
            leading=10.3,
            textColor=INK,
            spaceAfter=0.6 * mm,
        ),
        "entry_body": ParagraphStyle(
            "EntryBody",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=8.05,
            leading=10.2,
            textColor=BODY,
            spaceAfter=0.8 * mm,
        ),
        "entry_links": ParagraphStyle(
            "EntryLinks",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=7.7,
            leading=9.5,
            textColor=BLUE,
        ),
        "research_meta": ParagraphStyle(
            "ResearchMeta",
            parent=sample["Normal"],
            fontName="Arial-Bold",
            fontSize=7.1,
            leading=8.5,
            textColor=BLUE,
            spaceAfter=1.1 * mm,
        ),
        "research_title": ParagraphStyle(
            "ResearchTitle",
            parent=sample["Normal"],
            fontName="Arial-Bold",
            fontSize=10.4,
            leading=12,
            textColor=INK,
            spaceAfter=1.3 * mm,
        ),
        "research_body": ParagraphStyle(
            "ResearchBody",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=7.35,
            leading=9,
            textColor=BODY,
            spaceAfter=1.4 * mm,
        ),
        "research_label": ParagraphStyle(
            "ResearchLabel",
            parent=sample["Normal"],
            fontName="Arial-Bold",
            fontSize=7.1,
            leading=8.5,
            textColor=INK,
            spaceAfter=0.6 * mm,
        ),
        "research_bullet": ParagraphStyle(
            "ResearchBullet",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=7.1,
            leading=8.6,
            leftIndent=3.2 * mm,
            firstLineIndent=-2.4 * mm,
            bulletIndent=0,
            textColor=BODY,
            spaceAfter=0.7 * mm,
        ),
        "research_links": ParagraphStyle(
            "ResearchLinks",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=7,
            leading=8.8,
            textColor=BLUE,
            spaceBefore=1 * mm,
        ),
        "pub_heading": ParagraphStyle(
            "PublicationHeading",
            parent=sample["Normal"],
            fontName="Arial-Bold",
            fontSize=12.8,
            leading=15,
            textColor=BLUE,
            spaceAfter=1 * mm,
        ),
        "pub_note": ParagraphStyle(
            "PublicationNote",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=7.4,
            leading=8.7,
            textColor=MUTED,
            spaceAfter=1.4 * mm,
        ),
        "year": ParagraphStyle(
            "Year",
            parent=sample["Normal"],
            fontName="Arial-Bold",
            fontSize=8.9,
            leading=10.1,
            textColor=INK,
            spaceBefore=1 * mm,
            spaceAfter=0.5 * mm,
        ),
        "pub_title": ParagraphStyle(
            "PublicationTitle",
            parent=sample["Normal"],
            fontName="Arial-Bold",
            fontSize=8.5,
            leading=9.6,
            textColor=INK,
            spaceAfter=0.15 * mm,
        ),
        "pub_authors": ParagraphStyle(
            "PublicationAuthors",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=7.5,
            leading=8.6,
            leftIndent=3 * mm,
            textColor=BODY,
            spaceAfter=0.15 * mm,
        ),
        "pub_venue": ParagraphStyle(
            "PublicationVenue",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=7.35,
            leading=8.45,
            leftIndent=3 * mm,
            textColor=BODY,
            spaceAfter=0.9 * mm,
        ),
    }


def section_heading(text: str, style: ParagraphStyle) -> list:
    heading = Paragraph(text, style)
    heading.keepWithNext = 1
    rule = HRFlowable(width="100%", thickness=0.7, color=RULE, spaceAfter=1.6 * mm)
    rule.keepWithNext = 1
    return [heading, rule]


def year_heading(year: int, style_map: dict[str, ParagraphStyle]) -> list:
    heading = Paragraph(str(year), style_map["year"])
    heading.keepWithNext = 1
    rule = HRFlowable(width="100%", thickness=0.55, color=RULE, spaceAfter=1 * mm)
    rule.keepWithNext = 1
    return [heading, rule]


def dated_entry(
    year: str,
    title: str,
    body: str | None,
    style_map: dict[str, ParagraphStyle],
):
    content = [Paragraph(title, style_map["entry_title"])]
    if body:
        content.append(Paragraph(body, style_map["entry_body"]))
    table = Table(
        [[Paragraph(year, style_map["date"]), content]],
        colWidths=[20 * mm, 151 * mm],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1.2 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2 * mm),
                ("LINEBELOW", (0, 0), (-1, -1), 0.45, RULE),
            ]
        )
    )
    return table


def project_entry(
    year: str,
    title: str,
    description: str,
    links: list[tuple[str, str]],
    style_map: dict[str, ParagraphStyle],
):
    link_markup = " - ".join(link(label, url) for label, url in links)
    content = [
        Paragraph(title, style_map["entry_title"]),
        Paragraph(description, style_map["entry_body"]),
        Paragraph(link_markup, style_map["entry_links"]),
    ]
    table = Table(
        [[Paragraph(year, style_map["date"]), content]],
        colWidths=[20 * mm, 151 * mm],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1.2 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2 * mm),
                ("LINEBELOW", (0, 0), (-1, -1), 0.45, RULE),
            ]
        )
    )
    return table


def research_column(
    image_path: Path,
    meta: str,
    title: str,
    description: str,
    highlights: list[str],
    links: list[tuple[str, str]],
    style_map: dict[str, ParagraphStyle],
) -> list:
    image = research_image(image_path, max_width=48 * mm, max_height=41 * mm)
    image_frame = Table([[image]], colWidths=[51 * mm], rowHeights=[43 * mm])
    image_frame.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    link_markup = " | ".join(link(label, url) for label, url in links)
    content = [
        image_frame,
        Spacer(1, 2 * mm),
        Paragraph(meta, style_map["research_meta"]),
        Paragraph(title, style_map["research_title"]),
        Paragraph(description, style_map["research_body"]),
        Paragraph("Highlights", style_map["research_label"]),
    ]
    content.extend(
        Paragraph(highlight, style_map["research_bullet"], bulletText="-")
        for highlight in highlights
    )
    content.append(Paragraph(link_markup, style_map["research_links"]))
    return content


def selected_research_table(style_map: dict[str, ParagraphStyle]) -> Table:
    columns_newest_first = [
        research_column(
            OUROBOROS_IMAGE,
            "2026 | Representation &amp; generation",
            "Ouroboros",
            "Ouroboros connects molecular prediction and design within one chemically organized representation space. By preserving fingerprint, conformational-space, and pharmacophore relationships, it supports property prediction, similarity-based screening, targeted polypharmacology, and directed molecular optimization.",
            [
                "A shared chemical space closes the gap between predictive modeling and molecular generation, allowing property objectives to guide candidate design",
                "Conformational and pharmacophore organization supports scaffold-level exploration and multi-target design beyond fingerprint similarity alone",
            ],
            [
                ("Paper", "https://doi.org/10.1002/advs.202513556"),
                ("Code", "https://github.com/Wang-Lin-boop/Ouroboros"),
            ],
            style_map,
        ),
        research_column(
            GEMINIMOL_IMAGE,
            "2024 | Molecular representation",
            "GeminiMol",
            "GeminiMol addresses a central limitation of ligand-based discovery: functionally similar molecules can appear unrelated in two-dimensional structure. Learning from conformational-space and pharmacophore relationships supports cross-scaffold prediction, virtual screening, target identification, and scaffold hopping.",
            [
                "Screening 18 million compounds identified the scaffold-distinct GM-10, validated by whole-cell patch clamp against GluN1/GluN3A (IC<sub>50</sub> = 0.98 &#177; 0.13 &#956;M)",
                "First prize in the 2023 Shanghai International Computational Biology Innovation Competition",
            ],
            [
                ("Paper", "https://doi.org/10.1002/advs.202403998"),
                ("Code", "https://github.com/Wang-Lin-boop/GeminiMol"),
                (
                    "Application",
                    "https://doi.org/10.1038/s41401-025-01571-1",
                ),
            ],
            style_map,
        ),
        research_column(
            PPI_MINER_IMAGE,
            "2022 | PPI and molecule glue",
            "PPI-Miner",
            "PPI-Miner addresses a central limitation of sequence-motif searches: proteins can preserve receptor-recognition geometry even when their sequences diverge. It expands interaction-partner discovery across unrelated protein families and supports proteome-scale hypothesis generation for molecular-glue systems. The CRBN case produced a filtered G30 library of 1,739 candidates, 16 previously reported.",
            [
                "Geometry-aware search recovered CRBN-compatible G-loops across unrelated protein families that sequence homology would miss",
                "At least 12 additional candidates in the released library were later supported by compound-dependent CRBN-recruitment assays, with signal lost upon mutation of the predicted G-loop glycine",
            ],
            [
                ("Paper", "https://doi.org/10.1021/acs.jcim.2c01033"),
                ("Code", "https://github.com/Wang-Lin-boop/PPI-Miner"),
                ("CRBN library", "https://bailab.siais.shanghaitech.edu.cn/services/crbn-subslib"),
                ("Science", "https://doi.org/10.1126/science.adt6736"),
            ],
            style_map,
        ),
    ]
    columns_chronological = list(reversed(columns_newest_first))
    table = Table([columns_chronological], colWidths=[57 * mm] * 3, rowHeights=[118 * mm])
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("LINEBEFORE", (1, 0), (2, 0), 0.55, RULE),
            ]
        )
    )
    return table


def format_authors(publication: dict) -> str:
    marks = AUTHOR_MARKS.get(publication["id"], {})
    authors = publication.get("authors", [])
    formatted = []
    for index, author in enumerate(authors):
        if author == "others":
            formatted.append("et al.")
            continue
        name = html.escape(author)
        marker = marks.get(author, "")
        if marker:
            name += f"<super>{html.escape(marker)}</super>"
        if author == "Lin Wang" and (index == 0 or "#" in marker or "*" in marker):
            name = f'<font name="Arial-Bold" color="#000000">{name}</font>'
        formatted.append(name)
    return ", ".join(formatted)


def format_venue(publication: dict) -> str:
    pieces = [f"<i>{html.escape(publication.get('venue') or 'Publication')}</i>"]
    volume = publication.get("volume")
    issue = publication.get("issue")
    pages = publication.get("pages")
    if volume:
        volume_text = f"vol. {html.escape(str(volume))}"
        if issue:
            volume_text += f"({html.escape(str(issue))})"
        pieces.append(volume_text)
    if pages:
        pieces.append(f"p. {html.escape(str(pages))}")
    if publication.get("type") == "book chapter":
        pieces.append("book chapter")
    pieces.append(str(publication["year"]))
    label = "DOI" if publication.get("doi") else "Google Scholar"
    pieces.append(link(label, publication["url"]))
    return ", ".join(pieces[:-1]) + " - " + pieces[-1]


def publication_flowables(publication: dict, style_map: dict[str, ParagraphStyle]) -> list:
    return [
        Paragraph(html.escape(publication["title"]), style_map["pub_title"]),
        Paragraph(format_authors(publication), style_map["pub_authors"]),
        Paragraph(format_venue(publication), style_map["pub_venue"]),
    ]


def publication_entry(publication: dict, style_map: dict[str, ParagraphStyle]):
    return KeepTogether(publication_flowables(publication, style_map))


def footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setFont("Arial", 6.6)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 10 * mm, "Lin Wang - Computational Molecular Discovery")
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {document.page}")
    canvas.restoreState()


def build() -> None:
    register_fonts()
    style_map = styles()
    publications = json.loads(PUBLICATIONS.read_text(encoding="utf-8"))

    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=19 * mm,
        leftMargin=19 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="Lin Wang - Academic CV",
        author="Lin Wang",
        subject="Computational molecular representation and drug discovery",
    )

    name_line = Table(
        [[Paragraph("Lin Wang", style_map["name"]), Paragraph("王林", style_map["chinese_name"])]],
        colWidths=[43 * mm, 25 * mm],
        hAlign="LEFT",
    )
    name_line.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    identity = [
        name_line,
        Paragraph("Postdoctoral Researcher | Computational Molecular Discovery", style_map["subtitle"]),
        Paragraph(
            "Suzhou, China | "
            + link(EMAIL, f"mailto:{EMAIL}")
            + " | "
            + link("Website", WEBSITE)
            + " | "
            + link("GitHub", GITHUB)
            + " | "
            + link("Google Scholar", SCHOLAR)
            + " | "
            + link("ORCID", ORCID),
            style_map["contact"],
        ),
    ]
    portrait_buffer = circular_profile()
    portrait = Image(portrait_buffer, width=27 * mm, height=27 * mm)
    header = Table([[identity, portrait]], colWidths=[144 * mm, 27 * mm], hAlign="LEFT")
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    story = [
        header,
        Spacer(1, 3 * mm),
        HRFlowable(width="100%", thickness=1.2, color=BLUE, spaceAfter=1.8 * mm),
        Paragraph(
            "I develop computational methods that integrate chemical priors into molecular representation learning and generative drug design. My research spans AI-driven drug discovery and protein–ligand and protein–protein interaction modeling, with emerging directions in phenotype-based and polypharmacology drug design. My latest work, Ouroboros, advances this broader program through a molecular foundation model that learns chemically informed representations from conformational-space and pharmacophore similarities for molecular property prediction and generation.",
            style_map["summary"],
        ),
        *section_heading("Research Focus", style_map["section"]),
        Paragraph("Molecular representation and generation foundation models for medicinal chemistry", style_map["bullet"], bulletText="•"),
        Paragraph("Conformational-space- and pharmacophore-aware molecular representations", style_map["bullet"], bulletText="•"),
        Paragraph("Protein-ligand and protein-protein interaction modeling", style_map["bullet"], bulletText="•"),
        Paragraph("Phenotype-based and polypharmacology drug design", style_map["bullet"], bulletText="•"),
        Spacer(1, 1 * mm),
        *section_heading("Education and Experience", style_map["section"]),
        dated_entry(
            "Current",
            "Postdoctoral Researcher",
            "Institute of Systems Medicine, Chinese Academy of Medical Sciences, Suzhou, China.",
            style_map,
        ),
        dated_entry(
            "2019-2024",
            "Ph.D., ShanghaiTech University",
            None,
            style_map,
        ),
        dated_entry(
            "2019",
            "B.S. in Life Science, Northeast Agricultural University",
            None,
            style_map,
        ),
        *section_heading("Selected Research", style_map["section"]),
        selected_research_table(style_map),
        PageBreak(),
    ]

    story.extend(section_heading("Publications", style_map["pub_heading"]))
    publication_note = Paragraph(
        "# = co-first author; * = co-corresponding author.",
        style_map["pub_note"],
    )
    publication_note.keepWithNext = 1
    story.append(publication_note)

    previous_year = None
    for publication in publications:
        if publication["id"] == "mei2023discovery":
            story.append(PageBreak())
            story.extend(year_heading("2023 (continued)", style_map))
            previous_year = publication["year"]
        if publication["year"] != previous_year:
            story.append(
                KeepTogether(
                    year_heading(publication["year"], style_map)
                    + publication_flowables(publication, style_map)
                )
            )
            previous_year = publication["year"]
        else:
            story.append(publication_entry(publication, style_map))

    document.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Wrote {OUTPUT} with {len(publications)} publications")


if __name__ == "__main__":
    build()
