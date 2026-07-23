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

The biography, education, identifiers, contact information, and project links were transferred from the former repository. The canonical publication source is `data/publications.bib`, supplied for this redesign. It currently contains 33 works from 2020 through 2026. The dependency-free script in `scripts/parse_publications.py` converts that file into `data/publications.json` for the browser.

Direct DOI links are used where they were verified in the supplied metadata. Entries without a verified DOI open an exact-title Google Scholar search rather than relying on guessed identifiers.

## Template and visual direction

The information architecture is a lightweight adaptation of the academic priorities established by al-folio: a direct scholarly biography, selected work, and a dedicated publication record. The implementation does not use al-folio's Jekyll runtime or copy its component code.

The visual system is intentionally typographic:

- a white paper-like surface, graphite text, and one restrained cobalt accent;
- STIX Two Text for the scholarly display voice, IBM Plex Sans for reading, and IBM Plex Mono for metadata;
- a real profile portrait presented at its natural aspect ratio;
- original research figures supplied by the site owner, used only where they clarify a scientific relationship or workflow;
- no generated, redrawn, or speculative molecular structures;
- an Ouroboros research sequence that connects molecular encoding, hypothesis-defined objectives, encoding-space navigation, and structural reconstruction;
- a publication-year rail that makes the chronology of the research record visible and navigable.

Motion is limited to navigation and hover feedback. Reduced-motion preferences are respected.

## Ouroboros research profile and method lineage

The July 2026 revision gives Ouroboros a detailed technical profile within the broader research program. The account is grounded in the peer-reviewed Advanced Science article (`10.1002/advs.202513556`), the associated preprint (`10.1101/2025.03.18.643899`), and the official `Wang-Lin-boop/Ouroboros` repository.

The dossier now explains the methodological relationship between GeminiMol and Ouroboros:

- both use molecular conformational-space and pharmacophore similarity as chemical priors;
- GeminiMol learns from pairwise similarities between molecules;
- Ouroboros uses full molecular similarity matrices to organize several relative relationships in the encoding space at once;
- the two representation spaces are described alongside the screening, prediction, guided-generation, and discovery settings in which they were evaluated.

The representation-to-generation account follows a pharmacological hypothesis through four stages: hypothesis definition, a predictive objective supplied by a relevant property decoder or similarity target, navigation in molecular encoding space, and reconstruction of a revised encoding as SMILES. The application routes distinguish broader chemical-space search from iterative optimization beginning with a known hit, while retaining a multi-reference route for multi-target hypotheses.

Three owner-supplied PNG files were copied without generative editing into `images/research/`:

- `geminimol-ouroboros-lineage.png` for the method lineage and representative validation settings;
- `ouroboros-representation-engine.png` as the representation-foundation visual signature;
- `ouroboros-pharmacology-navigation.png` for pharmacological hypotheses, hit discovery, and hit-to-lead optimization.

The former numerical evidence strip and the `Current boundary` note were removed. The replacement remains compact: dense comparison rows, a four-step process, concise application routes, responsive figures, and full-resolution links for scientific inspection. All figures use translated alternative text and preserve their original molecular structures.

## Community record and multilingual revision

The current revision adds a compact Community section for work that is useful beyond formal publications. Descriptions were checked against the project pages and repository documentation:

- Biodb-Search sends a query to multiple biomedical databases from one browser-based navigator;
- AutoMD automates Desmond system setup and simulation, while AutoTRJ provides a configurable trajectory-analysis pipeline;
- CADD-Scripts collects shell workflows for virtual screening, cross-docking, and protein modeling with Schrödinger and Rosetta.

The News section restores all 14 dated entries from the former homepage, covering research releases, competition results, software updates, and publication milestones from 2019 through 2024. It also adds verified PhenoModel and Ouroboros publication updates. The two newest labels use the first formal electronic-publication dates rather than print-issue dates: PhenoModel is shown as `09 / 2025` from the PubMed electronic date of 2025-09-24 (PMID `41909744`), and Ouroboros is shown as `01 / 2026` from the Crossref and PubMed electronic date of 2026-01-04 (PMID `41486619`).

The interface supports all six official United Nations languages: Arabic, Chinese, English, French, Russian, and Spanish. English remains the no-JavaScript fallback. The browser loads a flat dictionary from `data/i18n/<language>.json`; `assets/i18n.js` applies the copy, stores the selected language in `localStorage`, and accepts shareable `?lang=` URLs. Arabic sets `dir="rtl"` and uses an Arabic type stack. Bibliographic titles, authors, journals, and DOI metadata remain in their source language, while filters, status messages, research-topic labels, figure captions, alternative text, and accessibility text are translated.

Multilingual QA checks both pages in all six languages, confirms 33 publication entries, verifies the three Community records and 16 News entries, and tests desktop and 390 px mobile layouts for horizontal overflow. The July 2026 figure revision additionally checks all three research images after lazy loading, the two newest machine-readable News dates, the absence of the removed evidence and boundary blocks, single-column mobile reflow, Arabic RTL rendering, translated alternative text, and browser console errors.

## Deployment model

The GitHub Actions workflow constructs a `_site` artifact from an explicit allowlist of public files and deploys it through GitHub Pages. There are no package installations, build frameworks, or runtime services. The workflow requests Pages enablement for a newly created repository.

## Maintenance checklist

- Keep the current role and institutional affiliation in `index.html` accurate.
- Update `data/publications.bib`, then regenerate `data/publications.json`.
- Add verified DOI values to `KNOWN_DOIS` in the parser when available.
- Keep all six translation files on an identical key set and translate new figure captions, alternative text, and accessibility labels.
- Verify desktop and mobile layouts after substantial copy or style changes.
- Confirm the Pages workflow completes after each push to `main`.
- Keep external links on HTTPS and avoid unverified metrics or claims.
