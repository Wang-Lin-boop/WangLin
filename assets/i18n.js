(() => {
  "use strict";

  const ASSET_VERSION = "20261122-3";
  const STORAGE_KEY = "lin-wang-site-language";
  const SUPPORTED_LANGUAGES = ["en", "zh", "ar", "fr", "ru", "es"];
  const RTL_LANGUAGES = new Set(["ar"]);
  const ARABIC_FONTS_HREF =
    "https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;500;600&family=Noto+Sans+Arabic:wght@400;500;600&display=swap";

  const catalogCache = new Map();
  let currentLanguage = "en";
  let currentCatalog = null;
  let englishCatalog = null;

  const normalizeLanguage = (value) => {
    const clean = String(value || "").trim().toLowerCase().split("-")[0];
    return SUPPORTED_LANGUAGES.includes(clean) ? clean : null;
  };

  const getPathValue = (obj, dottedPath) => {
    if (!obj || !dottedPath) return undefined;
    return dottedPath.split(".").reduce((acc, part) => (acc != null ? acc[part] : undefined), obj);
  };

  const interpolate = (template, variables = {}) =>
    String(template).replace(/\{([a-zA-Z0-9_]+)\}/g, (_, key) =>
      Object.prototype.hasOwnProperty.call(variables, key) ? String(variables[key]) : `{${key}}`
    );

  const ensureArabicFonts = (lang) => {
    if (!RTL_LANGUAGES.has(lang)) return;
    if (document.querySelector('link[data-arabic-fonts="true"]')) return;
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = ARABIC_FONTS_HREF;
    link.dataset.arabicFonts = "true";
    document.head.appendChild(link);
  };

  const loadCatalog = async (lang) => {
    if (catalogCache.has(lang)) return catalogCache.get(lang);
    const response = await fetch(`./data/i18n/${lang}.json?v=${ASSET_VERSION}`);
    if (!response.ok) {
      throw new Error(`Failed to load translation catalog for ${lang}`);
    }
    const data = await response.json();
    catalogCache.set(lang, data);
    if (lang === "en") englishCatalog = data;
    return data;
  };

  const t = (key, variables = {}) => {
    const raw =
      getPathValue(currentCatalog, key) ??
      getPathValue(englishCatalog, key) ??
      key;
    if (typeof raw !== "string") return String(raw);
    return interpolate(raw, variables);
  };

  const applyTranslationsToDom = (lang) => {
    const page = document.body?.dataset?.page || "home";
    document.documentElement.lang = lang;
    document.documentElement.dir = RTL_LANGUAGES.has(lang) ? "rtl" : "ltr";
    document.documentElement.dataset.language = lang;
    ensureArabicFonts(lang);

    const metaTitle = getPathValue(currentCatalog, `meta.${page}.title`);
    if (metaTitle) document.title = metaTitle;

    const metaDesc = getPathValue(currentCatalog, `meta.${page}.description`);
    if (metaDesc) {
      const descEl = document.querySelector('meta[name="description"]');
      if (descEl) descEl.setAttribute("content", metaDesc);
    }

    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      const val = getPathValue(currentCatalog, key);
      if (typeof val === "string") el.textContent = val;
    });

    document.querySelectorAll("[data-i18n-html]").forEach((el) => {
      const key = el.getAttribute("data-i18n-html");
      const val = getPathValue(currentCatalog, key);
      if (typeof val === "string") el.innerHTML = val;
    });

    document.querySelectorAll("[data-i18n-aria]").forEach((el) => {
      const key = el.getAttribute("data-i18n-aria");
      const val = getPathValue(currentCatalog, key);
      if (typeof val === "string") el.setAttribute("aria-label", val);
    });

    document.querySelectorAll("[data-i18n-alt]").forEach((el) => {
      const key = el.getAttribute("data-i18n-alt");
      const val = getPathValue(currentCatalog, key);
      if (typeof val === "string") el.setAttribute("alt", val);
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      const key = el.getAttribute("data-i18n-placeholder");
      const val = getPathValue(currentCatalog, key);
      if (typeof val === "string") el.setAttribute("placeholder", val);
    });

    document.querySelectorAll("[data-i18n-caption]").forEach((el) => {
      const key = el.getAttribute("data-i18n-caption");
      const val = getPathValue(currentCatalog, key);
      if (typeof val === "string") el.setAttribute("data-lightbox-caption", val);
    });

    document.querySelectorAll("[data-language-select]").forEach((select) => {
      select.value = lang;
    });
  };

  const resolveInitialLanguage = () => {
    const params = new URLSearchParams(window.location.search);
    const fromQuery = normalizeLanguage(params.get("lang"));
    if (fromQuery) return fromQuery;

    try {
      const fromStorage = normalizeLanguage(window.localStorage.getItem(STORAGE_KEY));
      if (fromStorage) return fromStorage;
    } catch (_) {
      // Ignore storage access errors in private contexts
    }

    return "en";
  };

  const setLanguage = async (lang, { persist = true, updateUrl = false } = {}) => {
    const normalized = normalizeLanguage(lang) || "en";
    if (!englishCatalog) {
      try {
        await loadCatalog("en");
      } catch (_) {
        // Fallback to inline DOM content if fetch unavailable
      }
    }

    try {
      currentCatalog = await loadCatalog(normalized);
      currentLanguage = normalized;
    } catch (_) {
      currentCatalog = englishCatalog;
      currentLanguage = "en";
    }

    if (persist) {
      try {
        window.localStorage.setItem(STORAGE_KEY, currentLanguage);
      } catch (_) {
        // Ignore storage write failure
      }
    }

    if (updateUrl && window.history?.replaceState) {
      const url = new URL(window.location.href);
      if (currentLanguage === "en") {
        url.searchParams.delete("lang");
      } else {
        url.searchParams.set("lang", currentLanguage);
      }
      window.history.replaceState({}, "", url.toString());
    }

    applyTranslationsToDom(currentLanguage);
    window.dispatchEvent(
      new CustomEvent("site:languagechange", { detail: { language: currentLanguage } })
    );
    return currentLanguage;
  };

  const initPromise = (async () => {
    const initial = resolveInitialLanguage();
    await setLanguage(initial, { persist: false, updateUrl: false });

    document.querySelectorAll("[data-language-select]").forEach((select) => {
      select.addEventListener("change", (event) => {
        setLanguage(event.target.value, { persist: true, updateUrl: true });
      });
    });

    return currentLanguage;
  })();

  window.SiteI18n = {
    ASSET_VERSION,
    SUPPORTED_LANGUAGES,
    ready: initPromise,
    t,
    getLanguage: () => currentLanguage,
    setLanguage
  };
})();
