#!/usr/bin/env python3
"""Build the job-oriented Chinese CV from data/publications.json.

Always writes the public version without private fields to:
  cv/Lin_Wang_CV_Chinese.pdf

When cv/private/profile.json exists (and --public-only is not passed), also writes:
  cv/private/Lin_Wang_CV_Chinese_full.pdf
"""

from __future__ import annotations

import argparse
import html
import io
import json
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
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

from build_cv import (
    BLUE,
    BODY,
    EMAIL,
    GEMINIMOL_IMAGE,
    GITHUB,
    INK,
    MUTED,
    ORCID,
    OUROBOROS_IMAGE,
    PPI_MINER_IMAGE,
    PROFILE_IMAGE,
    PUBLICATIONS,
    ROOT,
    RULE,
    SCHOLAR,
    WEBSITE,
    format_authors,
    format_venue,
    link,
    register_fonts,
    research_image,
    section_heading,
)


PUBLIC_OUTPUT = ROOT / "cv" / "Lin_Wang_CV_Chinese.pdf"
PRIVATE_DIR = ROOT / "cv" / "private"
PRIVATE_JSON = PRIVATE_DIR / "profile.json"
PRIVATE_OUTPUT = PRIVATE_DIR / "Lin_Wang_CV_Chinese_full.pdf"


ORIGINAL_ALGO_WORKS: list[tuple[str, str]] = [
    ("wang2026learned", "第一作者，中科院1区，IF=15.6"),
    ("wang2024conformational", "第一作者，中科院1区，IF=15.6"),
    ("wang2022ppi", "第一作者，中科院2区，IF=6.9"),
    ("wang2026small", "第一作者，书籍章节"),
    ("wang2026cocobind", "共同一作、共同通讯，中科院1区，IF=7.6"),
    ("liu2026integrating", "共同通讯，中科院1区，IF=7.1"),
    ("zhou2026proteinconformers", "共同通讯，会议论文"),
    ("wang2025phenomodel", "共同一作，中科院1区，IF=16.9"),
    ("wang2023deepsa", "共同一作，中科院2区，IF=10.0"),
]

APPLICATION_WORKS: list[tuple[str, str]] = [
    ("wang2022discovery", "共同一作，中科院2区，IF=10.8"),
    ("li2025nadph", "共同通讯，中科院1区，IF=9.9"),
    ("liang2025mcr3", "共同一作，中科院1区，IF=11.1"),
    ("wang2025discovery", "共同一作，中科院2区，IF=10.8"),
    ("liang2023new", "共同一作，中科院1区，IF=8.1"),
    ("wang2021probing", "共同一作，中科院1区，IF=7.6"),
]


def rectangular_portrait(path: Path, target_ratio: float = 5 / 7) -> io.BytesIO:
    with PILImage.open(path).convert("RGB") as source:
        width, height = source.size
        current_ratio = width / height
        if current_ratio > target_ratio:
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            cropped = source.crop((left, 0, left + new_width, height))
        else:
            new_height = int(width / target_ratio)
            top = max(0, int((height - new_height) * 0.25))
            cropped = source.crop((0, top, width, top + new_height))
        resized = cropped.resize((600, 840))
        output = io.BytesIO()
        resized.save(output, format="PNG")
        output.seek(0)
        return output


