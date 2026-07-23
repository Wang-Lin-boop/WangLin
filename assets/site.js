(() => {
  "use strict";

  const i18n = window.SiteI18n;
  const t = (key, variables = {}) => i18n?.t(key, variables) ?? key;

  const TOPIC_KEYS = {
    ai: "topics.ai",
    structure: "topics.structure",
    discovery: "topics.discovery"
  };

  const publicationLists = [...document.querySelectorAll("[data-publication-list]")];
  const publicationCountNodes = () => [...document.querySelectorAll("[data-publication-count]")];
  const filterButtons = [...document.querySelectorAll("[data-publication-filter]")];
  const searchInput = document.querySelector("[data-publication-search]");
  const statusNode = document.querySelector("[data-publication-status]");
  const yearNavigation = document.querySelector("[data-year-navigation]");
  let publications = [];
  let activeFilter = "all";
  let yearObserver;

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

  const topicLabel = (topics = []) => {
    const labels = topics.map((topic) => TOPIC_KEYS[topic]).filter(Boolean).map((key) => t(key));
    return labels.length ? labels.join(" · ") : t("topics.article");
  };

  const formatAuthors = (authors = [], compact = false) => {
    let visibleAuthors = authors;
    let hasOmittedAuthors = false;

    if (compact && authors.length > 7) {
      visibleAuthors = authors.slice(0, 6);
      hasOmittedAuthors = true;
    }

    const names = visibleAuthors.map((author) => {
      const normalizedAuthor = normalizeText(author);
      if (normalizedAuthor === "others") return `<em>${escapeHtml(t("publications.etAl"))}</em>`;

      const safeName = escapeHtml(author);
      return normalizedAuthor === "lin wang"
        ? `<strong class="self-author">${safeName}</strong>`
        : safeName;
    });

    if (hasOmittedAuthors) {
      names.push(escapeHtml(t("publications.etAl")));
    }

    return names.join(", ");
  };

  const publicationMarkup = (publication, compact = false) => {
    const title = escapeHtml(publication.title);
    const url = escapeHtml(publication.url || "#");
    const year = escapeHtml(publication.year);
    const venue = escapeHtml(publication.venue || "Publication");
    const volume = publication.volume ? ` ${escapeHtml(publication.volume)}` : "";
    const issue = publication.issue ? `(${escapeHtml(publication.issue)})` : "";
    const pages = publication.pages ? `, ${escapeHtml(publication.pages)}` : "";

    return `
      <article class="publication-item">
        <p class="publication-item-year">${year}</p>
        <div>
          <h3><a href="${url}" target="_blank" rel="noreferrer">${title}</a></h3>
          <p class="publication-authors">${formatAuthors(publication.authors, compact)}</p>
          <p class="publication-venue">${venue}${volume}${issue}${pages}</p>
        </div>
        <p class="publication-topic">${escapeHtml(topicLabel(publication.topics))}</p>
      </article>
    `;
  };

  const buildYearNavigation = (groups) => {
    if (!yearNavigation) return;

    yearNavigation.innerHTML = groups
      .map(
        ([year, items], index) =>
          `<a href="#year-${escapeHtml(year)}"${index === 0 ? ' aria-current="true"' : ""}>${escapeHtml(year)} <span aria-label="${escapeHtml(t("publications.countAria", { count: items.length }))}">(${items.length})</span></a>`
      )
      .join("");

    yearObserver?.disconnect();
    if (!("IntersectionObserver" in window)) return;

    const links = [...yearNavigation.querySelectorAll("a")];
    const setCurrentYear = (year) => {
      links.forEach((link) => {
        if (link.getAttribute("href") === `#year-${year}`) {
          link.setAttribute("aria-current", "true");
        } else {
          link.removeAttribute("aria-current");
        }
      });
    };

    yearObserver = new IntersectionObserver(
      (entries) => {
        const visibleEntry = entries.find((entry) => entry.isIntersecting);
        if (visibleEntry) {
          setCurrentYear(visibleEntry.target.dataset.publicationYear);
        }
      },
      { rootMargin: "-24% 0px -66% 0px", threshold: 0 }
    );

    document.querySelectorAll("[data-publication-year]").forEach((section) => {
      yearObserver.observe(section);
    });
  };

  const renderFullList = (container, items) => {
    if (!items.length) {
      container.innerHTML = `<p class="empty-state">${escapeHtml(t("publications.empty"))}</p>`;
      buildYearNavigation([]);
      return;
    }

    const grouped = new Map();
    items.forEach((publication) => {
      const year = String(publication.year);
      if (!grouped.has(year)) grouped.set(year, []);
      grouped.get(year).push(publication);
    });

    const groups = [...grouped.entries()];
    container.innerHTML = groups
      .map(
        ([year, yearItems]) => `
          <section class="publication-year" id="year-${escapeHtml(year)}" data-publication-year="${escapeHtml(year)}" aria-labelledby="year-${escapeHtml(year)}-heading">
            <header class="publication-year-heading">
              <h2 id="year-${escapeHtml(year)}-heading">${escapeHtml(year)}</h2>
              <p>${escapeHtml(t(yearItems.length === 1 ? "publications.workCountOne" : "publications.workCount", { count: yearItems.length }))}</p>
            </header>
            ${yearItems.map((item) => publicationMarkup(item)).join("")}
          </section>
        `
      )
      .join("");

    buildYearNavigation(groups);
  };

  const renderCompactList = (container, items) => {
    const limit = Number.parseInt(container.dataset.publicationLimit || "6", 10);
    container.innerHTML = items
      .slice(0, Number.isFinite(limit) ? limit : 6)
      .map((item) => publicationMarkup(item, true))
      .join("");
  };

  const filteredPublications = () => {
    const query = normalizeText(searchInput?.value || "");

    return publications.filter((publication) => {
      const matchesTopic =
        activeFilter === "all" || (publication.topics || []).includes(activeFilter);
      const haystack = normalizeText(
        [
          publication.title,
          publication.venue,
          publication.year,
          publication.type,
          ...(publication.authors || [])
        ].join(" ")
      );
      const matchesSearch = !query || haystack.includes(query);
      return matchesTopic && matchesSearch;
    });
  };

  const renderPublications = () => {
    const filtered = filteredPublications();

    publicationLists.forEach((container) => {
      if (container.dataset.publicationLimit) {
        renderCompactList(container, publications);
      } else {
        renderFullList(container, filtered);
      }
    });

    if (statusNode) {
      statusNode.textContent = t(filtered.length === 1 ? "publications.statusOne" : "publications.status", { shown: filtered.length, total: publications.length });
    }
  };

  const showPublicationError = () => {
    publicationLists.forEach((container) => {
      container.innerHTML = `<p class="empty-state">${t("publications.error")}</p>`;
    });
    if (statusNode) statusNode.textContent = t("publications.unavailable");
  };

  const initializePublications = async () => {
    if (!publicationLists.length && !publicationCountNodes().length) return;

    try {
      const response = await fetch("./data/publications.json");
      if (!response.ok) throw new Error(`Publication request failed: ${response.status}`);
      const data = await response.json();
      if (!Array.isArray(data)) throw new TypeError("Publication data is not an array");

      publications = [...data].sort((a, b) => {
        const yearDifference = Number(b.year) - Number(a.year);
        return yearDifference || String(a.title).localeCompare(String(b.title));
      });

      publicationCountNodes().forEach((node) => {
        node.textContent = String(publications.length);
      });
      renderPublications();
    } catch (error) {
      console.error(error);
      showPublicationError();
    }
  };

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      activeFilter = button.dataset.publicationFilter || "all";
      filterButtons.forEach((candidate) => {
        const isActive = candidate === button;
        candidate.classList.toggle("is-active", isActive);
        candidate.setAttribute("aria-pressed", String(isActive));
      });
      renderPublications();
    });
  });

  searchInput?.addEventListener("input", renderPublications);

  const navToggle = document.querySelector("[data-nav-toggle]");
  const primaryNav = document.querySelector("[data-primary-nav]");

  const closeNavigation = () => {
    navToggle?.setAttribute("aria-expanded", "false");
    primaryNav?.classList.remove("is-open");
    document.body.classList.remove("nav-open");
  };

  navToggle?.addEventListener("click", () => {
    const isOpen = navToggle.getAttribute("aria-expanded") === "true";
    navToggle.setAttribute("aria-expanded", String(!isOpen));
    primaryNav?.classList.toggle("is-open", !isOpen);
    document.body.classList.toggle("nav-open", !isOpen);
  });

  primaryNav?.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", closeNavigation);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeNavigation();
  });

  window.matchMedia("(min-width: 821px)").addEventListener("change", (event) => {
    if (event.matches) closeNavigation();
  });

  document.querySelectorAll("[data-current-year]").forEach((node) => {
    node.textContent = String(new Date().getFullYear());
  });

  document.addEventListener("site:languagechange", () => {
    if (publications.length) {
      publicationCountNodes().forEach((node) => {
        node.textContent = String(publications.length);
      });
      renderPublications();
    }
  });

  initializePublications();
})();
