#!/usr/bin/env python3
"""Build the academic English CV (cv/Lin_Wang_CV_English.pdf) from data/publications.json."""

from __future__ import annotations

import html
import io
import json
from pathlib import Path

from PIL import Image as PILImage, ImageDraw
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
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
OUTPUT = ROOT / "cv" / "Lin_Wang_CV_English.pdf"

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
    "zhou2026proteinconformers": {
        "Yihang Zhou": "#",
        "Chen Wei": "#",
        "Yang Li": "*",
        "Lin Wang": "*",
        "Yang Zhang": "*",
    },
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


def _first_existing(candidates: list[Path]) -> Path:
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"None of the candidate font files exist: {candidates}")


def _build_noto_cjk_ttf(ttc_path: Path, index: int, out_ttf: Path) -> bool:
    if out_ttf.is_file() and out_ttf.stat().st_size > 50_000:
        return True
    try:
        from fontTools.pens.cu2quPen import Cu2QuPen
        from fontTools.pens.ttGlyphPen import TTGlyphPen
        from fontTools.subset import Options, Subsetter
        from fontTools.ttLib import TTCollection, newTable
    except Exception:
        return False

    gb_chars = []
    for lead in range(0xB0, 0xF8):
        for trail in range(0xA1, 0xFF):
            try:
                gb_chars.append(bytes([lead, trail]).decode("gb2312"))
            except UnicodeDecodeError:
                pass
    extra = (
        "".join(chr(c) for c in range(32, 127))
        + "μ±–—•·×÷αβγδεκλνπρστφχψωΔΩ（）《》〈〉【】「」『』，。；：、？！“”‘’…—～｜"
    )
    charset = "".join(gb_chars) + extra

    font = TTCollection(str(ttc_path)).fonts[index]
    options = Options()
    options.desubroutinize = True
    options.drop_tables += ["VORG", "vhea", "vmtx", "BASE", "GPOS", "GSUB", "GDEF"]
    subsetter = Subsetter(options=options)
    subsetter.populate(text=charset)
    subsetter.subset(font)

    glyph_order = font.getGlyphOrder()
    glyph_set = font.getGlyphSet()
    glyf = newTable("glyf")
    glyf.glyphs = {}
    glyf.glyphOrder = glyph_order
    for glyph_name in glyph_order:
        pen = TTGlyphPen(glyph_set)
        cpen = Cu2QuPen(pen, max_err=1.0, reverse_direction=True)
        glyph_set[glyph_name].draw(cpen)
        glyf.glyphs[glyph_name] = pen.glyph()

    del font["CFF "]
    font.sfntVersion = "\x00\x01\x00\x00"
    font["loca"] = newTable("loca")
    font["glyf"] = glyf
    maxp = newTable("maxp")
    maxp.tableVersion = 0x00010000
    maxp.maxZones = 1
    maxp.maxTwilightPoints = 0
    maxp.maxStorage = 0
    maxp.maxFunctionDefs = 0
    maxp.maxInstructionDefs = 0
    maxp.maxStackElements = 0
    maxp.maxSizeOfInstructions = 0
    maxp.maxComponentElements = 0
    font["maxp"] = maxp
    font["post"].formatType = 3.0
    out_ttf.parent.mkdir(parents=True, exist_ok=True)
    font.save(str(out_ttf))
    return True


