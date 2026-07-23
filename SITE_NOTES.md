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
- a research-scale sequence that encodes an actual progression from molecule to protein to cell;
- a publication-year rail that makes the chronology of the research record visible and navigable.

Motion is limited to navigation and hover feedback. Reduced-motion preferences are respected.

## Deployment model

The GitHub Actions workflow constructs a `_site` artifact from an explicit allowlist of public files and deploys it through GitHub Pages. There are no package installations, build frameworks, or runtime services. The workflow requests Pages enablement for a newly created repository.

## Maintenance checklist

- Keep the current role and institutional affiliation in `index.html` accurate.
- Update `data/publications.bib`, then regenerate `data/publications.json`.
- Add verified DOI values to `KNOWN_DOIS` in the parser when available.
- Verify desktop and mobile layouts after substantial copy or style changes.
- Confirm the Pages workflow completes after each push to `main`.
- Keep external links on HTTPS and avoid unverified metrics or claims.
