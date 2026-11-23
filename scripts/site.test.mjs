import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import "../assets/catalog-core.js";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const CatalogCore = globalThis.CatalogCore;
const publications = JSON.parse(
  fs.readFileSync(path.join(ROOT, "data", "publications.json"), "utf8")
);

const LANGUAGES = ["en", "zh", "fr", "es", "ar", "ru"];

const flattenKeys = (obj, prefix = "") => {
  const keys = [];
  for (const [k, v] of Object.entries(obj)) {
    const next = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === "object" && !Array.isArray(v)) {
      keys.push(...flattenKeys(v, next));
    } else {
      keys.push(next);
    }
  }
  return keys.sort();
};

test("publications.json has 35 entries and 15 key-author works", () => {
  assert.equal(publications.length, 35);
  const keyWorks = publications.filter((p) => CatalogCore.isKeyPublication(p));
  assert.equal(keyWorks.length, 15);
});

test("curated collections resolve exact verified counts without missing IDs", () => {
  const selected = CatalogCore.selectCollection(publications, "selected");
  const algorithms = CatalogCore.selectCollection(publications, "algorithms");
  const applications = CatalogCore.selectCollection(publications, "applications");

  assert.equal(selected.length, 8);
  assert.equal(algorithms.length, 9);
  assert.equal(applications.length, 8);
  assert.equal(selected[0].id, "wang2026learned");
});

test("filtering by topic, query, and key-author toggle works accurately", () => {
  const keyOnly = CatalogCore.filterPublications(publications, { keyOnly: true });
  assert.equal(keyOnly.length, 15);

  const ouroboros = CatalogCore.filterPublications(publications, { query: "Ouroboros" });
  assert.ok(ouroboros.length >= 1);
  assert.equal(ouroboros[0].id, "wang2026learned");

  const ppiKey = CatalogCore.filterPublications(publications, {
    topic: "ppi_modeling",
    keyOnly: true
  });
  assert.ok(ppiKey.some((p) => p.id === "wang2022ppi"));
});

test("author formatting bolds Lin Wang strictly on first/co-first/co-corr works and preserves self in compact mode", () => {
  const firstAuthorPaper = publications.find((p) => p.id === "wang2026learned");
  const coCorrPaper = publications.find((p) => p.id === "zhou2026proteinconformers");
  const regularCoAuthor = publications.find((p) => !CatalogCore.isKeyPublication(p));

  const firstHtml = CatalogCore.formatAuthorsHtml(firstAuthorPaper, { compact: true });
  assert.match(firstHtml, /<strong class="self-author">Lin Wang<\/strong>/);

  const coCorrHtml = CatalogCore.formatAuthorsHtml(coCorrPaper, { compact: true });
  assert.match(coCorrHtml, /<strong class="self-author">Lin Wang<\/strong><sup class="author-mark">\*<\/sup>/);

  const regularHtml = CatalogCore.formatAuthorsHtml(regularCoAuthor, { compact: false });
  assert.doesNotMatch(regularHtml, /<strong class="self-author">Lin Wang<\/strong>/);
});

test("BibTeX formatter produces clean valid entries", () => {
  const pub = publications.find((p) => p.id === "wang2026learned");
  const bib = CatalogCore.formatBibTeX(pub);
  assert.ok(bib.startsWith("@article{wang2026learned,"));
  assert.ok(bib.includes("year = {2026}"));
  assert.ok(bib.endsWith("\n}"));
  assert.ok(!bib.includes(",\n}"));
});

test("all 6 i18n catalogs share 100% identical non-empty key sets", () => {
  const catalogs = Object.fromEntries(
    LANGUAGES.map((lang) => [
      lang,
      JSON.parse(fs.readFileSync(path.join(ROOT, "data", "i18n", `${lang}.json`), "utf8"))
    ])
  );
  const enKeys = flattenKeys(catalogs.en);

  for (const lang of LANGUAGES) {
    const keys = flattenKeys(catalogs[lang]);
    assert.deepEqual(keys, enKeys, `Key mismatch in data/i18n/${lang}.json`);
    for (const key of keys) {
      const val = key.split(".").reduce((acc, part) => acc[part], catalogs[lang]);
      assert.equal(typeof val, "string", `${lang}.${key} must be a string`);
      assert.ok(val.trim().length > 0, `${lang}.${key} must not be empty`);
    }
  }
});