def register_fonts() -> tuple[str, str]:
    """Register Latin and Chinese Regular/Bold fonts across Windows, macOS, and Linux."""
    regular = _first_existing(
        [
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
            Path("/Library/Fonts/Arial.ttf"),
            Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]
    )
    bold = _first_existing(
        [
            Path("C:/Windows/Fonts/arialbd.ttf"),
            Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
            Path("/Library/Fonts/Arial Bold.ttf"),
            Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ]
    )
    italic = _first_existing(
        [
            Path("C:/Windows/Fonts/ariali.ttf"),
            Path("/System/Library/Fonts/Supplemental/Arial Italic.ttf"),
            Path("/Library/Fonts/Arial Italic.ttf"),
            Path("/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]
    )
    pdfmetrics.registerFont(TTFont("Arial", str(regular)))
    pdfmetrics.registerFont(TTFont("Arial-Bold", str(bold)))
    pdfmetrics.registerFont(TTFont("Arial-Italic", str(italic)))
    pdfmetrics.registerFontFamily(
        "Arial",
        normal="Arial",
        bold="Arial-Bold",
        italic="Arial-Italic",
        boldItalic="Arial-Bold",
    )

    win_reg = Path("C:/Windows/Fonts/msyh.ttc")
    win_bd = Path("C:/Windows/Fonts/msyhbd.ttc")
    if win_reg.is_file():
        pdfmetrics.registerFont(TTFont("MicrosoftYaHei", str(win_reg)))
        bd_path = win_bd if win_bd.is_file() else win_reg
        pdfmetrics.registerFont(TTFont("MicrosoftYaHei-Bold", str(bd_path)))
        pdfmetrics.registerFontFamily(
            "MicrosoftYaHei",
            normal="MicrosoftYaHei",
            bold="MicrosoftYaHei-Bold",
            italic="MicrosoftYaHei",
            boldItalic="MicrosoftYaHei-Bold",
        )
        return "MicrosoftYaHei", "MicrosoftYaHei-Bold"

    noto_reg = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
    noto_bd = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
    cache_dir = Path("/tmp/cv_fonts")
    reg_ttf = cache_dir / "NotoSansCJKsc-Regular.ttf"
    bd_ttf = cache_dir / "NotoSansCJKsc-Bold.ttf"
    if (
        noto_reg.is_file()
        and noto_bd.is_file()
        and _build_noto_cjk_ttf(noto_reg, 2, reg_ttf)
        and _build_noto_cjk_ttf(noto_bd, 2, bd_ttf)
    ):
        pdfmetrics.registerFont(TTFont("MicrosoftYaHei", str(reg_ttf)))
        pdfmetrics.registerFont(TTFont("MicrosoftYaHei-Bold", str(bd_ttf)))
        pdfmetrics.registerFontFamily(
            "MicrosoftYaHei",
            normal="MicrosoftYaHei",
            bold="MicrosoftYaHei-Bold",
            italic="MicrosoftYaHei",
            boldItalic="MicrosoftYaHei-Bold",
        )
        return "MicrosoftYaHei", "MicrosoftYaHei-Bold"

    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    return "STSong-Light", "STSong-Light"


def circular_profile(path: Path = PROFILE_IMAGE) -> io.BytesIO:
    with PILImage.open(path).convert("RGB") as source:
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


def styles(cjk_font: str) -> dict[str, ParagraphStyle]:
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
            fontName=cjk_font,
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
            spaceAfter=2.2 * mm,
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
            fontSize=8.5,
            leading=11.4,
            textColor=INK,
            spaceAfter=2.2 * mm,
        ),
        "section": ParagraphStyle(
            "Section",
            parent=sample["Normal"],
            fontName="Arial-Bold",
            fontSize=11.8,
            leading=13.5,
            textColor=BLUE,
            spaceBefore=1.6 * mm,
            spaceAfter=1.0 * mm,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=8.0,
            leading=10.4,
            leftIndent=3.8 * mm,
            firstLineIndent=-2.8 * mm,
            bulletIndent=0,
            textColor=INK,
            spaceAfter=0.75 * mm,
        ),
        "funding": ParagraphStyle(
            "Funding",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=7.65,
            leading=9.4,
            leftIndent=4 * mm,
            firstLineIndent=-3 * mm,
            bulletIndent=0,
            textColor=INK,
            spaceAfter=0.25 * mm,
        ),
        "date": ParagraphStyle(
            "Date",
            parent=sample["Normal"],
            fontName="Arial-Bold",
            fontSize=7.8,
            leading=9.6,
            textColor=BLUE,
        ),
        "entry_title": ParagraphStyle(
            "EntryTitle",
            parent=sample["Normal"],
            fontName="Arial-Bold",
            fontSize=8.3,
            leading=9.8,
            textColor=INK,
            spaceAfter=0.35 * mm,
        ),
        "entry_body": ParagraphStyle(
            "EntryBody",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=7.55,
            leading=9.3,
            textColor=BODY,
            spaceAfter=0.2 * mm,
        ),
        "entry_advisor": ParagraphStyle(
            "EntryAdvisor",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=7.35,
            leading=9.0,
            textColor=MUTED,
        ),
        "research_meta": ParagraphStyle(
            "ResearchMeta",
            parent=sample["Normal"],
            fontName="Arial-Bold",
            fontSize=7.1,
            leading=8.5,
            textColor=BLUE,
            spaceAfter=1.0 * mm,
        ),
        "research_title": ParagraphStyle(
            "ResearchTitle",
            parent=sample["Normal"],
            fontName="Arial-Bold",
            fontSize=10.3,
            leading=11.8,
            textColor=INK,
            spaceAfter=1.2 * mm,
        ),
        "research_body": ParagraphStyle(
            "ResearchBody",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=7.3,
            leading=8.9,
            textColor=BODY,
            spaceAfter=1.3 * mm,
        ),
        "research_label": ParagraphStyle(
            "ResearchLabel",
            parent=sample["Normal"],
            fontName="Arial-Bold",
            fontSize=7.1,
            leading=8.5,
            textColor=INK,
            spaceAfter=0.55 * mm,
        ),
        "research_bullet": ParagraphStyle(
            "ResearchBullet",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=7.05,
            leading=8.5,
            leftIndent=3.2 * mm,
            firstLineIndent=-2.4 * mm,
            bulletIndent=0,
            textColor=BODY,
            spaceAfter=0.65 * mm,
        ),
        "research_links": ParagraphStyle(
            "ResearchLinks",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=7,
            leading=8.7,
            textColor=BLUE,
            spaceBefore=0.9 * mm,
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
            fontSize=8.45,
            leading=9.6,
            textColor=INK,
            spaceAfter=0.5 * mm,
        ),
        "pub_authors": ParagraphStyle(
            "PublicationAuthors",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=7.45,
            leading=8.8,
            leftIndent=3 * mm,
            textColor=BODY,
            spaceAfter=0.15 * mm,
        ),
        "pub_venue": ParagraphStyle(
            "PublicationVenue",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=7.3,
            leading=8.4,
            leftIndent=3 * mm,
            textColor=BODY,
            spaceAfter=0.85 * mm,
        ),
    }


