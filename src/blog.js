/* Páginas do blog: só o menu (as demais páginas do site usam src/app.js). */
(function () {
  "use strict";
  var doc = document;
  var toggle = doc.querySelector(".nav-toggle");
  var panel = doc.querySelector(".site-nav");
  var subToggle = doc.querySelector(".subnav-toggle");
  var sub = doc.querySelector("#submenu-participar");
  if (!toggle || !panel) return;

  function setMenu(open) {
    toggle.setAttribute("aria-expanded", String(open));
    panel.classList.toggle("is-open", open);
    toggle.querySelector(".nav-toggle__label").textContent = open ? "Fechar" : "Menu";
  }
  function setSub(open) {
    if (!subToggle || !sub) return;
    subToggle.setAttribute("aria-expanded", String(open));
    sub.classList.toggle("is-open", open);
  }
  toggle.addEventListener("click", function () { setMenu(toggle.getAttribute("aria-expanded") !== "true"); });
  if (subToggle) subToggle.addEventListener("click", function () { setSub(subToggle.getAttribute("aria-expanded") !== "true"); });
  doc.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if (sub && sub.classList.contains("is-open")) { setSub(false); subToggle.focus(); }
    else if (panel.classList.contains("is-open")) { setMenu(false); toggle.focus(); }
  });
  doc.addEventListener("click", function (e) {
    if (sub && sub.classList.contains("is-open") && !e.target.closest(".site-nav__group")) setSub(false);
  });
  var header = doc.querySelector(".site-header");
  window.addEventListener("scroll", function () { header.classList.toggle("is-scrolled", window.scrollY > 8); }, { passive: true });
})();
