# Academic homepage redesign notes

## Project background

The former website was built from an older Academic Pages and Jekyll stack. It contained valuable biography, project, and publication material, but its template architecture and visual presentation no longer reflected the current research program. A generated molecular hero image was also rejected because its molecular structure was not scientifically credible.

This project creates a clean repository with a new history and a lightweight static site. The former repository is intended to remain available under an archive name for rollback, while the new repository reuses the `WangLin` name and therefore preserves the existing GitHub Pages address.

## Problem definition

The site must help collaborators, students, principal investigators, and scientific hiring committees understand four things:

- the research question connecting Lin Wang's work;
- how the work spans molecules, proteins, and cellular phenotype;
- which methods and projects represent the main contributions;
- where to find publications, source code, identifiers, and contact details.

It must remain readable on mobile devices, usable with a keyboard, searchable without a framework, and easy to deploy on GitHub Pages.

## Content and data

The biography, education, identifiers, contact information, and project links were transferred from the former repository. The canonical publication source is `data/publications.bib`, supplied for this redesign. It currently contains 35 works from 2020 through 2026. The dependency-free script in `scripts/parse_publications.py` converts that file into `data/publications.json` for the browser.

Direct DOI links are used where they were verified in the supplied metadata. Entries without a verified DOI open an exact-title Google Scholar search rather than relying on guessed identifiers.

## Template and visual direction

The information architecture is a lightweight adaptation of the academic priorities established by al-folio: a direct scholarly biography, selected work, and a dedicated publication record. The implementation does not use al-folio's Jekyll runtime or copy its component code.

The visual system is intentionally typographic:

- a white paper-like surface, graphite text, and one restrained cobalt accent;
- STIX Two Text for the scholarly display voice, IBM Plex Sans for reading, and IBM Plex Mono for metadata;
- a real profile portrait presented at its natural aspect ratio;
- original research figures supplied by the site owner, used only where they clarify a scientific relationship or workflow;
- no generated, redrawn, or speculative molecular structures;
- an Ouroboros research sequence that connects molecular encoding, a specified computational objective, encoding-space navigation, and candidate-structure reconstruction;
- a publication-year rail that makes the chronology of the research record visible and navigable.

Motion is limited to navigation and hover feedback. Reduced-motion preferences are respected.

## Ouroboros research profile and method lineage

The July 2026 revision gives Ouroboros a detailed technical profile within the broader research program. The account is grounded in the peer-reviewed Advanced Science article (`10.1002/advs.202513556`), the associated preprint (`10.1101/2025.03.18.643899`), and the official `Wang-Lin-boop/Ouroboros` repository.

The dossier now explains the methodological relationship between GeminiMol and Ouroboros:

- both use molecular conformational-space and pharmacophore similarity as chemical priors;
- GeminiMol learns from pairwise similarities between molecules;
- Ouroboros uses full molecular similarity matrices to organize several relative relationships in the encoding space at once;
- the two representation spaces are described alongside the screening, prediction, guided-generation, and discovery settings in which they were evaluated.

The representation-to-generation account follows four stages: definition of a molecular design question, formulation of a computational objective using a relevant property decoder or similarity function, navigation in molecular encoding space, and reconstruction of a revised encoding as candidate SMILES. These are presented as search settings evaluated in the study, not as experimentally validated capabilities. The account distinguishes broader chemical-space search from iterative optimization beginning with a known hit, while retaining a multi-reference setting for multi-target hypotheses.

Three owner-supplied PNG files were copied without generative editing into `images/research/`:

- `geminimol-ouroboros-lineage.png` for the method lineage and representative validation settings;
- `ouroboros-representation-engine.png` as the representation-foundation visual signature;
- `ouroboros-pharmacology-navigation.png` for pharmacological hypotheses, hit discovery, and hit-to-lead optimization.

The original alpha-enabled lineage figure remains preserved. The website uses `geminimol-ouroboros-lineage-white.png`, a deterministic 1964 x 929 RGB derivative made by compositing only the source alpha channel onto `#FFFFFF`. Pixel validation confirms that no fully opaque scientific-content pixel changed and that every fully transparent source pixel became pure white; no generative redraw was used.

The former numerical evidence strip and the `Current boundary` note were removed. The replacement remains compact: dense comparison rows, a four-step process, concise application routes, responsive figures, and full-resolution links for scientific inspection. All figures use translated alternative text and preserve their original molecular structures.

## Community record and multilingual revision

The current revision adds a compact Community section for work that is useful beyond formal publications. Descriptions were checked against the project pages and repository documentation:

- Biodb-Search sends a query to multiple biomedical databases from one browser-based navigator;
- AutoMD automates Desmond system setup and simulation, while AutoTRJ provides a configurable trajectory-analysis pipeline;
- CADD-Scripts collects shell workflows for virtual screening, cross-docking, and protein modeling with Schrödinger and Rosetta.

