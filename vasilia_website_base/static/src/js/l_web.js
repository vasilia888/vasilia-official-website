/* global window, document */
(function () {
  "use strict";

  var lwebBound = false;
  var lwebStatsObserver = null;
  var lwebAnimatingStats = false;
  var lwebOriginalScrollRestoration = null;

  function onReady(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  function updateBodyMode() {
    if (document.querySelector(".lweb-page")) {
      document.body.classList.add("lweb-site");
    } else {
      document.body.classList.remove("lweb-site");
      document.body.classList.remove("lweb-no-scroll");
    }
  }

  function updateTopnavScrolled() {
    var topnav = document.querySelector(".topnav");
    if (!topnav) return;
    if (window.scrollY > 50) topnav.classList.add("scrolled");
    else topnav.classList.remove("scrolled");
  }

  function openMenu() {
    var menu = document.querySelector(".mobile-menu");
    if (!menu) return;
    menu.classList.add("lweb-open");
    document.body.classList.add("lweb-no-scroll");
  }

  function closeMenu() {
    var menu = document.querySelector(".mobile-menu");
    if (!menu) return;
    menu.classList.remove("lweb-open");
    document.body.classList.remove("lweb-no-scroll");
  }

  function setupStatsAnimation() {
    var statSection = document.querySelector("[data-lweb-stats]");
    if (!statSection) return;

    var items = statSection.querySelectorAll(".lweb-stat");
    var numbers = statSection.querySelectorAll("[data-lweb-number]");

    function animateNumber(el, target, suffix, duration) {
      var start = 0;
      var startTime = performance.now();
      function tick(now) {
        var elapsed = now - startTime;
        var progress = Math.min(elapsed / duration, 1);
        var easeOut = 1 - Math.pow(1 - progress, 3);
        var current = Math.floor(start + (target - start) * easeOut);
        el.textContent = String(current) + (suffix || "");
        if (progress < 1) window.requestAnimationFrame(tick);
      }
      window.requestAnimationFrame(tick);
    }

    function animate() {
      if (lwebAnimatingStats) return;
      lwebAnimatingStats = true;
      items.forEach(function (item, idx) {
        window.setTimeout(function () {
          item.classList.add("lweb-animate");
        }, idx * 150);
      });

      numbers.forEach(function (el, idx) {
        var target = parseInt(el.getAttribute("data-lweb-number") || "0", 10);
        var suffix = el.getAttribute("data-lweb-suffix") || "";
        window.setTimeout(function () {
          el.classList.add("lweb-animate");
          animateNumber(el, target, suffix, 1500);
        }, 200 + idx * 200);
      });
    }

    if (lwebStatsObserver) lwebStatsObserver.disconnect();
    lwebAnimatingStats = false;
    lwebStatsObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            animate();
            if (lwebStatsObserver) lwebStatsObserver.disconnect();
          }
        });
      },
      { threshold: 0.3 }
    );
    lwebStatsObserver.observe(statSection);
  }

  function updateBackToTopVisibility() {
    var btn = document.querySelector(".back-to-top");
    if (!btn) return;
    if (window.scrollY > 300) btn.classList.add("show");
    else btn.classList.remove("show");
  }

  function setupProductFilters() {
    var page = document.querySelector(".products-page");
    if (!page) return;

    var cards = Array.prototype.slice.call(page.querySelectorAll(".product-card"));
    if (!cards.length) return;

    var catButtons = Array.prototype.slice.call(page.querySelectorAll(".cat-btn[data-category]"));
    var priceRadios = Array.prototype.slice.call(page.querySelectorAll('input[name="price-range"]'));
    var sortSelect = page.querySelector('[data-sort="products"]');
    var resetBtn = page.querySelector(".reset-btn");
    var resultsCount = page.querySelector(".results-count");
    var grid = page.querySelector(".grid.grid-3");

    var state = {
      category: null,
      price: "all",
      sort: sortSelect ? sortSelect.value : "popular",
    };

    function inPriceRange(price, range) {
      if (range === "all") return true;
      if (range === "0-80") return price >= 0 && price <= 80;
      if (range === "80-150") return price > 80 && price <= 150;
      if (range === "150-250") return price > 150 && price <= 250;
      if (range === "250+") return price > 250;
      return true;
    }

    function sortCards(visibleCards) {
      var sorted = visibleCards.slice();
      if (state.sort === "price-asc") {
        sorted.sort(function (a, b) {
          return parseFloat(a.dataset.price || "0") - parseFloat(b.dataset.price || "0");
        });
      } else if (state.sort === "price-desc") {
        sorted.sort(function (a, b) {
          return parseFloat(b.dataset.price || "0") - parseFloat(a.dataset.price || "0");
        });
      } else if (state.sort === "newest") {
        sorted.sort(function (a, b) {
          return parseInt(b.dataset.id || "0", 10) - parseInt(a.dataset.id || "0", 10);
        });
      } else {
        // popular
        sorted.sort(function (a, b) {
          return parseInt(b.dataset.reviews || "0", 10) - parseInt(a.dataset.reviews || "0", 10);
        });
      }
      return sorted;
    }

    function render() {
      var visible = cards.filter(function (card) {
        var categoryOk = !state.category || (card.dataset.category || "") === state.category;
        var price = parseFloat(card.dataset.price || "0");
        var priceOk = inPriceRange(price, state.price);
        return categoryOk && priceOk;
      });

      cards.forEach(function (card) {
        card.style.display = "none";
      });

      var sorted = sortCards(visible);
      if (grid) {
        sorted.forEach(function (card) {
          card.style.display = "";
          grid.appendChild(card);
        });
      }

      if (resultsCount) {
        resultsCount.innerHTML = sorted.length + "<span> 款产品</span>";
      }
    }

    catButtons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var category = btn.getAttribute("data-category");
        state.category = state.category === category ? null : category;
        catButtons.forEach(function (b) {
          b.classList.toggle("is-active", b === btn && state.category === category);
        });
        render();
      });
    });

    priceRadios.forEach(function (radio) {
      radio.addEventListener("change", function () {
        if (radio.checked) {
          state.price = radio.value || "all";
          render();
        }
      });
    });

    if (sortSelect) {
      sortSelect.addEventListener("change", function () {
        state.sort = sortSelect.value || "popular";
        render();
      });
    }

    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        state.category = null;
        state.price = "all";
        state.sort = "popular";
        catButtons.forEach(function (b) {
          b.classList.remove("is-active");
        });
        priceRadios.forEach(function (radio) {
          radio.checked = (radio.value || "all") === "all";
        });
        if (sortSelect) sortSelect.value = "popular";
        render();
      });
    }

    render();
  }

  function parseHTML(html) {
    var parser = new window.DOMParser();
    return parser.parseFromString(html, "text/html");
  }

  function restoreScrollY(scrollY) {
    if (typeof scrollY !== "number") return;
    // Avoid smooth scrolling interfering with a "seamless" switch.
    var rootStyle = document.documentElement && document.documentElement.style;
    var prevBehavior = rootStyle ? rootStyle.scrollBehavior : "";
    if (rootStyle) rootStyle.scrollBehavior = "auto";

    function set() {
      window.scrollTo(0, scrollY);
    }

    // Multiple attempts: some scripts/images/layout shifts can reset scroll shortly after DOM swap.
    set();
    window.requestAnimationFrame(function () {
      set();
      window.requestAnimationFrame(function () {
        set();
      });
    });
    window.setTimeout(set, 50);
    window.setTimeout(set, 250);

    if (rootStyle) {
      window.setTimeout(function () {
        rootStyle.scrollBehavior = prevBehavior || "";
      }, 300);
    }
  }

  function replaceWrapwrapFromDoc(doc) {
    var current = document.querySelector("#wrapwrap");
    var next = doc.querySelector("#wrapwrap");
    if (!current || !next) return false;
    current.replaceWith(next);

    // keep title/lang in sync
    if (doc.title) document.title = doc.title;
    var nextLang = doc.documentElement && doc.documentElement.getAttribute("lang");
    if (nextLang) document.documentElement.setAttribute("lang", nextLang);
    return true;
  }

  function doSoftNavigate(url, opts) {
    var scrollY = (opts && typeof opts.scrollY === "number") ? opts.scrollY : window.scrollY;
    var push = opts && opts.push === false ? false : true;

    document.documentElement.classList.add("lweb-soft-nav");
    return window
      .fetch(url, {
        method: "GET",
        credentials: "include",
        headers: { "X-Requested-With": "XMLHttpRequest" },
      })
      .then(function (res) {
        if (!res.ok) throw new Error("Bad response");
        return res.text();
      })
      .then(function (html) {
        var doc = parseHTML(html);
        var ok = replaceWrapwrapFromDoc(doc);
        if (!ok) throw new Error("No wrapwrap found");
        if (push) window.history.pushState({ lweb: true }, "", url);

        // re-init features for newly injected DOM
        updateBodyMode();
        updateTopnavScrolled();
        updateBackToTopVisibility();
        setupStatsAnimation();

        // keep user position (best-effort)
        restoreScrollY(scrollY);
      })
      .catch(function () {
        // fallback to classic navigation (keeps existing behavior)
        window.location.href = url;
      })
      .finally(function () {
        window.setTimeout(function () {
          document.documentElement.classList.remove("lweb-soft-nav");
        }, 50);
      });
  }

  function isLikelyLangSegment(seg) {
    if (!seg) return false;
    // en, fr, zh, en_US, zh_CN
    return /^[a-z]{2}([_-][A-Za-z]{2})?$/.test(seg);
  }

  function normalizeUrlCode(urlCode) {
    if (!urlCode) return "";
    return String(urlCode).replace("-", "_");
  }

  function buildTargetUrlFromCurrent(urlCode) {
    var target = normalizeUrlCode(urlCode);
    if (!target) return null;

    var u = new window.URL(window.location.href);
    var parts = (u.pathname || "/").split("/").filter(Boolean);
    var first = parts.length ? parts[0] : "";
    var hasPrefix = isLikelyLangSegment(first);
    var wantZh = /^zh/i.test(target);

    // Symmetric behavior:
    // - zh -> en : add/replace lang prefix with target
    // - en -> zh : remove lang prefix (common Odoo default-lang setup)
    if (wantZh) {
      if (hasPrefix) parts.shift();
    } else {
      if (hasPrefix) parts[0] = target;
      else parts.unshift(target);
    }

    u.pathname = "/" + parts.join("/");
    return u.pathname + u.search + u.hash;
  }

  function setOdooLangCookie(urlCode, returnToUrl) {
    // Best-effort: set website_lang cookie via standard endpoint, but don't rely on its redirect HTML.
    try {
      var base = "/website/lang/" + encodeURIComponent(urlCode);
      var r = returnToUrl || window.location.pathname + window.location.search + window.location.hash;
      var setUrl = base + "?r=" + encodeURIComponent(r);
      return window.fetch(setUrl, { method: "GET", credentials: "include" }).catch(function () {});
    } catch (e) {
      return Promise.resolve();
    }
  }

  function getOdooReturnUrlFromSetter(href) {
    try {
      var u = new window.URL(href, window.location.origin);
      if ((u.pathname || "").indexOf("/website/lang/") !== 0) return null;
      var r = u.searchParams.get("r");
      if (!r) return null;
      // r is usually a path (may include query/hash). Ensure it is a same-origin relative URL.
      if (r.indexOf("http://") === 0 || r.indexOf("https://") === 0) {
        var ru = new window.URL(r);
        if (ru.origin !== window.location.origin) return null;
        return ru.pathname + ru.search + ru.hash;
      }
      if (r[0] !== "/") r = "/" + r;
      return r;
    } catch (e) {
      return null;
    }
  }

  function pickBestTargetUrl(urlCode, href) {
    // 1) If href is /website/lang/... use r= (Odoo's "return URL") if it points to a real page.
    var r = getOdooReturnUrlFromSetter(href);
    if (r && r !== "/") return r;

    // 2) If href points to home while we're not on home, ignore it and compute from current URL.
    try {
      var hu = new window.URL(href, window.location.origin);
      if (hu.pathname === "/" && window.location.pathname !== "/") {
        return buildTargetUrlFromCurrent(urlCode) || href;
      }
    } catch (e) {
      // ignore
    }

    // 3) Otherwise: href is already a localized page URL (works for zh->en in your setup).
    return href || buildTargetUrlFromCurrent(urlCode);
  }

  function doSoftLangSwitch(urlCode, href, opts) {
    var scrollY = (opts && typeof opts.scrollY === "number") ? opts.scrollY : window.scrollY;
    var push = opts && opts.push === false ? false : true;

    var targetUrl = pickBestTargetUrl(urlCode, href);
    if (!targetUrl) return doSoftNavigate(href, opts);

    document.documentElement.classList.add("lweb-soft-nav");
    return setOdooLangCookie(urlCode, targetUrl)
      .then(function () {
        return window.fetch(targetUrl, {
          method: "GET",
          credentials: "include",
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
      })
      .then(function (res) {
        if (!res || !res.ok) throw new Error("Bad response");
        return res.text();
      })
      .then(function (html) {
        var doc = parseHTML(html);
        var ok = replaceWrapwrapFromDoc(doc);
        if (!ok) throw new Error("No wrapwrap found");
        if (push) window.history.pushState({ lweb: true }, "", targetUrl);

        updateBodyMode();
        updateTopnavScrolled();
        updateBackToTopVisibility();
        setupStatsAnimation();

        restoreScrollY(scrollY);
      })
      .catch(function () {
        window.location.href = href || targetUrl;
      })
      .finally(function () {
        window.setTimeout(function () {
          document.documentElement.classList.remove("lweb-soft-nav");
        }, 50);
      });
  }

  function bindOnce() {
    if (lwebBound) return;
    lwebBound = true;

    // Make scroll restoration deterministic across PJAX swaps.
    try {
      if (typeof window.history !== "undefined" && "scrollRestoration" in window.history) {
        lwebOriginalScrollRestoration = window.history.scrollRestoration;
        window.history.scrollRestoration = "manual";
      }
    } catch (e) {
      // ignore
    }

    // IMPORTANT:
    // Let Odoo's native `.js_change_lang` flow handle language switches.
    // This keeps URL/lang prefix behavior consistent with standard website behavior.

    window.addEventListener(
      "scroll",
      function () {
        updateTopnavScrolled();
        updateBackToTopVisibility();
      },
      { passive: true }
    );

    // Event delegation so DOM swaps won't break interactions
    document.addEventListener("click", function (e) {
      var target = e.target;
      if (!target) return;

      if (target.closest && target.closest("[data-lweb-burger]")) {
        e.preventDefault();
        openMenu();
        return;
      }
      if (target.closest && target.closest("[data-lweb-close]")) {
        e.preventDefault();
        closeMenu();
        return;
      }
      if (target.matches && target.matches("[data-lweb-nav] a")) {
        closeMenu();
        return;
      }

      if (target.closest && target.closest(".back-to-top")) {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    });

    window.addEventListener("popstate", function () {
      doSoftNavigate(window.location.href, { scrollY: window.scrollY, push: false });
    });
  }

  function init() {
    updateBodyMode();
    updateTopnavScrolled();
    updateBackToTopVisibility();
    setupStatsAnimation();
    setupProductFilters();
  }

  // Bind as early as possible (do not wait for DOMContentLoaded),
  // to beat Odoo's own handlers and avoid navigation to homepage.
  bindOnce();

  onReady(function () {
    init();
  });
})();

