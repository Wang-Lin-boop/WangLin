(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  }
  root.CatalogCore = api;
})(typeof globalThis !== "undefined" ? globalThis : window, function () {
  "use strict";

  const TOPIC_KEYS = {
    structural_bioinformatics: "topics.structuralBioinformatics",
    ppi_modeling: "topics.ppiModeling",
    protein_ligand_modeling: "topics.proteinLigandModeling",
    drug_discovery: "topics.drugDiscovery"
  };

  // Curated collections aligned with both English academic CV and Chinese CV groupings.
  const COLLECTION_IDS = {
    selected: [
      "wang2026learned",
      "wang2026cocobind",
      "liu2026integrating",
      "zhou2026proteinconformers",
      "wang2025phenomodel",
      "wang2024conformational",
      "wang2023deepsa",
      "wang2022ppi"
    ],
    algorithms: [
      "wang2026learned",
      "wang2024conformational",
      "wang2022ppi",
      "wang2026small",
      "wang2026cocobind",
      "liu2026integrating",
      "zhou2026proteinconformers",
      "wang2025phenomodel",
      "wang2023deepsa"
    ],
    applications: [
      "lu2026molecular",
      "wang2025discovery",
      "li2025nadph",
      "liang2025mcr3",
      "liang2023new",
      "wang2022discovery",
      "wang2021probing",
      "jin2020structure"
    ]
  };

  // Synchronized with AUTHOR_MARKS in scripts/build_cv.py.
  const SELF_CONTRIBUTION_MARKS = {
    zhou2026proteinconformers: "*",
    wang2026cocobind: "#*",
    liu2026integrating: "*",
    wang2025discovery: "#",
    liang2025mcr3: "#",
    li2025nadph: "*",
    wang2025phenomodel: "#",
    liang2023new: "#",
    wang2023deepsa: "#",
    wang2022discovery: "#",
    wang2021probing: "#"
  };

  // Method & alias search keywords so researchers searching tool names find matching papers.
  const SEARCH_ALIASES = {
    wang2026learned: "Ouroboros",
    wang2024conformational: "GeminiMol",
    wang2025discovery: "GeminiMol GM-10 GluN1 GluN3A",
    wang2022ppi: "PPI-Miner CRBN molecular glue",
    wang2026cocobind: "CoCoBind RNA",
    liu2026integrating: "SBDD chemical priors",
    zhou2026proteinconformers: "ProteinConformers NeurIPS",
    wang2025phenomodel: "PhenoModel",
    wang2023deepsa: "DeepSA",
    zhang2025deeppsa: "DeepPSA PROTAC"
  };

  const escapeHtml = (value) =>
    String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

  const normalizeText = (value) =>
    String(value ?? "")
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase();

  const isSelfAuthor = (author) => normalizeText(author) === "lin wang";

  const getContributionMark = (publicationId) => SELF_CONTRIBUTION_MARKS[publicationId] || "";

  // Key papers: first author, co-first author (#), or co-corresponding author (*).
  const isKeyPublication = (publication) => {
    const authors = publication?.authors || [];
    const mark = getContributionMark(publication?.id);
    return isSelfAuthor(authors[0]) || mark.includes("#") || mark.includes("*");
  };

  const getRoleKey = (publication) => {
    const authors = publication?.authors || [];
    const mark = getContributionMark(publication?.id);
    if (mark.includes("#") && mark.includes("*")) return "home.role.cofirstCorresponding";
    if (mark.includes("#")) return "home.role.cofirst";
    if (mark.includes("*")) return "home.role.corresponding";
    if (isSelfAuthor(authors[0])) return "home.role.first";
    return "";
  };

  const sortPublications = (items = []) =>
    [...items].sort((a, b) => {
      const yearDiff = Number(b.year) - Number(a.year);
      return yearDiff || String(a.title).localeCompare(String(b.title));
    });

  const selectCollection = (items = [], mode = "selected") => {
    const ids = COLLECTION_IDS[mode];
    if (!ids) return sortPublications(items);
    const byId = new Map(items.map((item) => [item.id, item]));
    return ids.map((id) => byId.get(id)).filter(Boolean);
  };

  const filterPublications = (
    items = [],
    { topic = "all", query = "", keyOnly = false } = {}
  ) => {
    const cleanQuery = normalizeText(query).trim();
    return items.filter((publication) => {
      const matchesTopic = topic === "all" || (publication.topics || []).includes(topic);
      if (!matchesTopic) return false;
      if (keyOnly && !isKeyPublication(publication)) return false;
      if (!cleanQuery) return true;

      const haystack = normalizeText(
        [
          publication.title,
          publication.venue,
          publication.year,
          publication.type,
          publication.doi,
          SEARCH_ALIASES[publication.id] || "",
          ...(publication.authors || [])
        ].join(" ")
      );
      return haystack.includes(cleanQuery);
    });
  };

  const formatAuthorsHtml = (publication, { compact = false, etAlLabel = "et al." } = {}) => {
    const authors = publication?.authors || [];
    const contributionMark = getContributionMark(publication?.id);
    const selfIndex = authors.findIndex(isSelfAuthor);
    let visibleIndexes = authors.map((_, index) => index);
    let hasOmittedAuthors = false;

    if (compact && authors.length > 7) {
      hasOmittedAuthors = true;
      visibleIndexes = selfIndex >= 6 ? [0, 1, 2, 3, 4, "gap", selfIndex] : [0, 1, 2, 3, 4, 5];
    }

    const names = visibleIndexes.map((index) => {
      if (index === "gap") return "…";
      const author = authors[index];
      if (normalizeText(author) === "others") return `<em>${escapeHtml(etAlLabel)}</em>`;

      const safeName = escapeHtml(author);
      if (!isSelfAuthor(author)) return safeName;

      const marks = contributionMark
        ? `<sup class="author-mark">${escapeHtml(contributionMark)}</sup>`
        : "";
      return index === 0 || contributionMark
        ? `<strong class="self-author">${safeName}</strong>${marks}`
        : safeName;
    });

    if (hasOmittedAuthors && visibleIndexes[visibleIndexes.length - 1] !== authors.length - 1) {
      names.push(`<em>${escapeHtml(etAlLabel)}</em>`);
    }

    return names.join(", ");
  };

  const formatBibTeX = (publication) => {
    const isChapter = publication?.type === "book chapter";
    const entryType = isChapter ? "incollection" : "article";
    const key = publication?.id || "reference";
    const authors = (publication?.authors || []).join(" and ");
    const venueField = isChapter ? "booktitle" : "journal";

    const lines = [
      `@${entryType}{${key},`,
      `  title = {${publication?.title || ""}},`,
      `  author = {${authors}},`,
      `  ${venueField} = {${publication?.venue || ""}},`,
      `  year = {${publication?.year || ""}}`
    ];
    if (publication?.volume) lines.push(`  volume = {${publication.volume}},`);
    if (publication?.issue) lines.push(`  number = {${publication.issue}},`);
    if (publication?.pages) lines.push(`  pages = {${publication.pages}},`);
    if (publication?.doi) lines.push(`  doi = {${publication.doi}},`);

    // Remove trailing comma on last field line for strict BibTeX cleanliness
    const lastIdx = lines.length - 1;
    lines[lastIdx] = lines[lastIdx].replace(/,$/, "");
    lines.push("}");
    return lines.join("\n");
  };

  const groupByYear = (items = []) => {
    const grouped = new Map();
    items.forEach((pub) => {
      const year = String(pub.year);
      if (!grouped.has(year)) grouped.set(year, []);
      grouped.get(year).push(pub);
    });
    return [...grouped.entries()];
  };

  const interpolateMessage = (template, variables = {}) =>
    String(template).replace(/\{([a-zA-Z0-9_]+)\}/g, (_, name) =>
      Object.prototype.hasOwnProperty.call(variables, name) ? String(variables[name]) : `{${name}}`
    );

  return {
    TOPIC_KEYS,
    COLLECTION_IDS,
    SELF_CONTRIBUTION_MARKS,
    escapeHtml,
    normalizeText,
    isSelfAuthor,
    getContributionMark,
    isKeyPublication,
    getRoleKey,
    sortPublications,
    selectCollection,
    filterPublications,
    formatAuthorsHtml,
    formatBibTeX,
    groupByYear,
    interpolateMessage
  };
});