The News section restores all 14 dated entries from the former homepage, covering research releases, competition results, software updates, and publication milestones from 2019 through 2024. It also adds verified PhenoModel, Ouroboros, and CoCoBind publication updates. These labels use the first formal electronic-publication dates rather than print-issue dates: PhenoModel is shown as `09 / 2025` from the PubMed electronic date of 2025-09-24 (PMID `41909744`), Ouroboros is shown as `01 / 2026` from the Crossref and PubMed electronic date of 2026-01-04 (PMID `41486619`), and CoCoBind is shown as `08 / 2026` from the ACS and Crossref online-publication date of 2026-08-17. PubMed did not yet return a CoCoBind record when this update was prepared.

The interface supports all six official United Nations languages: Arabic, Chinese, English, French, Russian, and Spanish. English remains the no-JavaScript fallback. The browser loads a flat dictionary from `data/i18n/<language>.json`; `assets/i18n.js` applies the copy, stores the selected language in `localStorage`, and accepts shareable `?lang=` URLs. Arabic sets `dir="rtl"` and uses an Arabic type stack. Bibliographic titles, authors, journals, and DOI metadata remain in their source language, while filters, status messages, research-topic labels, figure captions, alternative text, and accessibility text are translated.

Multilingual QA checks both pages in all six languages, confirms 35 publication entries, verifies the three Community records and 17 News entries, and tests desktop and 390 px mobile layouts for horizontal overflow. The July 2026 figure revision additionally checks all three research images after lazy loading, the newest machine-readable News dates, the absence of the removed evidence and boundary blocks, single-column mobile reflow, Arabic RTL rendering, translated alternative text, and browser console errors.

## Copy and attribution review

The August 2026 copy review revised the homepage, publication introduction, and CV to make contribution boundaries explicit and reduce the risk of overstating computational results:

- first-person wording presents Lin Wang's research program and future directions, while project descriptions identify the scientific contribution without repeatedly emphasizing authorship position;
- model benchmarks and case studies are described as settings in which methods were evaluated, rather than as generally validated capabilities;
- generated structures and CRBN substrate-library entries are identified as computational candidates requiring downstream validation;
- News entries use the research project, paper, or released tool as the subject when individual attribution is not established by the record;
- publication titles, author order, contribution marks, DOI metadata, and reported experimental values remain unchanged.

The publication renderer now uses contribution-aware name emphasis. `Lin Wang` is rendered with the explicit Arial Bold font in pure black only when listed first or marked as co-first (`#`) or co-corresponding (`*`); ordinary co-authorship is not emphasized and retains the standard author color. The CV source of contribution marks is `AUTHOR_MARKS` in `scripts/build_cv.py`, and the website mirrors Lin Wang's relevant roles in `SELF_CONTRIBUTION_MARKS` in `assets/site.js`. The GeminiMol application paper uses the six equal-contribution authors recorded by PubMed (PMID `40355656`).

The publication browser uses four mutually exclusive primary categories: structural bioinformatics & cheminformatics, protein-protein interaction modeling, protein-ligand modeling, and drug discovery. Categories are assigned explicitly by publication ID in `PUBLICATION_CATEGORIES` in `scripts/parse_publications.py`; title-keyword inference was removed because it produced overlapping and scientifically ambiguous labels. The parser requires a category for every new BibTeX entry before regenerating the JSON record.

The category revision also versions `site.js`, `i18n.js`, `publications.json`, and translation requests with the same release token and disables response reuse for JSON fetches. This prevents a cached pre-category JSON file from being combined with the new filter IDs, which otherwise makes every selected category appear empty. The renderer additionally rejects publication records whose categories are unknown to the loaded site script.

The CV is generated reproducibly by `scripts/build_cv.py`. Its opening profile, research focus, experience, and selected-project sections follow the same attribution and evidence boundaries as the website, while the complete 35-work publication record remains sourced from `data/publications.json`.

The later August 2026 CV layout revision makes the Summary first-person and presents Ouroboros as the latest work within the broader research program. The Summary is identical in the English homepage and CV; molecular-glue discovery is retained as a PPI-Miner application rather than listed as a separate program-level direction. Page 1 now ends with three parallel Selected Research columns ordered chronologically from left to right: PPI-Miner (2022), GeminiMol (2024), and Ouroboros (2026). Each column combines an owner-supplied summary figure with a concise method description, explicit technical or scientific highlights, and resource links. The latest `images/research/cv-ouroboros.png` emphasizes conformational-space and pharmacophore similarity; the other figures are `images/research/cv-geminimol-screening.png` and `images/research/cv-ppi-miner-crbn.png`. The builder crops only transparent outer margins and preserves the underlying pixels. Publications start on page 2, with a deliberate continuation inside the 2023 group to keep the two publication pages balanced and avoid a sparsely filled final page.