def section_heading(text: str, style: ParagraphStyle, width: str = "100%") -> list:
    heading = Paragraph(text, style)
    heading.keepWithNext = 1
    rule = HRFlowable(width=width, thickness=0.7, color=RULE, spaceAfter=1.4 * mm)
    rule.keepWithNext = 1
    return [heading, rule]


def year_heading(year: int | str, style_map: dict[str, ParagraphStyle]) -> list:
    heading = Paragraph(str(year), style_map["year"])
    heading.keepWithNext = 1
    rule = HRFlowable(width="100%", thickness=0.55, color=RULE, spaceAfter=1 * mm)
    rule.keepWithNext = 1
    return [heading, rule]


def compact_edu_entry(
    year: str,
    title: str,
    org: str | None,
    advisor: str | None,
    style_map: dict[str, ParagraphStyle],
    is_last: bool = False,
) -> Table:
    content = [Paragraph(title, style_map["entry_title"])]
    if org:
        content.append(Paragraph(org, style_map["entry_body"]))
    if advisor:
        content.append(Paragraph(advisor, style_map["entry_advisor"]))
    table = Table(
        [[Paragraph(year, style_map["date"]), content]],
        colWidths=[16.5 * mm, 74.5 * mm],
        hAlign="LEFT",
    )
    rules = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1.0 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.0 * mm),
    ]
    if not is_last:
        rules.append(("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE))
    table.setStyle(TableStyle(rules))
    return table


def focus_and_education_band(style_map: dict[str, ParagraphStyle]) -> Table:
    left_col = [
        *section_heading("Research Focus", style_map["section"]),
        Paragraph(
            "Molecular representation and generation foundation models for medicinal chemistry",
            style_map["bullet"],
            bulletText="•",
        ),
        Paragraph(
            "Conformational-space- and pharmacophore-aware molecular representations",
            style_map["bullet"],
            bulletText="•",
        ),
        Paragraph(
            "Protein–ligand, protein–protein, and RNA–ligand interaction modeling",
            style_map["bullet"],
            bulletText="•",
        ),
        Paragraph(
            "Phenotype-based and polypharmacology drug design",
            style_map["bullet"],
            bulletText="•",
        ),
        Paragraph(
            "Cyclic-peptide conformational space search and molecular design",
            style_map["bullet"],
            bulletText="•",
        ),
    ]
    right_col = [
        *section_heading("Education and Experience", style_map["section"]),
        compact_edu_entry(
            "Current",
            "Postdoctoral Researcher",
            "Institute of Systems Medicine, CAMS, Suzhou, China",
            "Supervisor: Prof. Yang Zhang (National Univ. of Singapore)",
            style_map,
        ),
        compact_edu_entry(
            "2019–2024",
            "Ph.D. in Computer-Aided Drug Design",
            "School of Life Science and Technology, ShanghaiTech Univ.",
            "Advisor: Prof. Fang Bai (SIAIS)",
            style_map,
        ),
        compact_edu_entry(
            "2019",
            "B.S. in Biology",
            "Northeast Agricultural University",
            None,
            style_map,
            is_last=True,
        ),
    ]
    band = Table([[left_col, "", right_col]], colWidths=[74 * mm, 6 * mm, 91 * mm], hAlign="LEFT")
    band.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return band


def research_column(
    image_path: Path,
    meta: str,
    title: str,
    description: str,
    highlights: list[str],
    links: list[tuple[str, str]],
    style_map: dict[str, ParagraphStyle],
) -> list:
    image = research_image(image_path, max_width=48 * mm, max_height=40 * mm)
    image_frame = Table([[image]], colWidths=[51 * mm], rowHeights=[42 * mm])
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
        Spacer(1, 1.8 * mm),
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
                ("Advanced Science", "https://doi.org/10.1002/advs.202513556"),
                ("Commun. Chem.", "https://doi.org/10.1038/s42004-026-02115-2"),
                ("J. Med. Chem.", "https://doi.org/10.1021/acs.jmedchem.6c00902"),
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
                "First prize, inaugural Shanghai International Computational Biology Innovation Competition (2023 edition, 2024 award)",
            ],
            [
                ("Advanced Science", "https://doi.org/10.1002/advs.202403998"),
                (
                    "Acta Pharmacol. Sin.",
                    "https://doi.org/10.1038/s41401-025-01571-1",
                ),
                ("Code", "https://github.com/Wang-Lin-boop/GeminiMol"),
            ],
            style_map,
        ),
        research_column(
            PPI_MINER_IMAGE,
            "2022 | PPI and molecule glue",
            "PPI-Miner",
            "PPI-Miner searches receptor-compatible backbone motifs across sequence-divergent proteins, expanding interaction-partner discovery beyond sequence homology. Applied to CRBN, it produced a filtered G30 library of 1,739 candidate substrates.",
            [
                "Geometry-aware search recovered CRBN-compatible G-loops across unrelated protein families that sequence homology would miss",
                "At least 12 additional candidates in the released library were later supported by compound-dependent CRBN-recruitment assays, with signal lost upon mutation of the predicted G-loop glycine",
            ],
            [
                ("JCIM", "https://doi.org/10.1021/acs.jcim.2c01033"),
                ("CRBN library", "https://bailab.siais.shanghaitech.edu.cn/services/crbn-subslib"),
                ("Code", "https://github.com/Wang-Lin-boop/PPI-Miner"),
            ],
            style_map,
        ),
    ]
    columns_chronological = list(reversed(columns_newest_first))
    table = Table([columns_chronological], colWidths=[57 * mm] * 3)
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
            name += f'<super rise="2" size="5.2">{html.escape(marker)}</super>'
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
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    cjk_font, _ = register_fonts()
    style_map = styles(cjk_font)
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
    portrait = Image(portrait_buffer, width=26 * mm, height=26 * mm)
    header = Table([[identity, portrait]], colWidths=[145 * mm, 26 * mm], hAlign="LEFT")
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

    # Summary must stay synced with index.html (.hero-statement) and data/i18n/en.json (home.hero.statement).
    story = [
        header,
        Spacer(1, 2.5 * mm),
        HRFlowable(width="100%", thickness=1.2, color=BLUE, spaceAfter=1.8 * mm),
        Paragraph(
            "I develop machine-learning methods that bring chemical knowledge — conformations, pharmacophores, and molecular interactions — into molecular representation and drug design. My work spans small-molecule discovery and protein–ligand, protein–protein, and RNA–ligand interaction modeling, with emerging directions in phenotype-based and multi-target drug design.",
            style_map["summary"],
        ),
        focus_and_education_band(style_map),
        Spacer(1, 0.8 * mm),
        *section_heading("Funding and Honors", style_map["section"]),
        Paragraph(
            "National Natural Science Foundation of China, Young Scientists Fund (Category C), Grant No. T2600798",
            style_map["funding"],
            bulletText="•",
        ),
        Paragraph(
            "Fundamental Research Funds for the Central Universities, Peking Union Medical College, Grant No. 3332025054",
            style_map["funding"],
            bulletText="•",
        ),
        Paragraph(
            "First prize, inaugural Shanghai International Computational Biology Innovation Competition (2023 edition, GeminiMol team), 2024",
            style_map["funding"],
            bulletText="•",
        ),
        Spacer(1, 1.0 * mm),
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