def zh_styles(cjk_reg: str, cjk_bold: str) -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "name": ParagraphStyle(
            "ZhName",
            parent=sample["Normal"],
            fontName=cjk_bold,
            fontSize=22,
            leading=25,
            textColor=INK,
        ),
        "en_name": ParagraphStyle(
            "EnName",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=11.5,
            leading=15,
            textColor=MUTED,
        ),
        "subtitle": ParagraphStyle(
            "ZhSubtitle",
            parent=sample["Normal"],
            fontName=cjk_reg,
            fontSize=10.2,
            leading=13.5,
            textColor=BODY,
            spaceBefore=1.2 * mm,
            spaceAfter=1.8 * mm,
        ),
        "contact": ParagraphStyle(
            "ZhContact",
            parent=sample["Normal"],
            fontName=cjk_reg,
            fontSize=7.9,
            leading=10.8,
            textColor=MUTED,
        ),
        "summary": ParagraphStyle(
            "ZhSummary",
            parent=sample["Normal"],
            fontName=cjk_reg,
            fontSize=8.5,
            leading=12.4,
            wordWrap="CJK",
            textColor=INK,
            spaceAfter=2.2 * mm,
        ),
        "section": ParagraphStyle(
            "ZhSection",
            parent=sample["Normal"],
            fontName=cjk_bold,
            fontSize=11.5,
            leading=14,
            textColor=BLUE,
            spaceBefore=1.5 * mm,
            spaceAfter=1.0 * mm,
        ),
        "bullet": ParagraphStyle(
            "ZhBullet",
            parent=sample["Normal"],
            fontName=cjk_reg,
            fontSize=8.1,
            leading=11.8,
            wordWrap="CJK",
            leftIndent=3.6 * mm,
            firstLineIndent=-2.8 * mm,
            bulletIndent=0,
            textColor=INK,
            spaceAfter=0.6 * mm,
        ),
        "funding": ParagraphStyle(
            "ZhFunding",
            parent=sample["Normal"],
            fontName=cjk_reg,
            fontSize=7.9,
            leading=10.6,
            wordWrap="CJK",
            leftIndent=3.6 * mm,
            firstLineIndent=-2.8 * mm,
            bulletIndent=0,
            textColor=INK,
            spaceAfter=0.25 * mm,
        ),
        "date": ParagraphStyle(
            "ZhDate",
            parent=sample["Normal"],
            fontName=cjk_bold,
            fontSize=7.9,
            leading=10.4,
            textColor=BLUE,
        ),
        "entry_title": ParagraphStyle(
            "ZhEntryTitle",
            parent=sample["Normal"],
            fontName=cjk_bold,
            fontSize=8.4,
            leading=10.8,
            textColor=INK,
            spaceAfter=0.3 * mm,
        ),
        "entry_body": ParagraphStyle(
            "ZhEntryBody",
            parent=sample["Normal"],
            fontName=cjk_reg,
            fontSize=7.7,
            leading=10.2,
            textColor=BODY,
            spaceAfter=0.2 * mm,
        ),
        "entry_advisor": ParagraphStyle(
            "ZhEntryAdvisor",
            parent=sample["Normal"],
            fontName=cjk_reg,
            fontSize=7.5,
            leading=9.8,
            textColor=MUTED,
        ),
        "research_meta": ParagraphStyle(
            "ZhResearchMeta",
            parent=sample["Normal"],
            fontName=cjk_bold,
            fontSize=7.3,
            leading=9.2,
            textColor=BLUE,
            spaceAfter=0.8 * mm,
        ),
        "research_title": ParagraphStyle(
            "ZhResearchTitle",
            parent=sample["Normal"],
            fontName="Arial-Bold",
            fontSize=10.5,
            leading=12,
            textColor=INK,
            spaceAfter=1.4 * mm,
        ),
        "research_body": ParagraphStyle(
            "ZhResearchBody",
            parent=sample["Normal"],
            fontName=cjk_reg,
            fontSize=7.55,
            leading=10.5,
            wordWrap="CJK",
            textColor=BODY,
            spaceAfter=1.4 * mm,
        ),
        "research_label": ParagraphStyle(
            "ZhResearchLabel",
            parent=sample["Normal"],
            fontName=cjk_bold,
            fontSize=7.4,
            leading=9.2,
            textColor=INK,
            spaceAfter=0.6 * mm,
        ),
        "research_bullet": ParagraphStyle(
            "ZhResearchBullet",
            parent=sample["Normal"],
            fontName=cjk_reg,
            fontSize=7.25,
            leading=9.8,
            wordWrap="CJK",
            leftIndent=3.2 * mm,
            firstLineIndent=-2.4 * mm,
            bulletIndent=0,
            textColor=BODY,
            spaceAfter=0.8 * mm,
        ),
        "research_links": ParagraphStyle(
            "ZhResearchLinks",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=7.0,
            leading=8.8,
            textColor=BLUE,
            spaceBefore=1.0 * mm,
        ),
        "pub_heading": ParagraphStyle(
            "ZhPubHeading",
            parent=sample["Normal"],
            fontName=cjk_bold,
            fontSize=13.2,
            leading=16,
            textColor=BLUE,
            spaceAfter=1.0 * mm,
        ),
        "pub_note": ParagraphStyle(
            "ZhPubNote",
            parent=sample["Normal"],
            fontName=cjk_reg,
            fontSize=7.6,
            leading=9.6,
            textColor=MUTED,
            spaceAfter=1.6 * mm,
        ),
        "group_heading": ParagraphStyle(
            "ZhGroupHeading",
            parent=sample["Normal"],
            fontName=cjk_bold,
            fontSize=10.0,
            leading=12.4,
            textColor=BLUE,
            spaceBefore=1.4 * mm,
            spaceAfter=0.6 * mm,
        ),
        "pub_title": ParagraphStyle(
            "ZhPubTitle",
            parent=sample["Normal"],
            fontName="Arial-Bold",
            fontSize=8.35,
            leading=10.0,
            textColor=INK,
            spaceAfter=0.55 * mm,
        ),
        "pub_authors": ParagraphStyle(
            "ZhPubAuthors",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=7.35,
            leading=8.7,
            textColor=BODY,
            spaceAfter=0.15 * mm,
        ),
        "pub_venue": ParagraphStyle(
            "ZhPubVenue",
            parent=sample["Normal"],
            fontName="Arial",
            fontSize=7.25,
            leading=8.5,
            textColor=BODY,
            spaceAfter=1.15 * mm,
        ),
    }


