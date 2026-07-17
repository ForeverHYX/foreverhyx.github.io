(function () {
  "use strict";

  function init() {
    setFooterYear();
    initActiveRoutes();
    initPageEntry();
    initMobileMenu();
    initThemeToggle();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { passive: true });
  } else {
    init();
  }

  function setFooterYear() {
    var el = document.getElementById("footerYear");
    if (el) el.textContent = String(new Date().getFullYear());
  }

  function initActiveRoutes() {
    var root = document.documentElement;
    root.classList.add("nav-booting");
    var path = window.location.pathname || "/";
    var links = document.querySelectorAll(
      ".nav-link[data-route], .nav-mobile-link[data-route]"
    );

    for (var i = 0; i < links.length; i++) {
      var link = links[i];
      var route = link.getAttribute("data-route") || "";
      var isActive =
        route === "/"
          ? path === "/"
          : path === route || path.indexOf(route + "/") === 0;
      link.setAttribute("data-active", isActive ? "true" : "false");
      if (isActive) {
        link.setAttribute("aria-current", "page");
      } else {
        link.removeAttribute("aria-current");
      }
    }
    window.requestAnimationFrame(function () {
      root.classList.remove("nav-booting");
    });
  }

  function initPageEntry() {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    var cards = document.querySelectorAll(
      ".site-main .home-glass, .site-main .home-liquid-card"
    );
    var visibleBodies = [];
    var viewportHeight = Math.max(window.innerHeight || 0, 1);
    var maxAnimatedHeight = viewportHeight * 1.35;

    for (var i = 0; i < cards.length; i++) {
      var card = cards[i];
      var parentMaterial = card.parentElement
        ? card.parentElement.closest(".home-glass, .home-liquid-card")
        : null;
      if (parentMaterial) continue;

      var body = card.querySelector(
        ":scope > .home-glass-body, :scope > .home-liquid-body"
      );
      if (!body) continue;

      var rect = body.getBoundingClientRect();
      if (
        rect.bottom > -40 &&
        rect.top < viewportHeight + 80 &&
        rect.height <= maxAnimatedHeight
      ) {
        visibleBodies.push(body);
      }
    }

    if (!visibleBodies.length) return;

    window.requestAnimationFrame(function () {
      for (var index = 0; index < visibleBodies.length; index++) {
        (function (body, order) {
          body.style.setProperty(
            "--page-enter-delay",
            Math.min(order, 3) * 24 + "ms"
          );
          body.classList.add("page-enter");

          var release = function () {
            body.classList.remove("page-enter");
            body.style.removeProperty("--page-enter-delay");
            body.removeEventListener("animationend", handleAnimationEnd);
          };
          var handleAnimationEnd = function (event) {
            if (
              event.target === body &&
              event.animationName === "pageContentEnter"
            ) {
              release();
            }
          };
          body.addEventListener("animationend", handleAnimationEnd);
          window.setTimeout(release, 520);
        })(visibleBodies[index], index);
      }
    });
  }

  function initMobileMenu() {
    var navCluster = document.getElementById("navCluster");
    var trigger = document.getElementById("navMobileTrigger");
    var panel = document.getElementById("navMobilePanel");
    var open = false;

    if (!navCluster || !trigger || !panel) return;
    panel.inert = true;

    function setOpen(nextOpen) {
      open = nextOpen;
      panel.classList.toggle("open", open);
      panel.setAttribute("aria-hidden", open ? "false" : "true");
      panel.inert = !open;
      trigger.setAttribute("aria-expanded", open ? "true" : "false");
      trigger.setAttribute("title", open ? "Close Menu" : "Open Menu");
      trigger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    }

    trigger.addEventListener("click", function (event) {
      event.stopPropagation();
      setOpen(!open);
    });

    document.addEventListener("click", function (event) {
      if (!open) return;
      if (!navCluster.contains(event.target)) setOpen(false);
    });

    var links = panel.querySelectorAll("a");
    for (var i = 0; i < links.length; i++) {
      links[i].addEventListener("click", function () {
        setOpen(false);
      });
    }

    document.addEventListener("keydown", function (event) {
      if (open && event.key === "Escape") {
        event.preventDefault();
        setOpen(false);
        trigger.focus({ preventScroll: true });
      }
    });
  }

  function initThemeToggle() {
    var toggle = document.getElementById("themeToggle");
    if (!toggle) return;

    function activeTheme() {
      return document.documentElement.getAttribute("data-theme") || "light";
    }

    function syncIcons(theme) {
      var isDark = theme === "dark";
      var moon = toggle.querySelector(".theme-icon-moon");
      var sun = toggle.querySelector(".theme-icon-sun");
      if (moon) moon.style.display = isDark ? "none" : "";
      if (sun) sun.style.display = isDark ? "" : "none";
      var label = isDark ? "Switch to light mode" : "Switch to dark mode";
      toggle.setAttribute("aria-label", label);
      toggle.setAttribute("title", label);
      toggle.setAttribute("aria-pressed", isDark ? "true" : "false");
    }

    syncIcons(activeTheme());

    toggle.addEventListener("click", function () {
      var nextTheme = activeTheme() === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", nextTheme);
      document.documentElement.style.colorScheme = nextTheme;
      try {
        localStorage.setItem("theme", nextTheme);
      } catch (e) {
        // localStorage can be unavailable in strict privacy modes.
      }
      syncIcons(nextTheme);
    });
  }
})();
