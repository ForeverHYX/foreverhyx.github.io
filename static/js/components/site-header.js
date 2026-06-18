(function () {
  "use strict";

  function init() {
    setFooterYear();
    initActiveRoutes();
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
    var path = window.location.pathname || "/";
    var links = document.querySelectorAll(
      ".nav-link[data-route], .nav-mobile-link[data-route]"
    );

    for (var i = 0; i < links.length; i++) {
      var link = links[i];
      var route = link.getAttribute("data-route") || "";
      var isActive = route === "/" ? path === "/" : path.indexOf(route) === 0;
      link.setAttribute("data-active", isActive ? "true" : "false");
    }
  }

  function initMobileMenu() {
    var navCluster = document.getElementById("navCluster");
    var trigger = document.getElementById("navMobileTrigger");
    var panel = document.getElementById("navMobilePanel");
    var openIcon = trigger ? trigger.querySelector(".menu-icon-open") : null;
    var closeIcon = trigger ? trigger.querySelector(".menu-icon-close") : null;
    var open = false;

    if (!navCluster || !trigger || !panel) return;

    function setOpen(nextOpen) {
      open = nextOpen;
      panel.classList.toggle("open", open);
      trigger.setAttribute("aria-expanded", open ? "true" : "false");
      trigger.setAttribute("title", open ? "Close Menu" : "Open Menu");
      trigger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      if (openIcon) openIcon.style.display = open ? "none" : "";
      if (closeIcon) closeIcon.style.display = open ? "" : "none";
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
  }

  function initThemeToggle() {
    var toggle = document.getElementById("themeToggle");
    if (!toggle) return;

    function activeTheme() {
      return document.documentElement.getAttribute("data-theme") || "light";
    }

    function syncIcons(theme) {
      var moon = toggle.querySelector(".theme-icon-moon");
      var sun = toggle.querySelector(".theme-icon-sun");
      if (moon) moon.style.display = theme === "dark" ? "none" : "";
      if (sun) sun.style.display = theme === "dark" ? "" : "none";
    }

    syncIcons(activeTheme());

    toggle.addEventListener("click", function () {
      var nextTheme = activeTheme() === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", nextTheme);
      document.documentElement.style.colorScheme = nextTheme;
      localStorage.setItem("theme", nextTheme);
      syncIcons(nextTheme);
    });
  }
})();
