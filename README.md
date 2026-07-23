# Lin Wang — Academic Homepage

This repository contains the source for [wang-lin-boop.github.io/WangLin](https://wang-lin-boop.github.io/WangLin/).

The site is a lightweight, dependency-free academic portfolio informed by the information architecture of [al-folio](https://github.com/alshedivat/al-folio). It uses a custom static implementation so the homepage remains fast, portable, and straightforward to maintain on GitHub Pages.

## Site structure

- `index.html`: biography, research program, projects, community tools, news, trajectory, and contact details
- `publications.html`: searchable and filterable full publication record
- `data/i18n/`: Arabic, Chinese, English, French, Russian, and Spanish interface copy
- `data/publications.bib`: canonical publication source
- `data/publications.json`: browser-ready publication data
- `scripts/parse_publications.py`: dependency-free BibTeX conversion script
- `assets/site.css`: visual system and responsive layout
- `assets/i18n.js`: language selection, persistence, translated copy, and RTL support
- `assets/site.js`: responsive navigation and multilingual publication browser
- `.github/workflows/pages.yml`: GitHub Pages deployment

The only photographic asset is the real profile portrait in `images/profile.png`. The design intentionally avoids generated molecular imagery and decorative scientific diagrams.

## Update publications

1. Add or correct entries in `data/publications.bib`.
2. Regenerate the JSON:

   ```bash
   python scripts/parse_publications.py data/publications.bib data/publications.json
   ```

3. Preview the site locally:

   ```bash
   python -m http.server 8000
   ```

4. Open `http://localhost:8000/` and verify the homepage and publication filters.

## Deployment

Every push to `main` runs the GitHub Pages workflow. The workflow packages only the public website files and deploys them to the repository's Pages environment.

## License and attribution

The website source is released under the MIT License. Template research and third-party attribution are recorded in `THIRD_PARTY_NOTICES.md`.
