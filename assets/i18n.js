(() => {
  "use strict";

  const SUPPORTED_LANGUAGES = ["en", "zh", "ar", "fr", "ru", "es"];
  const RTL_LANGUAGES = new Set(["ar"]);
  const STORAGE_KEY = "lin-wang-site-language";

  const DYNAMIC_FALLBACKS = {
    "topics.ai": "Molecular AI",
    "topics.structure": "Structure & PPI",
    "topics.discovery": "Drug discovery",
    "topics.article": "Research article",
    "publications.loading": "Loading publication record…",
    "publications.empty": "No publications match this search. Try a broader term or another research area.",
    "publications.error": "The publication list could not be loaded. View the <a href=\"./data/publications.bib\">BibTeX record</a> instead.",
    "publications.unavailable": "Publication data unavailable",
    "publications.status": "Showing {shown} of {total} works",
    "publications.statusOne": "Showing {shown} of {total} work",
    "publications.workCount": "{count} works",
    "publications.workCountOne": "{count} work",
    "publications.countAria": "{count} publications",
    "publications.etAl": "et al."
  };

  const COMMON_BINDINGS = [
    [".skip-link", "common.skip"],
    [".wordmark", "common.homeAria", "aria-label"],
    [".nav-toggle span", "common.menu"],
    [".primary-nav", "common.primaryNav", "aria-label"],
    [".primary-nav a[href$='#research']", "nav.research"],
    [".primary-nav a[href$='#work']", "nav.projects"],
    [".primary-nav a[href$='#community']", "nav.community"],
    [".primary-nav a[href$='#news']", "nav.news"],
    [".primary-nav a[href$='publications.html']", "nav.publications"],
    [".language-control .sr-only", "common.language"],
    ["[data-language-select]", "common.language", "aria-label"],
    [".site-footer p:nth-child(2)", "common.footerTag"],
    [".site-footer a", "common.backTop"]
  ];

  const HOME_BINDINGS = [
    [".hero .section-tag", "home.hero.tag"],
    ["#hero-title", "home.hero.title", "html"],
    [".hero-statement", "home.hero.statement"],
    [".hero-actions", "home.hero.actionsAria", "aria-label"],
    [".hero-actions a:nth-child(1)", "home.hero.paper", "html"],
    [".hero-actions a:nth-child(2)", "common.code", "html"],
    [".hero-actions a:nth-child(3)", "common.scholar", "html"],
    [".current-role .metadata-label", "home.hero.position"],
    [".current-role p:last-child", "home.hero.role", "html"],
    [".profile-panel", "home.profile.aria", "aria-label"],
    [".profile-panel img", "home.profile.alt", "alt"],
    [".profile-details div:nth-child(1) dt", "home.profile.basedLabel"],
    [".profile-details div:nth-child(1) dd", "home.profile.basedValue"],
    [".profile-details div:nth-child(2) dt", "home.profile.researchLabel"],
    [".profile-details div:nth-child(2) dd", "home.profile.researchValue"],
    [".profile-details div:nth-child(3) dt", "home.profile.contactLabel"],
    [".scale-heading .metadata-label", "home.scale.tag"],
    ["#scale-title", "home.scale.title"],
    [".scale-sequence li:nth-child(1) .scale-index", "home.scale.encodeIndex"],
    [".scale-sequence li:nth-child(1) h3", "home.scale.encodeTitle"],
    [".scale-sequence li:nth-child(1) p:last-child", "home.scale.encodeText"],
    [".scale-sequence li:nth-child(2) .scale-index", "home.scale.navigateIndex"],
    [".scale-sequence li:nth-child(2) h3", "home.scale.navigateTitle"],
    [".scale-sequence li:nth-child(2) p:last-child", "home.scale.navigateText"],
    [".scale-sequence li:nth-child(3) .scale-index", "home.scale.decodeIndex"],
    [".scale-sequence li:nth-child(3) h3", "home.scale.decodeTitle"],
    [".scale-sequence li:nth-child(3) p:last-child", "home.scale.decodeText"],
    [".dossier-kicker .section-tag", "home.dossier.tag"],
    [".dossier-deck", "home.dossier.deck"],
    [".dossier-links", "home.dossier.linksAria", "aria-label"],
    [".dossier-links a:nth-child(1)", "home.dossier.peerPaper", "html"],
    [".dossier-links a:nth-child(2)", "home.dossier.preprint", "html"],
    [".dossier-links a:nth-child(3)", "home.dossier.codeModels", "html"],
    [".dossier-architecture", "home.dossier.architectureAria", "aria-label"],
    [".dossier-architecture article:nth-child(1) .research-question", "home.scale.encodeIndex"],
    [".dossier-architecture article:nth-child(1) h3", "home.dossier.encodeTitle"],
    [".dossier-architecture article:nth-child(1) p:last-child", "home.dossier.encodeText"],
    [".dossier-architecture article:nth-child(2) .research-question", "home.scale.navigateIndex"],
    [".dossier-architecture article:nth-child(2) h3", "home.dossier.navigateTitle"],
    [".dossier-architecture article:nth-child(2) p:last-child", "home.dossier.navigateText"],
    [".dossier-architecture article:nth-child(3) .research-question", "home.scale.decodeIndex"],
    [".dossier-architecture article:nth-child(3) h3", "home.dossier.decodeTitle"],
    [".dossier-architecture article:nth-child(3) p:last-child", "home.dossier.decodeText"],
    [".lineage-copy > .metadata-label", "home.lineage.tag"],
    ["#lineage-title", "home.lineage.title"],
    [".lineage-intro", "home.lineage.intro"],
    [".lineage-comparison article:nth-child(1) h4", "home.lineage.geminiTitle"],
    [".lineage-comparison article:nth-child(1) > p:nth-of-type(2)", "home.lineage.geminiText"],
    [".lineage-comparison article:nth-child(1) .lineage-validation", "home.lineage.geminiValidation", "html"],
    [".lineage-comparison article:nth-child(2) h4", "home.lineage.ouroborosTitle"],
    [".lineage-comparison article:nth-child(2) > p:nth-of-type(2)", "home.lineage.ouroborosText"],
    [".lineage-comparison article:nth-child(2) .lineage-validation", "home.lineage.ouroborosValidation", "html"],
    [".lineage-figure figcaption", "home.lineage.caption"],
    [".engine-mark figcaption", "home.engine.figureCaption"],
    [".engine-copy .metadata-label", "home.engine.tag"],
    ["#engine-title", "home.engine.title"],
    [".engine-copy > p:last-child", "home.engine.intro"],
    [".engine-flow", "home.engine.flowAria", "aria-label"],
    [".engine-flow li:nth-child(1) h4", "home.engine.hypothesisTitle"],
    [".engine-flow li:nth-child(1) p", "home.engine.hypothesisText"],
    [".engine-flow li:nth-child(2) h4", "home.engine.objectiveTitle"],
    [".engine-flow li:nth-child(2) p", "home.engine.objectiveText"],
    [".engine-flow li:nth-child(3) h4", "home.engine.navigationTitle"],
    [".engine-flow li:nth-child(3) p", "home.engine.navigationText"],
    [".engine-flow li:nth-child(4) h4", "home.engine.reconstructionTitle"],
    [".engine-flow li:nth-child(4) p", "home.engine.reconstructionText"],
    [".evolution-heading .metadata-label", "home.operations.tag"],
    [".evolution-heading p:last-child", "home.operations.intro"],
    [".evolution-grid article:nth-of-type(1) h3", "home.operations.explorationTitle"],
    [".evolution-grid article:nth-of-type(1) p", "home.operations.explorationText"],
    [".evolution-grid article:nth-of-type(2) h3", "home.operations.migrationTitle"],
    [".evolution-grid article:nth-of-type(2) p", "home.operations.migrationText"],
    [".evolution-grid article:nth-of-type(3) h3", "home.operations.fusionTitle"],
    [".evolution-grid article:nth-of-type(3) p", "home.operations.fusionText"],
    [".application-figure figcaption", "home.engine.applicationCaption"],
    ["#work .section-tag", "home.projects.tag"],
    ["#work-title", "home.projects.title"],
    ["#work .section-intro > div > p", "home.projects.intro"],
    ["#work .project-links a:first-child", "common.paper", "html"],
    ["#work .project-links a:nth-child(2)", "common.code", "html"],
    ["#publications .section-tag", "home.recent.tag"],
    ["#recent-title", "home.recent.title"],
    ["#publications .section-intro > div > p", "home.recent.intro", "html"],
    ["#publications .loading-note", "publications.loading"],
    ["#publications .section-action a", "home.recent.all", "html"],
    ["#trajectory .section-tag", "home.trajectory.tag"],
    ["#trajectory-title", "home.trajectory.title"],
    ["#trajectory .section-intro > div > p", "home.trajectory.intro"],
    [".trajectory-list li:nth-child(1) h3", "home.trajectory.bs"],
    [".trajectory-list li:nth-child(1) > p:last-child", "home.trajectory.bsText"],
    [".trajectory-list li:nth-child(2) h3", "home.trajectory.phd"],
    [".trajectory-list li:nth-child(2) > p:last-child", "home.trajectory.phdText"],
    [".trajectory-list li:nth-child(3) h3", "home.trajectory.postdoc"],
    [".trajectory-list li:nth-child(3) > p:last-child", "home.trajectory.postdocText"],
    ["#contact .section-tag", "home.contact.tag"],
    ["#contact-title", "home.contact.title"],
    ["#contact div > p", "home.contact.text"],
    [".contact-links", "home.contact.linksAria", "aria-label"]
  ];

  const PROJECT_NAMES = ["ouroboros", "geminimol", "phenomodel", "proteinconformers", "ppiminer", "deepsa"];
  PROJECT_NAMES.forEach((project, index) => {
    const number = index + 1;
    HOME_BINDINGS.push(
      [`#work .project-row:nth-child(${number}) .project-kind`, `home.projects.${project}.kind`],
      [`#work .project-row:nth-child(${number}) .project-main p`, `home.projects.${project}.tagline`],
      [`#work .project-row:nth-child(${number}) .project-detail`, `home.projects.${project}.detail`]
    );
  });

  const PUBLICATION_BINDINGS = [
    [".page-heading .section-tag", "record.tag"],
    [".page-heading h1", "record.title"],
    [".page-heading-copy p", "record.intro", "html"],
    [".page-heading-copy a", "record.download", "html"],
    ["#publication-browser-title", "record.browserTitle"],
    [".publication-controls", "record.filtersAria", "aria-label"],
    ["[data-publication-filter='all']", "record.all"],
    ["[data-publication-filter='ai']", "record.ai"],
    ["[data-publication-filter='structure']", "record.structure"],
    ["[data-publication-filter='discovery']", "record.discovery"],
    [".publication-search .sr-only", "record.search"],
    ["[data-publication-search]", "record.searchPlaceholder", "placeholder"],
    ["[data-publication-status]", "publications.loading"],
    [".publication-list .loading-note", "publications.loading"],
    [".year-rail", "record.yearsAria", "aria-label"],
    [".year-rail .metadata-label", "record.jump"],
    ["[data-year-navigation]", "record.jumpAria", "aria-label"]
  ];

  let currentLanguage = "en";
  let messages = { ...DYNAMIC_FALLBACKS };
  const messageCache = new Map();

  const normalizeLanguage = (value) => {
    const candidate = String(value || "").trim().toLowerCase().split(/[-_]/)[0];
    return SUPPORTED_LANGUAGES.includes(candidate) ? candidate : null;
  };

  const interpolate = (value, variables = {}) =>
    String(value).replace(/\{([a-zA-Z0-9_]+)\}/g, (_, name) =>
      Object.prototype.hasOwnProperty.call(variables, name) ? String(variables[name]) : `{${name}}`
    );

  const t = (key, variables = {}) =>
    interpolate(messages[key] ?? DYNAMIC_FALLBACKS[key] ?? key, variables);

  const setNodeValue = (node, key, mode) => {
    const value = t(key);
    if (mode === "html") {
      node.innerHTML = value;
    } else if (mode) {
      node.setAttribute(mode, value);
    } else {
      node.textContent = value;
    }
  };

  const applyBindingSet = (bindings) => {
    bindings.forEach(([selector, key, mode]) => {
      document.querySelectorAll(selector).forEach((node) => setNodeValue(node, key, mode));
    });
  };

  const applyDataBindings = () => {
    document.querySelectorAll("[data-i18n]").forEach((node) => setNodeValue(node, node.dataset.i18n));
    document.querySelectorAll("[data-i18n-html]").forEach((node) => setNodeValue(node, node.dataset.i18nHtml, "html"));
    document.querySelectorAll("[data-i18n-aria]").forEach((node) => setNodeValue(node, node.dataset.i18nAria, "aria-label"));
    document.querySelectorAll("[data-i18n-alt]").forEach((node) => setNodeValue(node, node.dataset.i18nAlt, "alt"));
  };

  const applyMetadata = (page) => {
    const title = t(`${page}.meta.title`);
    const description = t(`${page}.meta.description`);
    if (!title.endsWith(".title")) document.title = title;
    document.querySelector('meta[name="description"]')?.setAttribute("content", description);
    document.querySelector('meta[property="og:title"]')?.setAttribute("content", title);
    document.querySelector('meta[property="og:description"]')?.setAttribute("content", description);
  };

  const applyTranslations = () => {
    const page = document.body.dataset.page || "home";
    applyBindingSet(COMMON_BINDINGS);
    applyBindingSet(page === "publications" ? PUBLICATION_BINDINGS : HOME_BINDINGS);
    applyDataBindings();
    applyMetadata(page);
    document.querySelectorAll("[data-language-select]").forEach((select) => {
      select.value = currentLanguage;
    });
  };

  const loadMessages = async (language) => {
    if (messageCache.has(language)) return messageCache.get(language);
    const response = await fetch(`./data/i18n/${language}.json`);
    if (!response.ok) throw new Error(`Translation request failed: ${response.status}`);
    const data = await response.json();
    messageCache.set(language, data);
    return data;
  };

  const updateUrl = (language) => {
    const url = new URL(window.location.href);
    if (language === "en") {
      url.searchParams.delete("lang");
    } else {
      url.searchParams.set("lang", language);
    }
    window.history.replaceState({}, "", `${url.pathname}${url.search}${url.hash}`);
  };

  const setLanguage = async (language, options = {}) => {
    const normalized = normalizeLanguage(language) || "en";
    currentLanguage = normalized;
    document.documentElement.lang = normalized === "zh" ? "zh-CN" : normalized;
    document.documentElement.dir = RTL_LANGUAGES.has(normalized) ? "rtl" : "ltr";
    document.documentElement.dataset.language = normalized;

    if (options.persist !== false) {
      try {
        window.localStorage.setItem(STORAGE_KEY, normalized);
      } catch (_) {
        // Language selection still works when storage is unavailable.
      }
    }
    if (options.updateUrl) updateUrl(normalized);

    try {
      messages = { ...DYNAMIC_FALLBACKS, ...(await loadMessages(normalized)) };
    } catch (error) {
      console.error(error);
      if (normalized !== "en") {
        try {
          messages = { ...DYNAMIC_FALLBACKS, ...(await loadMessages("en")) };
        } catch (fallbackError) {
          console.error(fallbackError);
          messages = { ...DYNAMIC_FALLBACKS };
        }
      }
    }

    applyTranslations();
    document.dispatchEvent(new CustomEvent("site:languagechange", { detail: { language: normalized } }));
    return normalized;
  };

  const requestedLanguage = normalizeLanguage(new URLSearchParams(window.location.search).get("lang"));
  let storedLanguage = null;
  try {
    storedLanguage = normalizeLanguage(window.localStorage.getItem(STORAGE_KEY));
  } catch (_) {
    storedLanguage = null;
  }
  const browserLanguage = (navigator.languages || [navigator.language]).map(normalizeLanguage).find(Boolean);
  const initialLanguage = requestedLanguage || storedLanguage || browserLanguage || "en";

  const api = {
    t,
    setLanguage,
    get language() {
      return currentLanguage;
    },
    get supportedLanguages() {
      return [...SUPPORTED_LANGUAGES];
    }
  };
  window.SiteI18n = api;

  document.querySelectorAll("[data-language-select]").forEach((select) => {
    select.addEventListener("change", (event) => {
      setLanguage(event.target.value, { persist: true, updateUrl: true });
    });
  });

  api.ready = setLanguage(initialLanguage, { persist: true, updateUrl: Boolean(requestedLanguage) });
})();
