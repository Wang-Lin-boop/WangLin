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
- a real profile portrait as the only photographic asset;
- no generated molecules, scientific diagrams, decorative gradients, or speculative structure graphics;
- an Ouroboros research sequence that encodes the real workflow from molecular encoding through gradient-guided navigation to structural decoding;
- a publication-year rail that makes the chronology of the research record visible and navigable.

Motion is limited to navigation and hover feedback. Reduced-motion preferences are respected.

## Ouroboros-centered compact revision

The July 2026 revision makes Ouroboros the organizing center of the homepage. Its technical dossier is grounded in the peer-reviewed Advanced Science article (`10.1002/advs.202513556`), the associated preprint (`10.1101/2025.03.18.643899`), and the official `Wang-Lin-boop/Ouroboros` repository.

The dossier records the paper's architecture and selected evidence without introducing illustrative molecular structures:

- a global-attention GNN produces a 2048-dimensional molecular encoding;
- molecular fingerprints, conformational space, and pharmacophore similarity organize that encoding;
- property decoders guide exploration, migration, and fusion before an autoregressive Transformer decodes SMILES;
- the evidence strip reports the study's pre-training scale, DUD-E/LIT-PCBA benchmark scale, screened library size, and experimentally confirmed multi-target hits;
- a boundary note states that target-specific candidates still require docking, pose analysis, and experimental validation.

The layout was compressed into an academic-dossier reading rhythm: a 64 px header, a non-viewport-filling hero, tighter section spacing, compact project and publication rows, and responsive two-column evidence cells. The portrait now uses its natural aspect ratio with `object-fit: contain`, preventing facial or shoulder cropping. At 1440 px, the expanded homepage is approximately 39% shorter than the earlier loose layout despite the added research detail.

## Deployment model

The GitHub Actions workflow constructs a `_site` artifact from an explicit allowlist of public files and deploys it through GitHub Pages. There are no package installations, build frameworks, or runtime services. The workflow requests Pages enablement for a newly created repository.

## Maintenance checklist

- Keep the current role and institutional affiliation in `index.html` accurate.
- Update `data/publications.bib`, then regenerate `data/publications.json`.
- Add verified DOI values to `KNOWN_DOIS` in the parser when available.
- Verify desktop and mobile layouts after substantial copy or style changes.
- Confirm the Pages workflow completes after each push to `main`.
- Keep external links on HTTPS and avoid unverified metrics or claims.