test("all local images and assets referenced by HTML files exist on disk", () => {
  const htmlFiles = ["index.html", "publications.html", "404.html"];
  const attrRegex = /(?:src|srcset|href)="(\.\/[^"?#]+)/g;

  for (const file of htmlFiles) {
    const content = fs.readFileSync(path.join(ROOT, file), "utf8");
    let match;
    while ((match = attrRegex.exec(content)) !== null) {
      const rel = match[1].replace(/^\.\//, "");
      const fullPath = path.join(ROOT, rel);
      assert.ok(fs.existsSync(fullPath), `Missing asset ${rel} referenced in ${file}`);
    }
  }
});

test("English hero summary stays synchronized across index.html, en.json, and scripts/build_cv.py", () => {
  const en = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "i18n", "en.json"), "utf8"));
  const indexHtml = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");
  const cvPy = fs.readFileSync(path.join(ROOT, "scripts", "build_cv.py"), "utf8");
  const summary = en.home.hero.statement;

  assert.ok(indexHtml.includes(summary), "index.html hero statement out of sync with en.json");
  assert.ok(cvPy.includes(summary), "scripts/build_cv.py summary out of sync with en.json");
});

test("every DOI linked in index.html and i18n files matches publications.json or approved external citations", () => {
  const validDois = new Set([
    ...publications.map((p) => p.doi).filter(Boolean),
    "10.1101/2025.03.18.643899", // Ouroboros bioRxiv preprint
    "10.1126/science.adt6736" // Petzold et al. Science 2025 cross-validation
  ]);

  const files = [
    path.join(ROOT, "index.html"),
    ...LANGUAGES.map((lang) => path.join(ROOT, "data", "i18n", `${lang}.json`))
  ];
  const doiRegex = /https:\/\/doi\.org\/([^"\\<\s]+)/g;

  for (const file of files) {
    const content = fs.readFileSync(file, "utf8");
    let match;
    while ((match = doiRegex.exec(content)) !== null) {
      assert.ok(validDois.has(match[1]), `Unverified DOI ${match[1]} in ${path.basename(file)}`);
    }
  }
});

test("every data-i18n* key referenced in HTML files resolves to a non-empty string in en.json", () => {
  const en = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "i18n", "en.json"), "utf8"));
  const htmlFiles = ["index.html", "publications.html", "404.html"];
  const keyRegex = /data-i18n(?:-[a-z]+)?="([^"]+)"/g;

  for (const file of htmlFiles) {
    const content = fs.readFileSync(path.join(ROOT, file), "utf8");
    let match;
    while ((match = keyRegex.exec(content)) !== null) {
      const key = match[1];
      const val = key.split(".").reduce((acc, part) => (acc != null ? acc[part] : undefined), en);
      assert.equal(typeof val, "string", `Missing i18n key "${key}" referenced in ${file}`);
      assert.ok(val.trim().length > 0, `Empty i18n key "${key}" referenced in ${file}`);
    }
  }
});

test("homepage structure enforces standalone contact section, 2026 NSFC grant, and 3-panel Ouroboros orthogonality", () => {
  const indexHtml = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");
  assert.match(indexHtml, /<section id="contact" class="section/);
  assert.match(indexHtml, /2026 · NSFC T2600798/);
  assert.match(indexHtml, /<time datetime="2026">2026<\/time>[\s\S]{0,200}T2600798/);
  assert.match(indexHtml, /ouroboros-projection-orthogonality\.png/);
  assert.match(indexHtml, /ouroboros-smiles-reconstruction\.png/);
  assert.match(indexHtml, /ouroboros-iterative-optimization\.png/);
  assert.match(indexHtml, /thumb-cocobind\.png/);
  assert.match(indexHtml, /thumb-mcr1\.png/);
  assert.match(indexHtml, /Comp\. Bio\. &amp; Drug Discovery/);
  assert.match(indexHtml, /statAwardNote">GeminiMol team/);
  assert.match(indexHtml, /CADD-Scripts/);
  assert.match(indexHtml, /AutoMD \/ AutoTRJ/);
  assert.match(indexHtml, /Biodb-Search/);
});