def zh_edu_entry(
    period: str,
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
        [[Paragraph(period, style_map["date"]), content]],
        colWidths=[18 * mm, 69 * mm],
        hAlign="LEFT",
    )
    rules = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0.9 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0.9 * mm),
    ]
    if not is_last:
        rules.append(("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE))
    table.setStyle(TableStyle(rules))
    return table


def zh_focus_and_edu_band(style_map: dict[str, ParagraphStyle]) -> Table:
    left_col = [
        *section_heading("研究方向", style_map["section"]),
        Paragraph("面向药物化学的分子表征与生成基础模型", style_map["bullet"], bulletText="-"),
        Paragraph("融合构象空间与药效团信息的分子表征", style_map["bullet"], bulletText="-"),
        Paragraph("蛋白-配体、蛋白-蛋白与 RNA-配体相互作用建模", style_map["bullet"], bulletText="-"),
        Paragraph("基于表型和多靶点药理学的药物设计", style_map["bullet"], bulletText="-"),
        Paragraph("环肽构象空间搜索算法及其分子设计", style_map["bullet"], bulletText="-"),
    ]
    right_col = [
        *section_heading("教育与工作经历", style_map["section"]),
        zh_edu_entry(
            "目前",
            "博士后研究员",
            "中国医学科学院系统医学研究所，中国苏州",
            "博士后导师：新加坡国立大学 张阳教授",
            style_map,
        ),
        zh_edu_entry(
            "2019-2024",
            "博士（计算机辅助药物设计）",
            "上海科技大学生命科学与技术学院",
            "博士导师：免疫化学研究所 白芳教授",
            style_map,
        ),
        zh_edu_entry(
            "2019",
            "理学学士（生物学），东北农业大学",
            None,
            None,
            style_map,
            is_last=True,
        ),
    ]
    band = Table([[left_col, "", right_col]], colWidths=[77 * mm, 7 * mm, 87 * mm], hAlign="LEFT")
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


def zh_research_column(
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
        Paragraph(meta, style_map["research_meta"]),
        Paragraph(title, style_map["research_title"]),
        image_frame,
        Spacer(1, 1.8 * mm),
        Paragraph(description, style_map["research_body"]),
        Paragraph("研究亮点", style_map["research_label"]),
    ]
    content.extend(
        Paragraph(highlight, style_map["research_bullet"], bulletText="-")
        for highlight in highlights
    )
    content.append(Paragraph(link_markup, style_map["research_links"]))
    return content


def zh_selected_research_table(style_map: dict[str, ParagraphStyle], cjk_bold: str) -> Table:
    award_line = (
        f'<font name="{cjk_bold}" color="#172534">'
        "首届上海国际计算生物学创新大赛第一名（2023 届赛事，2024 年颁奖）。"
        "</font>"
    )
    columns = [
        zh_research_column(
            PPI_MINER_IMAGE,
            "2022 | 蛋白互作与分子胶",
            "PPI-Miner",
            "PPI-Miner 可跨越序列差异检索与受体相容的主链结构基序，突破序列同源性对互作伙伴发现的限制。<br/>用于 CRBN 时，构建经筛选的 G30 库，含 1,739 个候选底物。",
            [
                "跨蛋白家族识别序列同源搜索难以发现的 CRBN 相容 G-loop。",
                "公开库中另有至少 12 个候选后来获化合物依赖的 CRBN 招募实验支持；预测 G-loop 中甘氨酸突变后，招募信号消失。",
            ],
            [
                ("JCIM", "https://doi.org/10.1021/acs.jcim.2c01033"),
                ("CRBN library", "https://bailab.siais.shanghaitech.edu.cn/services/crbn-subslib"),
                ("Code", "https://github.com/Wang-Lin-boop/PPI-Miner"),
            ],
            style_map,
        ),
        zh_research_column(
            GEMINIMOL_IMAGE,
            "2024 | 分子表征",
            "GeminiMol",
            "GeminiMol 突破基于配体的药物发现中的关键局限：功能相似的分子可能在二维结构上差异显著。通过学习构象空间与药效团关系，支持跨骨架预测、虚拟筛选、靶标识别和骨架跃迁。",
            [
                "筛选 1,800 万化合物发现新骨架 GM-10，<br/>全细胞膜片钳证实其抑制 GluN1/GluN3A<br/>(IC<sub>50</sub> = 0.98 &#177; 0.13 &#956;M)。",
                award_line,
            ],
            [
                ("Advanced Science", "https://doi.org/10.1002/advs.202403998"),
                ("Acta Pharmacol. Sin.", "https://doi.org/10.1038/s41401-025-01571-1"),
                ("Code", "https://github.com/Wang-Lin-boop/GeminiMol"),
            ],
            style_map,
        ),
        zh_research_column(
            OUROBOROS_IMAGE,
            "2026 | 分子表征与生成",
            "Ouroboros",
            "Ouroboros 在按化学特征组织的统一表征空间中连接分子预测与设计。通过保留指纹、构象空间与药效团关系，支持性质预测、相似性筛选、定向多靶点药理设计及分子优化。",
            [
                "统一化学空间衔接预测建模与分子生成，使性质目标可直接引导候选分子设计。",
                "按构象与药效团关系组织化学空间，支持超越单一指纹相似性的骨架探索与多靶点设计。",
            ],
            [
                ("Advanced Science", "https://doi.org/10.1002/advs.202513556"),
                ("Commun. Chem.", "https://doi.org/10.1038/s42004-026-02115-2"),
                ("J. Med. Chem.", "https://doi.org/10.1021/acs.jmedchem.6c00902"),
                ("Code", "https://github.com/Wang-Lin-boop/Ouroboros"),
            ],
            style_map,
        ),
    ]
    table = Table([columns], colWidths=[57 * mm] * 3)
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


def zh_group_heading(text: str, style_map: dict[str, ParagraphStyle]) -> list:
    heading = Paragraph(text, style_map["group_heading"])
    heading.keepWithNext = 1
    rule = HRFlowable(width="100%", thickness=0.55, color=RULE, spaceAfter=1.2 * mm)
    rule.keepWithNext = 1
    return [heading, rule]


def zh_pub_entry(
    publication: dict,
    annotation: str,
    style_map: dict[str, ParagraphStyle],
    cjk_bold: str,
) -> KeepTogether:
    title_html = (
        html.escape(publication["title"])
        + f'<font name="{cjk_bold}">（{html.escape(annotation)}）</font>'
    )
    return KeepTogether(
        [
            Paragraph(title_html, style_map["pub_title"]),
            Paragraph(format_authors(publication), style_map["pub_authors"]),
            Paragraph(format_venue(publication), style_map["pub_venue"]),
        ]
    )


def make_footer(cjk_reg: str):
    def _footer(canvas, document) -> None:
        canvas.saveState()
        canvas.setFont(cjk_reg, 6.8)
        canvas.setFillColor(MUTED)
        canvas.drawString(18 * mm, 10 * mm, "王林 - 计算分子发现")
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"第{document.page}页")
        canvas.restoreState()

    return _footer


def render_chinese_cv(
    output_path: Path,
    publications_by_id: dict[str, dict],
    cjk_reg: str,
    cjk_bold: str,
    private_info: dict | None = None,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    style_map = zh_styles(cjk_reg, cjk_bold)

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=19 * mm,
        leftMargin=19 * mm,
        topMargin=13 * mm,
        bottomMargin=14 * mm,
        title="王林 - 个人简历",
        author="Lin Wang",
        subject="计算分子发现与人工智能药物设计",
    )

    name_line = Table(
        [[Paragraph("王林", style_map["name"]), Paragraph("Lin Wang", style_map["en_name"])]],
        colWidths=[24 * mm, 40 * mm],
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

    contact_lines = [
        "中国苏州 | "
        + link(EMAIL, f"mailto:{EMAIL}")
        + " | "
        + link("主页", WEBSITE)
        + " | "
        + link("GitHub", GITHUB)
        + " | "
        + link("Google Scholar", SCHOLAR)
        + " | "
        + link("ORCID", ORCID)
    ]
    photo_path = PROFILE_IMAGE
    if private_info:
        parts = []
        if private_info.get("phone"):
            parts.append(f"电话：{html.escape(str(private_info['phone']))}")
        if private_info.get("birth"):
            parts.append(f"出生年月：{html.escape(str(private_info['birth']))}")
        if private_info.get("hometown"):
            parts.append(f"籍贯：{html.escape(str(private_info['hometown']))}")
        if parts:
            contact_lines.append(" | ".join(parts))
        photo_rel = private_info.get("photo")
        if photo_rel:
            candidate = (PRIVATE_DIR / photo_rel).resolve()
            if candidate.is_file():
                photo_path = candidate

    identity = [
        name_line,
        Paragraph("博士后研究员 | 计算分子发现", style_map["subtitle"]),
        *[Paragraph(line, style_map["contact"]) for line in contact_lines],
    ]

    portrait_buffer = rectangular_portrait(photo_path)
    portrait = Image(portrait_buffer, width=24 * mm, height=33.6 * mm)
    header = Table([[identity, portrait]], colWidths=[147 * mm, 24 * mm], hAlign="LEFT")
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
        Spacer(1, 2.2 * mm),
        HRFlowable(width="100%", thickness=1.2, color=BLUE, spaceAfter=1.8 * mm),
        Paragraph(
            "我开发将化学先验融入分子表征学习与生成式药物设计的计算方法。研究涵盖 AI 驱动的药物发现、蛋白-配体、蛋白-蛋白及 RNA-配体相互作用建模，并拓展基于表型和多靶点药理学的药物设计。最新工作 Ouroboros 通过分子基础模型推进这一研究方向，利用构象空间与药效团相似性学习融入化学信息的表征，用于分子性质预测与生成。",
            style_map["summary"],
        ),
        zh_focus_and_edu_band(style_map),
        Spacer(1, 0.8 * mm),
        *section_heading("基金资助", style_map["section"]),
        Paragraph(
            "国家自然科学基金青年科学基金项目（C 类），项目编号：T2600798",
            style_map["funding"],
            bulletText="-",
        ),
        Paragraph(
            "北京协和医学院中央高校基本科研业务费，项目编号：3332025054",
            style_map["funding"],
            bulletText="-",
        ),
        Spacer(1, 1.0 * mm),
        *section_heading("代表性研究", style_map["section"]),
        zh_selected_research_table(style_map, cjk_bold),
        PageBreak(),
        *section_heading("代表性研究工作", style_map["pub_heading"]),
        Paragraph(
            "# = 共同第一作者；* = 共同通讯作者。IF：五年影响因子（2025）。",
            style_map["pub_note"],
        ),
        *zh_group_heading("原创算法开发", style_map),
    ]

    for pub_id, annotation in ORIGINAL_ALGO_WORKS:
        story.append(zh_pub_entry(publications_by_id[pub_id], annotation, style_map, cjk_bold))

    story.extend(zh_group_heading("应用研究", style_map))
    for pub_id, annotation in APPLICATION_WORKS:
        story.append(zh_pub_entry(publications_by_id[pub_id], annotation, style_map, cjk_bold))

    footer_fn = make_footer(cjk_reg)
    document.build(story, onFirstPage=footer_fn, onLaterPages=footer_fn)
    print(f"Wrote {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Chinese CV PDFs.")
    parser.add_argument(
        "--public-only",
        action="store_true",
        help="Only build the public CV (skip cv/private/profile.json).",
    )
    args = parser.parse_args()

    cjk_reg, cjk_bold = register_fonts()
    publications = json.loads(PUBLICATIONS.read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in publications}

    render_chinese_cv(PUBLIC_OUTPUT, by_id, cjk_reg, cjk_bold, private_info=None)

    if not args.public_only and PRIVATE_JSON.is_file():
        private_info = json.loads(PRIVATE_JSON.read_text(encoding="utf-8"))
        render_chinese_cv(PRIVATE_OUTPUT, by_id, cjk_reg, cjk_bold, private_info=private_info)


if __name__ == "__main__":
    main()
