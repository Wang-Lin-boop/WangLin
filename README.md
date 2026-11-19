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
- `scripts/build_cv.py`: reproducible CV builder using the website publication data
- `assets/site.css`: visual system and responsive layout
- `assets/i18n.js`: language selection, persistence, translated copy, and RTL support
- `assets/site.js`: responsive navigation and multilingual publication browser
- `.github/workflows/pages.yml`: GitHub Pages deployment

The only photographic asset is the real profile portrait in `images/profile.png`. The design intentionally avoids generated molecular imagery and decorative scientific diagrams.

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

The publication and translation requests use the asset version shared by `index.html`, `publications.html`, `assets/site.js`, and `assets/i18n.js`. For local previews, increment that `YYYYMMDD-N` version together when category data or translated labels change. On deployment, the Pages workflow replaces every copy with the first eight characters of the commit SHA, so GitHub Pages and browser caches cannot mix old JSON with new controls even if a manual bump is forgotten.

The homepage publication list (`data-publication-mode="selected"`) shows only first-author, co-first-author (`#`), and co-corresponding-author (`*`) papers. The full record offers the same filter through the role checkbox. In compact author lists, `Lin Wang` always stays visible even when the name falls beyond the truncation point.

## Update the CV

1. Edit the profile, research-focus, experience, or selected-project copy in `scripts/build_cv.py`.
2. Replace the three selected-research figures in `images/research/cv-ouroboros.png`, `images/research/cv-geminimol-screening.png`, and `images/research/cv-ppi-miner-crbn.png` when the project summaries change. The builder crops transparent margins without altering the scientific content.
3. Keep publication metadata in `data/publications.bib`, then regenerate `data/publications.json` as described above.
4. Rebuild the PDF:

   ```bash
   python -m pip install reportlab pillow
   python scripts/build_cv.py
   ```

5. Review all three pages of `assets/Lin_Wang_CV.pdf` before publishing. Page 1 is the research overview; the complete publication record starts on page 2. The builder preserves the website publication data and the contribution marks recorded in the script.

Contribution marks are maintained in `AUTHOR_MARKS` in `scripts/build_cv.py` and, for website highlighting, in `SELF_CONTRIBUTION_MARKS` in `assets/site.js`. Keep these maps synchronized. The website and CV render `Lin Wang` in bold black only for first-author, co-first-author (`#`), or co-corresponding-author (`*`) publications; ordinary co-authorship remains at normal weight and uses the standard author color. The three CV research columns run chronologically from left to right: PPI-Miner (2022), GeminiMol (2024), and Ouroboros (2026).

## Update the profile summary

The English homepage has two copies of the Summary: the no-JavaScript fallback in `index.html` and `home.hero.statement` in `data/i18n/en.json`. Keep both identical, and update the same key in the other five translation files. The CV copy is defined separately in `scripts/build_cv.py` and should match the English Summary word for word; rebuild the PDF after every Summary change.

The current Summary describes machine-learning methods that bring chemical knowledge (conformations, pharmacophores, and molecular interactions) into molecular representation and drug design, spanning small-molecule discovery, protein–ligand, protein–protein, and RNA–ligand interaction modeling, and phenotype-based and multi-target design. The homepage research band organizes the same program into three lines: molecules, interactions, and phenotypes. Molecular-glue work remains in the PPI-Miner project context rather than appearing as a separate program-level direction.

## Deployment

Every push to `main` runs the GitHub Pages workflow. The workflow packages only the public website files and deploys them to the repository's Pages environment.

## License and attribution

The website source is released under the MIT License. Template research and third-party attribution are recorded in `THIRD_PARTY_NOTICES.md`.