The subsequent evidence-based revision separates method descriptions from highlights. GeminiMol is described as a pairwise contrastive graph-encoding framework trained against conformational-space and pharmacophore similarities; its highlights report the scaffold-distinct GM-10 discovered by screening 18 million compounds and validated by whole-cell patch clamp, plus the 2023 competition award. PPI-Miner is described as a motif-driven workflow in which backbone-structure similarity is the primary search signal and sequence similarity provides complementary evidence. Its highlights emphasize retrieval of sequence-divergent proteins with conserved motif geometry and the published proteome-wide CRBN result (1,739 predicted candidates, 16 of which had been reported experimentally before the study). Ouroboros retains similarity-matrix learning and property-guided generation as its two concise highlights, without repeating SMILES reconstruction in the latter.

## PPI-Miner evidence audit

The August 2026 revision was checked against the author-supplied PPI-Miner paper (`10.1021/acs.jcim.2c01033`; received 2022-08-14 and published 2022-11-30) and `CRBN_SubsLib_db.csv`. PPI-Miner has complementary sequence and structure modes rather than a single fused sequence-structure representation. The 3D mode searches continuous or discontinuous local backbones by Cα RMSD, transfers the known receptor-bound geometry, filters clashes, and refines and scores candidate interfaces. The method can define beta-hairpin, helix-loop-helix, sheet-helix, and composite structural motifs, while CRBN beta-hairpins are the paper's principal structural case study.

The CRBN search produced 74,012 possible complex structures before the G30 filter and 1,739 candidate proteins after requiring Gly at motif position six and excluding homology models below 30% template similarity. Sixteen candidates had prior experimental support. The supplied database export is broader than the paper's 1,739-protein G30 set: it contains 20,302 motif/structure rows, 6,740 unique UniProt IDs, and 2,622 unique IDs with a G-site row. Because the export has no explicit High-G30 membership field, later overlaps are described as released-library candidates and not as a numerically exact subset of the 1,739. Each of the 12 headline candidates has a G-site row derived from an experimental PDB structure: WEE1/5VDA, SCYL1/6BDN, CSNK1D/4TN6, LIMK1/3MMK, PLK3/4I6H, TRIB1/5CEM, MNAT1/1G25, WBP4/2JXW, CHD7/2V0F, ASS1/2NZ2, HNRNPD/5IM0, and KIFC3/5WDE.

A conservative retrospective audit uses motif-concordant, compound-dependent CRBN recruitment or ternary-complex evidence from Petzold et al., "Mining the CRBN target space redefines rules for molecular glue-induced neosubstrate recognition," <em>Science</em> 389, eadt6736 (2025), DOI `10.1126/science.adt6736`, PMID `40608931`. The relevant evidence is in the section "Exploration and validation of the β-hairpin G-loop target space," Figure 1E and 1G-I, and Figures S4-S5. Fourteen classical G-loop proteins in that study match the released database; NEK7 and LIMD1 were already among the paper's original 16, leaving at least 12 additional candidates: WEE1, SCYL1, CSNK1D, LIMK1, PLK3, TRIB1, MNAT1, WBP4, CHD7, ASS1, HNRNPD, and KIFC3. NanoBRET/TR-FRET covered the six kinase and six non-kinase candidates, and G-to-N mutation of the predicted G-loop glycine abolished the signal. This interaction-level endpoint is consistent with PPI-Miner's prediction scope. Broader proteomic and reporter-screen overlaps were not used because they mix motif classes and experimental endpoints.

Public-facing research copy should foreground the scientific limitation addressed, the discovery scope enabled, and experimentally grounded outcomes. Implementation sequences such as alignment, filtering, decoding, and refinement belong in papers or technical documentation unless they are necessary to understand a scientific claim. The homepage project cards and Ouroboros feature panels therefore frame Ouroboros around connecting prediction and design, GeminiMol around cross-scaffold functional similarity and GM-10, and PPI-Miner around backbone-motif discovery beyond sequence similarity and subsequent CRBN-recruitment evidence.

## Deployment model

The GitHub Actions workflow constructs a `_site` artifact from an explicit allowlist of public files and deploys it through GitHub Pages. There are no package installations, build frameworks, or runtime services. The workflow requests Pages enablement for a newly created repository.

## Maintenance checklist

- Keep the current role and institutional affiliation in `index.html` accurate.
- Keep the English Summary in `index.html`, `data/i18n/en.json`, and `scripts/build_cv.py` identical; synchronize its meaning across the other translation files.
- Update `data/publications.bib`, then regenerate `data/publications.json`.
- Rebuild `assets/Lin_Wang_CV.pdf` with `python scripts/build_cv.py` after changing profile text or publication data.
- Keep the three `images/research/cv-*.png` summary figures synchronized with the Selected Research descriptions.
- Add verified DOI values to `KNOWN_DOIS` in the parser when available.
- Keep all six translation files on an identical key set and translate new figure captions, alternative text, and accessibility labels.
- Verify desktop and mobile layouts after substantial copy or style changes.
- Confirm the Pages workflow completes after each push to `main`.
- Keep external links on HTTPS and avoid unverified metrics or claims.
