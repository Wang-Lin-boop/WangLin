# Lin Wang — Academic Homepage

This repository contains the source for [wang-lin-boop.github.io/WangLin](https://wang-lin-boop.github.io/WangLin/).

The site is a lightweight, dependency-free academic portfolio informed by the information architecture of [al-folio](https://github.com/alshedivat/al-folio). It uses a custom static implementation so the homepage remains fast, portable, and straightforward to maintain on GitHub Pages.

## Site structure

- `index.html`: biography, research program, featured Ouroboros research, grouped projects with authorship roles, selected publications, open tools, news (recent items plus a collapsible archive), background with funding and honors, and contact details
- `publications.html`: searchable and filterable full publication record
- `data/i18n/`: Arabic, Chinese, English, French, Russian, and Spanish interface copy
- `data/publications.bib`: canonical publication source
- `data/publications.json`: browser-ready publication data
- `scripts/parse_publications.py`: dependency-free BibTeX conversion script
- `scripts/build_cv.py`: academic English CV builder (`cv/Lin_Wang_CV_English.pdf`)
- `scripts/build_cv_zh.py`: job-oriented Chinese CV builder (`cv/Lin_Wang_CV_Chinese.pdf` plus optional local full version)
- `cv/`: repository-managed CVs and `private.example.json` template (not deployed to GitHub Pages; `cv/private/` is gitignored)
- `assets/site.css`: visual system and responsive layout
- `assets/i18n.js`: language selection, persistence, translated copy, and RTL support
- `assets/site.js`: responsive navigation and multilingual publication browser
- `.github/workflows/pages.yml`: GitHub Pages deployment

The only photographic asset on the public site is the real profile portrait in `images/profile.png`. The hero background uses a subtle geometric lattice texture rather than generated molecular structures or speculative scientific diagrams.

The pages serve WebP derivatives through `<picture>` (`images/profile.webp`, `images/research/*-1400.webp`, `ouroboros-representation-engine.webp`) and keep the original PNG files as fallbacks, lightbox targets, and CV inputs. Regenerate a WebP derivative whenever its source PNG changes. `images/og-card.png` (1200 x 630) is the social-preview card referenced by the Open Graph and Twitter meta tags.

## Update publications

1. Add or correct entries in `data/publications.bib`, then assign each new entry one primary category in `PUBLICATION_CATEGORIES` in `scripts/parse_publications.py`: `structural_bioinformatics`, `ppi_modeling`, `protein_ligand_modeling`, or `drug_discovery`.
2. Regenerate the JSON:

   ```bash
   python scripts/parse_publications.py data/publications.bib data/publications.json
   ```

3. Preview the site locally:

   ```bash
   python -m http.server 8000
   ```

4. Open `http://localhost:8000/` and verify the homepage and all four mutually exclusive publication filters.

The publication and translation requests use the asset version shared by `index.html`, `publications.html`, `404.html`, `assets/site.js`, and `assets/i18n.js`. For local previews, increment that `YYYYMMDD-N` version together when category data or translated labels change. On deployment, the Pages workflow replaces every copy with the first eight characters of the commit SHA, so GitHub Pages and browser caches cannot mix old JSON with new controls even if a manual bump is forgotten.

The homepage publication list (`data-publication-mode="selected"`) displays a curated set of six representative works (`FEATURED_PUBLICATION_IDS` in `assets/site.js`). The full record on `publications.html` offers a checkbox filter for all first-author, co-first-author (`#`), and co-corresponding-author (`*`) papers. In compact author lists, `Lin Wang` always stays visible even when the name falls beyond the truncation point.

## Manage CVs (`cv/`)

CV downloads are intentionally excluded from the public website (`.github/workflows/pages.yml` does not copy `cv/`), while the repository manages two distinct CVs built from the same canonical `data/publications.json`:

- **Academic English CV (`cv/Lin_Wang_CV_English.pdf`)** — built by `scripts/build_cv.py`. Focuses on research statement, research focus, academic lineage and supervisors, funding & honors, three illustrated Selected Research columns, and the complete chronological publication record.
- **Job-oriented Chinese CV (`cv/Lin_Wang_CV_Chinese.pdf`)** — built by `scripts/build_cv_zh.py`. Emphasizes core research directions, training and advisors, grants, three illustrated flagship works, and representative publications grouped into original algorithm development and applied studies.

### Private fields for local Chinese CV builds

Personal contact/biographical details and formal ID photos are never committed to Git:

1. Copy `cv/private.example.json` to `cv/private/profile.json` (`cv/private/` is gitignored) and fill in `phone`, `birth`, `hometown`, and an optional portrait filename (e.g., `photo.png` placed inside `cv/private/`).
2. Install dependencies and build both CVs:

   ```bash
   python -m pip install reportlab pillow
   python scripts/build_cv.py
   python scripts/build_cv_zh.py
   ```

   When `cv/private/profile.json` is present, `build_cv_zh.py` writes both the public `cv/Lin_Wang_CV_Chinese.pdf` (using `images/profile.png` and omitting private fields) and the full local `cv/private/Lin_Wang_CV_Chinese_full.pdf`. Pass `--public-only` to generate only the public file.
   On Windows, the builders automatically use `Arial` and `Microsoft YaHei`; on Linux/macOS without Windows fonts, they fall back to `Liberation Sans` / `DejaVu Sans` and `Noto Sans CJK SC` (via `fonttools` + `cu2qu` if installed) or `STSong-Light`. Rebuild on Windows if exact Microsoft YaHei glyph metrics are desired.

Contribution marks are maintained in `AUTHOR_MARKS` in `scripts/build_cv.py` (shared by `build_cv_zh.py`) and, for website highlighting, in `SELF_CONTRIBUTION_MARKS` in `assets/site.js`. Keep these maps synchronized. The website and CVs render `Lin Wang` in bold black only for first-author, co-first-author (`#`), or co-corresponding-author (`*`) publications; ordinary co-authorship remains at normal weight and uses the standard author color. The three CV research columns run chronologically from left to right: PPI-Miner (2022), GeminiMol (2024), and Ouroboros (2026).

## Update the profile summary

The English homepage has two copies of the Summary: the no-JavaScript fallback in `index.html` and `home.hero.statement` in `data/i18n/en.json`. Keep both identical, and update the same key in the other five translation files. The English CV copy in `scripts/build_cv.py` must match the English Summary word for word; rebuild `cv/Lin_Wang_CV_English.pdf` after every Summary change.

The current Summary describes machine-learning methods that bring chemical knowledge (conformations, pharmacophores, and molecular interactions) into molecular representation and drug design, spanning small-molecule discovery, protein–ligand, protein–protein, and RNA–ligand interaction modeling, and phenotype-based and multi-target design. The homepage research band organizes the same program into three lines: molecules, interactions, and phenotypes. Molecular-glue work remains in the PPI-Miner project context rather than appearing as a separate program-level direction.

## Deployment

Every push to `main` runs the GitHub Pages workflow. The workflow packages only the allowlisted public website files (`index.html`, `publications.html`, `404.html`, `robots.txt`, `sitemap.xml`, `site.webmanifest`, `.nojekyll`, `assets/`, `data/`, `images/`) and deploys them to the repository's Pages environment.

## License and attribution

The website source is released under the MIT License. Template research and third-party attribution are recorded in `THIRD_PARTY_NOTICES.md`.
