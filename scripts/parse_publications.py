#!/usr/bin/env python3
"""Convert the user-supplied BibTeX list into the site's publication JSON.

The parser is intentionally dependency-free so future publication updates only
require replacing data/publications.bib and rerunning this script.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.parse
from pathlib import Path


KNOWN_DOIS = {
    "jin2020structure": "10.1038/s41586-020-2223-y",
    "wang2022ppi": "10.1021/acs.jcim.2c01033",
    "wang2023deepsa": "10.1186/s13321-023-00771-3",
    "wang2024conformational": "10.1002/advs.202403998",
    "liang2025mcr3": "10.1016/j.ebiom.2025.105923",
    "wang2025phenomodel": "10.1016/j.apsb.2025.09.036",
    "wang2026learned": "10.1002/advs.202513556",
    "wang2026cocobind": "10.1021/acs.jmedchem.6c00902",
}


# Each publication has one primary research category so filters remain
# mutually exclusive and do not depend on ambiguous title keywords.
PUBLICATION_CATEGORIES = {
    "wang2026cocobind": "structural_bioinformatics",
    "liu2026integrating": "protein_ligand_modeling",
    "wang2026learned": "structural_bioinformatics",
    "lu2026molecular": "drug_discovery",
    "zhou2026proteinconformers": "structural_bioinformatics",
    "wang2026small": "structural_bioinformatics",
    "zhang2025deeppsa": "drug_discovery",
    "wang2025discovery": "drug_discovery",
    "liang2025mcr3": "drug_discovery",
    "li2025mai": "protein_ligand_modeling",
    "li2025nadph": "drug_discovery",
    "wang2025phenomodel": "drug_discovery",
    "wang2025recent": "drug_discovery",
    "wang2024conformational": "structural_bioinformatics",
    "fu2024salvianolic": "drug_discovery",
    "liang2023new": "drug_discovery",
    "wang2023deepsa": "drug_discovery",
    "han2023discovery": "drug_discovery",
    "mei2023discovery": "drug_discovery",
    "zhu2023propofol": "drug_discovery",
    "li2023synthesis": "drug_discovery",
    "ren2022multi": "drug_discovery",
    "wang2022crystal": "structural_bioinformatics",
    "wang2022discovery": "drug_discovery",
    "liu2022pilsl": "drug_discovery",
    "wang2022ppi": "ppi_modeling",
    "sun2022rapamycin": "drug_discovery",
    "li2022recent": "ppi_modeling",
    "hou2022target": "drug_discovery",
    "wang2021ckb": "drug_discovery",
    "li2021identification": "protein_ligand_modeling",
    "wang2021probing": "protein_ligand_modeling",
    "yang2020antimicrobial": "protein_ligand_modeling",
    "jin2020structure": "drug_discovery",
    "wang2020structural": "structural_bioinformatics",
}


def balanced_segment(text: str, start: int, opener: str = "{", closer: str = "}") -> tuple[str, int]:
    depth = 0
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return text[start + 1 : index], index + 1
    raise ValueError(f"Unclosed {opener!r} starting at {start}")


def parse_entries(text: str) -> list[tuple[str, str, dict[str, str]]]:
    entries: list[tuple[str, str, dict[str, str]]] = []
    cursor = 0
    header = re.compile(r"@(article|incollection)\s*\{\s*([^,]+),", re.IGNORECASE)
    while match := header.search(text, cursor):
        entry_type = match.group(1).lower()
        key = match.group(2).strip()
        outer_start = text.find("{", match.start())
        body, cursor = balanced_segment(text, outer_start)
        body = body[body.find(",") + 1 :]

        fields: dict[str, str] = {}
        field_re = re.compile(r"([A-Za-z][A-Za-z0-9_]*)\s*=\s*\{", re.MULTILINE)
        field_cursor = 0
        while field_match := field_re.search(body, field_cursor):
            value_start = body.find("{", field_match.start())
            value, field_cursor = balanced_segment(body, value_start)
            fields[field_match.group(1).lower()] = value.strip()
        entries.append((entry_type, key, fields))
    return entries


def clean_tex(value: str) -> str:
    replacements = {
        r"$\beta$": "β",
        r"$\gamma$": "γ",
        r"\_": "_",
        r"\&": "&",
        "--": "–",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def format_author(name: str) -> str:
    name = clean_tex(name)
    if "," not in name:
        return name
    family, given = (part.strip() for part in name.split(",", 1))
    return f"{given} {family}".strip()


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: parse_publications.py INPUT.bib OUTPUT.json")

    source = Path(sys.argv[1])
    destination = Path(sys.argv[2])
    records = []
    for entry_type, key, fields in parse_entries(source.read_text(encoding="utf-8")):
        if key not in PUBLICATION_CATEGORIES:
            raise ValueError(f"Add a primary publication category for {key!r}")
        title = clean_tex(fields.get("title", ""))
        authors = [format_author(name) for name in fields.get("author", "").split(" and ")]
        year = int(fields.get("year", "0"))
        venue = clean_tex(fields.get("journal") or fields.get("booktitle", ""))
        doi = KNOWN_DOIS.get(key)
        query = urllib.parse.quote_plus(f'"{title}"')
        records.append(
            {
                "id": key,
                "type": "book chapter" if entry_type == "incollection" else "journal article",
                "title": title,
                "authors": authors,
                "venue": venue,
                "year": year,
                "volume": clean_tex(fields.get("volume", "")),
                "issue": clean_tex(fields.get("number", "")),
                "pages": clean_tex(fields.get("pages", "")),
                "topics": [PUBLICATION_CATEGORIES[key]],
                "doi": doi,
                "url": f"https://doi.org/{doi}" if doi else f"https://scholar.google.com/scholar?q={query}",
            }
        )

    records.sort(key=lambda item: (-item["year"], item["title"].casefold()))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} publications to {destination}")


if __name__ == "__main__":
    main()
