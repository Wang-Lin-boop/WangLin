(() => {
  "use strict";

  const ASSET_VERSION = "20261122-3";
  const EMAIL_ADDRESS = "Wanglin1102@outlook.com";
  const core = window.CatalogCore;

  const t = (key, vars = {}) => {
    if (window.SiteI18n && typeof window.SiteI18n.t === "function") {
      return window.SiteI18n.t(key, vars);
    }
    return core ? core.interpolateMessage(key, vars) : key;
  };

  const copyTextToClipboard = async (text) => {
    if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (_) {
        // Fallback below
      }
    }
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.select();
    let ok = false;
    try {
      ok = document.execCommand("copy");
    } catch (_) {
      ok = false;
    }
    textarea.remove();
    return ok;
  };

  const flashButtonFeedback = (button, copiedText, originalText) => {
    if (!button) return;
    clearTimeout(button._copyTimer);
    button.classList.add("is-copied");
    button.textContent = copiedText;
    button._copyTimer = setTimeout(() => {
      button.classList.remove("is-copied");
      button.textContent = originalText;
    }, 1800);
  };

  /* ------------------------------------------------------------------------
     1. Mobile Navigation Drawer
     ------------------------------------------------------------------------ */
  const setupNavigation = () => {
    const toggle = document.querySelector("[data-nav-toggle]");
    const nav = document.querySelector("[data-primary-nav]");
    if (!toggle || !nav) return;

    const closeNav = () => {
      toggle.setAttribute("aria-expanded", "false");
      nav.classList.remove("is-open");
      document.body.classList.remove("nav-open");
    };

    toggle.addEventListener("click", () => {
      const expanded = toggle.getAttribute("aria-expanded") === "true";
      if (expanded) {
        closeNav();
      } else {
        toggle.setAttribute("aria-expanded", "true");
        nav.classList.add("is-open");
        document.body.classList.add("nav-open");
      }
    });

    nav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", closeNav);
    });

    window.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeNav();
    });

    window.addEventListener("resize", () => {
      if (window.innerWidth > 780) closeNav();
    });
  };

  /* ------------------------------------------------------------------------
     2. Copy Email Controls
     ------------------------------------------------------------------------ */
  const setupEmailCopy = () => {
    document.querySelectorAll("[data-copy-email]").forEach((button) => {
      button.addEventListener("click", async () => {
        const email = button.getAttribute("data-copy-email") || EMAIL_ADDRESS;
        const ok = await copyTextToClipboard(email);
        if (ok) {
          const defaultLabel = t("common.copyEmail");
          const copiedLabel = t("common.copied");
          flashButtonFeedback(button, copiedLabel, defaultLabel);
        }
      });
    });
  };

  /* ------------------------------------------------------------------------
     3. Ouroboros Monograph Segmented Switcher
     ------------------------------------------------------------------------ */
  const setupMonographTabs = () => {
    const tabs = [...document.querySelectorAll("[data-monograph-tab]")];
    const panels = [...document.querySelectorAll("[data-monograph-panel]")];
    if (!tabs.length || !panels.length) return;

    const activate = (targetId) => {
      tabs.forEach((tab) => {
        const active = tab.getAttribute("data-monograph-tab") === targetId;
        tab.setAttribute("aria-selected", String(active));
        tab.classList.toggle("is-active", active);
      });
      panels.forEach((panel) => {
        const match = panel.getAttribute("data-monograph-panel") === targetId;
        panel.hidden = !match;
      });
    };

    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        activate(tab.getAttribute("data-monograph-tab"));
      });
    });
  };

  /* ------------------------------------------------------------------------
     4. Research Portfolio Category Filter
     ------------------------------------------------------------------------ */
  const setupPortfolioFilter = () => {
    const buttons = [...document.querySelectorAll("[data-portfolio-filter]")];
    const items = [...document.querySelectorAll("[data-portfolio-category]")];
    const countEl = document.querySelector("[data-portfolio-count]");
    const flagshipGroup = document.querySelector('[data-portfolio-group="flagship"]');
    const ledgerGroup = document.querySelector('[data-portfolio-group="ledger"]');
    const ledgerHeading = document.querySelector("[data-portfolio-ledger-heading]");
    if (!buttons.length || !items.length) return;

    const updateCount = () => {
      if (!countEl) return;
      const visible = items.filter((item) => !item.hidden).length;
      countEl.textContent = t("home.portfolio.count", {
        shown: visible,
        total: items.length
      });
    };

    const applyFilter = (category) => {
      buttons.forEach((btn) => {
        const active = btn.getAttribute("data-portfolio-filter") === category;
        btn.classList.toggle("is-active", active);
        btn.setAttribute("aria-pressed", String(active));
      });

      items.forEach((item) => {
        const cats = (item.getAttribute("data-portfolio-category") || "").split(/\s+/);
        item.hidden = category !== "all" && !cats.includes(category);
      });

      const visibleFlagship = flagshipGroup
        ? [...flagshipGroup.querySelectorAll("[data-portfolio-category]")].some((el) => !el.hidden)
        : false;
      const visibleLedger = ledgerGroup
        ? [...ledgerGroup.querySelectorAll("[data-portfolio-category]")].some((el) => !el.hidden)
        : false;

      if (flagshipGroup) flagshipGroup.hidden = !visibleFlagship;
      if (ledgerGroup) ledgerGroup.hidden = !visibleLedger;
      if (ledgerHeading) ledgerHeading.hidden = !visibleLedger || !visibleFlagship;

      updateCount();
    };

    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        applyFilter(btn.getAttribute("data-portfolio-filter"));
      });
    });

    window.addEventListener("site:languagechange", updateCount);
    updateCount();
  };

  /* ------------------------------------------------------------------------
     5. Accessible Figure Lightbox (<dialog>)
     ------------------------------------------------------------------------ */
  const setupLightbox = () => {
    const dialog = document.querySelector("[data-figure-lightbox]");
    if (!dialog) return;

    const imgEl = dialog.querySelector("[data-lightbox-img]");
    const captionEl = dialog.querySelector("[data-lightbox-caption-text]");
    const fullLink = dialog.querySelector("[data-lightbox-full]");
    const closeBtn = dialog.querySelector("[data-lightbox-close]");

    const openDialog = (trigger) => {
      const src = trigger.getAttribute("href") || trigger.getAttribute("data-lightbox-src");
      const caption = trigger.getAttribute("data-lightbox-caption") || "";
      const imgInTrigger = trigger.querySelector("img");
      const alt = imgInTrigger ? imgInTrigger.alt : caption;
      if (!src || !imgEl) return;

      imgEl.src = src;
      imgEl.alt = alt;
      if (captionEl) captionEl.textContent = caption;
      if (fullLink) fullLink.href = src;

      if (typeof dialog.showModal === "function") {
        dialog.showModal();
      } else {
        dialog.setAttribute("open", "");
      }
    };

    const closeDialog = () => {
      if (typeof dialog.close === "function" && dialog.open) {
        dialog.close();
      } else {
        dialog.removeAttribute("open");
      }
    };

    document.querySelectorAll("[data-lightbox-trigger]").forEach((trigger) => {
      trigger.addEventListener("click", (event) => {
        event.preventDefault();
        openDialog(trigger);
      });
    });

    if (closeBtn) closeBtn.addEventListener("click", closeDialog);

    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) closeDialog();
    });
  };

  /* ------------------------------------------------------------------------
     6. Publication Rendering + BibTeX Copy
     ------------------------------------------------------------------------ */
  let cachedPublications = null;
  let publicationMap = new Map();

  const loadPublications = async () => {
    if (cachedPublications) return cachedPublications;
    const response = await fetch(`./data/publications.json?v=${ASSET_VERSION}`);
    if (!response.ok) {
      throw new Error("Could not load publications.json");
    }
    const raw = await response.json();
    cachedPublications = core ? core.sortPublications(raw) : raw;
    publicationMap = new Map(cachedPublications.map((item) => [item.id, item]));
    return cachedPublications;
  };

  const renderPublicationItem = (pub, { compact = false } = {}) => {
    const roleKey = core.getRoleKey(pub);
    const roleLabel = roleKey ? t(roleKey) : "";
    const topicLabels = (pub.topics || [])
      .map((topic) => (core.TOPIC_KEYS[topic] ? t(core.TOPIC_KEYS[topic]) : ""))
      .filter(Boolean);
    const asideLabel = roleLabel
      ? [roleLabel, topicLabels[0]].filter(Boolean).join(" · ")
      : topicLabels[0] || "";

    const authorsHtml = core.formatAuthorsHtml(pub, {
      compact,
      etAlLabel: t("common.etAl")
    });

    const titleInner = pub.url
      ? `<a href="${core.escapeHtml(pub.url)}" target="_blank" rel="noreferrer">${core.escapeHtml(pub.title)}</a>`
      : core.escapeHtml(pub.title);

    const doiLink = pub.url
      ? `<a class="quiet-link" href="${core.escapeHtml(pub.url)}" target="_blank" rel="noreferrer">${core.escapeHtml(t("common.doi"))} <span aria-hidden="true">↗</span></a>`
      : "";

    const citeLabel = t("common.bibtex");
    const citeAria = t("common.copyBibtexFor", { title: pub.title });

    return `
      <article class="publication-item" data-pub-id="${core.escapeHtml(pub.id)}">
        <p class="publication-item-year">${core.escapeHtml(pub.year)}</p>
        <div class="publication-main">
          <h3>${titleInner}</h3>
          <p class="publication-authors">${authorsHtml}</p>
          <p class="publication-venue">${core.escapeHtml(pub.venue)}</p>
        </div>
        <div class="publication-aside">
          ${asideLabel ? `<p class="publication-topic">${core.escapeHtml(asideLabel)}</p>` : ""}
          <div class="publication-item-actions">
            ${doiLink}
            <button type="button" class="cite-button" data-copy-bibtex="${core.escapeHtml(pub.id)}" aria-label="${core.escapeHtml(citeAria)}">${core.escapeHtml(citeLabel)}</button>
          </div>
        </div>
      </article>
    `;
  };

  const bindBibtexCopyButtons = (container) => {
    if (!container) return;
    container.querySelectorAll("[data-copy-bibtex]").forEach((button) => {
      button.addEventListener("click", async () => {
        const pubId = button.getAttribute("data-copy-bibtex");
        const pub = publicationMap.get(pubId);
        if (!pub) return;
        const bibtex = core.formatBibTeX(pub);
        const ok = await copyTextToClipboard(bibtex);
        if (ok) {
          flashButtonFeedback(button, t("common.copied"), t("common.bibtex"));
        }
      });
    });
  };

  /* ------------------------------------------------------------------------
     7. Home Curated Publications Tabs
     ------------------------------------------------------------------------ */
  const setupHomePublications = async () => {
    const listEl = document.querySelector("[data-home-publications]");
    if (!listEl || !core) return;

    const tabButtons = [...document.querySelectorAll("[data-pub-collection]")];
    let activeCollection = "selected";

    let allPublications = [];
    try {
      allPublications = await loadPublications();
    } catch (_) {
      listEl.innerHTML = `<p class="empty-state">${core.escapeHtml(t("publications.error"))}</p>`;
      return;
    }

    const render = () => {
      const items = core.selectCollection(allPublications, activeCollection);
      listEl.innerHTML = items.map((pub) => renderPublicationItem(pub, { compact: true })).join("");
      bindBibtexCopyButtons(listEl);

      tabButtons.forEach((btn) => {
        const isActive = btn.getAttribute("data-pub-collection") === activeCollection;
        btn.setAttribute("aria-selected", String(isActive));
        btn.classList.toggle("is-active", isActive);
      });
    };

    tabButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        activeCollection = btn.getAttribute("data-pub-collection") || "selected";
        render();
      });
    });

    window.addEventListener("site:languagechange", render);
    render();
  };

  /* ------------------------------------------------------------------------
     8. Full Publications Archive Page
     ------------------------------------------------------------------------ */
  const setupPublicationsArchive = async () => {
    const listEl = document.querySelector("[data-full-publications]");
    if (!listEl || !core) return;

    const filterButtons = [...document.querySelectorAll("[data-topic-filter]")];
    const searchInput = document.querySelector("[data-publication-search]");
    const keyOnlyCheckbox = document.querySelector("[data-key-only-toggle]");
    const statusEl = document.querySelector("[data-publication-status]");
    const yearRailNav = document.querySelector("[data-year-rail]");

    const state = {
      topic: "all",
      query: "",
      keyOnly: false
    };

    let allPublications = [];
    let yearObserver = null;

    try {
      allPublications = await loadPublications();
    } catch (_) {
      listEl.innerHTML = `<p class="empty-state">${core.escapeHtml(t("publications.error"))}</p>`;
      return;
    }

    const setupYearObserver = () => {
      if (yearObserver) yearObserver.disconnect();
      if (!yearRailNav || typeof IntersectionObserver === "undefined") return;

      const sections = [...listEl.querySelectorAll(".publication-year")];
      const links = new Map(
        [...yearRailNav.querySelectorAll("a")].map((a) => [a.getAttribute("href"), a])
      );

      const markYear = (id) => {
        links.forEach((link, href) => {
          link.setAttribute("aria-current", href === `#${id}` ? "true" : "false");
        });
      };

      if (sections[0]) markYear(sections[0].id);

      yearObserver = new IntersectionObserver(
        (entries) => {
          const visible = entries
            .filter((entry) => entry.isIntersecting)
            .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
          if (visible[0]) markYear(visible[0].target.id);
        },
        { rootMargin: "-15% 0px -65% 0px", threshold: 0 }
      );

      sections.forEach((section) => yearObserver.observe(section));
    };

    const render = () => {
      const filtered = core.filterPublications(allPublications, state);
      const total = allPublications.length;

      filterButtons.forEach((btn) => {
        const active = btn.getAttribute("data-topic-filter") === state.topic;
        btn.classList.toggle("is-active", active);
        btn.setAttribute("aria-pressed", String(active));
      });

      if (statusEl) {
        statusEl.textContent = t("publications.status", {
          shown: filtered.length,
          total
        });
      }

      if (!filtered.length) {
        listEl.innerHTML = `<p class="empty-state">${core.escapeHtml(t("publications.empty"))}</p>`;
        if (yearRailNav) yearRailNav.innerHTML = "";
        return;
      }

      const grouped = core.groupByYear(filtered);

      if (yearRailNav) {
        yearRailNav.innerHTML = grouped
          .map(
            ([year, items]) =>
              `<a href="#year-${core.escapeHtml(year)}">${core.escapeHtml(year)} <span>(${items.length})</span></a>`
          )
          .join("");
      }

      listEl.innerHTML = grouped
        .map(([year, items]) => {
          const countLabel = t(
            items.length === 1 ? "publications.yearCountOne" : "publications.yearCountMany",
            { count: items.length }
          );
          return `
            <section class="publication-year" id="year-${core.escapeHtml(year)}" aria-labelledby="heading-year-${core.escapeHtml(year)}">
              <div class="publication-year-heading">
                <h2 id="heading-year-${core.escapeHtml(year)}">${core.escapeHtml(year)}</h2>
                <p>${core.escapeHtml(countLabel)}</p>
              </div>
              <div class="publication-year-items">
                ${items.map((pub) => renderPublicationItem(pub, { compact: false })).join("")}
              </div>
            </section>
          `;
        })
        .join("");

      bindBibtexCopyButtons(listEl);
      setupYearObserver();
    };

    filterButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        state.topic = btn.getAttribute("data-topic-filter") || "all";
        render();
      });
    });

    if (searchInput) {
      searchInput.addEventListener("input", (event) => {
        state.query = event.target.value || "";
        render();
      });
    }

    if (keyOnlyCheckbox) {
      keyOnlyCheckbox.addEventListener("change", (event) => {
        state.keyOnly = Boolean(event.target.checked);
        render();
      });
    }

    window.addEventListener("site:languagechange", render);
    render();
  };

  /* ------------------------------------------------------------------------
     Bootstrap
     ------------------------------------------------------------------------ */
  const init = async () => {
    if (window.SiteI18n && window.SiteI18n.ready) {
      await window.SiteI18n.ready;
    }
    setupNavigation();
    setupEmailCopy();
    setupMonographTabs();
    setupPortfolioFilter();
    setupLightbox();
    await Promise.all([setupHomePublications(), setupPublicationsArchive()]);
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
