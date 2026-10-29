/* MRO Brasil 2027 — navegação e componentes interativos.
   Script clássico (sem módulos) para funcionar também em file://. */
(function () {
  "use strict";

  var doc = document;
  var $ = function (sel, root) { return (root || doc).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || doc).querySelectorAll(sel)); };
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var POPUP_KEY = "mro2027:perfil-popup-exibido";

  /* ------------------------------------------------------------------ */
  /* Rotas                                                               */
  /* ------------------------------------------------------------------ */
  var ROUTES = [
    { path: "participar/visitante", page: "visitante", nav: "visitante", parent: "participar", sections: { formulario: "visitante-formulario" } },
    { path: "participar/expositor", page: "expositor", nav: "expositor", parent: "participar", sections: { formulario: "expositor-formulario" } },
    { path: "participar", page: "participar", nav: "participar" },
    { path: "feira", page: "feira", nav: "feira", sections: { sobre: "feira-sobre", publico: "feira-publico", oportunidades: "feira-oportunidades", informacoes: "feira-informacoes" } },
    { path: "patrocinio", page: "patrocinio", nav: "patrocinio", sections: { formulario: "patrocinio-formulario" } },
    { path: "reviva-2026", page: "reviva", nav: "reviva", filters: ["fotos", "videos", "depoimentos"], sections: { "feira-virtual": "reviva-virtual" } },
    { path: "contato", page: "contato", nav: "contato" },
    { path: "", page: "inicio", nav: null }
  ];
  var NOT_FOUND = { path: null, page: "nao-encontrada", nav: null };
  var PROFILE_PAGES = { visitante: 1, expositor: 1, patrocinio: 1 };

  function parseHash() {
    var raw = location.hash;
    if (raw && raw.indexOf("#/") !== 0 && raw !== "#") return null; // âncora comum (não é rota)
    var rest = decodeURIComponent(raw.replace(/^#\/?/, "")).replace(/\/+$/, "").toLowerCase();
    for (var i = 0; i < ROUTES.length; i++) {
      var r = ROUTES[i];
      if (rest === r.path) return { route: r, extra: "" };
      if (r.path && rest.indexOf(r.path + "/") === 0) {
        var extra = rest.slice(r.path.length + 1);
        if ((r.sections && r.sections[extra]) || (r.filters && r.filters.indexOf(extra) > -1)) return { route: r, extra: extra };
      }
    }
    return { route: NOT_FOUND, extra: "" };
  }

  var currentPage = null;
  var firstRender = true;
  var metaDesc = $('meta[name="description"]');
  var announcer = $("#anuncio-rota");

  function render() {
    var parsed = parseHash();
    if (!parsed) return;
    var route = parsed.route;
    var extra = parsed.extra;
    var pageEl = $('[data-page="' + route.page + '"]');
    var samePage = currentPage === route.page;

    $$("[data-page]").forEach(function (el) { el.hidden = el !== pageEl; });
    doc.title = pageEl.getAttribute("data-title");
    if (metaDesc) metaDesc.setAttribute("content", pageEl.getAttribute("data-description"));

    $$(".site-nav [data-nav]").forEach(function (a) {
      var key = a.getAttribute("data-nav");
      if (key === route.nav) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
      a.classList.toggle("is-section", key === route.parent);
    });
    nav.close();

    Form.attach(pageEl);
    Gallery.setFilter(route.page === "reviva" ? (extra || "todos") : "todos");
    Carousel.setVisible(route.page === "inicio");

    var target = route.sections && extra && route.sections[extra] ? doc.getElementById(route.sections[extra]) : null;
    if (target) {
      scrollAndFocus(target, firstRender);
    } else if (!samePage) {
      if (!firstRender) {
        window.scrollTo(0, 0);
        var h1 = $("h1", pageEl);
        if (h1) h1.focus({ preventScroll: true });
      }
    }
    if (!samePage && !firstRender && announcer) announcer.textContent = doc.title;

    currentPage = route.page;
    firstRender = false;
  }

  function scrollAndFocus(section, instant) {
    var heading = $("h2", section) || section;
    if (!heading.hasAttribute("tabindex")) heading.setAttribute("tabindex", "-1");
    requestAnimationFrame(function () {
      section.scrollIntoView({ block: "start", behavior: instant || reduceMotion.matches ? "auto" : "smooth" });
      heading.focus({ preventScroll: true });
    });
  }

  /* ------------------------------------------------------------------ */
  /* Navegação principal                                                 */
  /* ------------------------------------------------------------------ */
  var nav = (function () {
    var toggle = $(".nav-toggle");
    var panel = $(".site-nav");
    var subToggle = $(".subnav-toggle");
    var sub = $("#submenu-participar");

    function setMenu(open) {
      toggle.setAttribute("aria-expanded", String(open));
      panel.classList.toggle("is-open", open);
      toggle.querySelector(".nav-toggle__label").textContent = open ? "Fechar" : "Menu";
    }
    function setSub(open) {
      subToggle.setAttribute("aria-expanded", String(open));
      sub.classList.toggle("is-open", open);
    }
    toggle.addEventListener("click", function () { setMenu(toggle.getAttribute("aria-expanded") !== "true"); });
    subToggle.addEventListener("click", function () { setSub(subToggle.getAttribute("aria-expanded") !== "true"); });

    doc.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      if (sub.classList.contains("is-open")) { setSub(false); subToggle.focus(); }
      else if (panel.classList.contains("is-open")) { setMenu(false); toggle.focus(); }
    });
    doc.addEventListener("click", function (e) {
      if (sub.classList.contains("is-open") && !e.target.closest(".site-nav__group")) setSub(false);
    });
    $(".site-nav__group").addEventListener("focusout", function (e) {
      if (!e.currentTarget.contains(e.relatedTarget)) setSub(false);
    });

    return { close: function () { setMenu(false); setSub(false); } };
  })();

  /* ------------------------------------------------------------------ */
  /* Diálogos                                                            */
  /* ------------------------------------------------------------------ */
  function setupDialog(dlg) {
    var returnTo = null;
    var skipReturn = false;
    dlg.addEventListener("close", function () {
      if (window.MROCarousel) window.MROCarousel.setDialog(false);
      if (!skipReturn && returnTo && doc.contains(returnTo) && returnTo.offsetParent !== null) returnTo.focus();
      else if (!skipReturn) $("#conteudo").focus({ preventScroll: true });
      skipReturn = false;
      returnTo = null;
    });
    dlg.addEventListener("click", function (e) {
      if (e.target === dlg) dlg.close(); // toque no fundo escurecido
    });
    $$("[data-dialog-close]", dlg).forEach(function (b) { b.addEventListener("click", function () { dlg.close(); }); });
    return {
      open: function (opener) {
        returnTo = opener || null;
        if (!dlg.open) dlg.showModal();
        if (window.MROCarousel) window.MROCarousel.setDialog(true);
      },
      closeForNavigation: function () { skipReturn = true; dlg.close(); },
      el: dlg
    };
  }

  /* Pop-up de perfil ------------------------------------------------- */
  var perfilDialog = setupDialog($("#dialog-perfil"));
  $$("[data-dialog-choice]", perfilDialog.el).forEach(function (a) {
    a.addEventListener("click", function (e) {
      perfilDialog.closeForNavigation();
      if (a.getAttribute("href") === location.hash) {
        e.preventDefault();
        var h1 = $("[data-page]:not([hidden]) h1");
        window.scrollTo(0, 0);
        if (h1) h1.focus({ preventScroll: true });
      }
    });
  });
  $$("[data-open-perfil]").forEach(function (b) {
    b.addEventListener("click", function () { perfilDialog.open(b); });
  });

  function maybeShowPopup() {
    var seen = false;
    try { seen = sessionStorage.getItem(POPUP_KEY) === "1"; } catch (err) { seen = false; }
    // "?sem-popup" na URL suprime o pop-up apenas para capturas de QA.
    if (seen || PROFILE_PAGES[currentPage] || /[?&]sem-popup\b/.test(location.search)) return;
    // Abre após a primeira rolagem ou 5 s, o que vier antes; não interrompe quem já escolheu um perfil.
    var timer = setTimeout(show, 5000);
    window.addEventListener("scroll", onScroll, { passive: true });
    function onScroll() { if (window.scrollY > 160) show(); }
    function show() {
      clearTimeout(timer);
      window.removeEventListener("scroll", onScroll);
      if (PROFILE_PAGES[currentPage] || doc.querySelector("dialog[open]")) return;
      try { sessionStorage.setItem(POPUP_KEY, "1"); } catch (err) { /* sem storage: exibe uma vez nesta página */ }
      perfilDialog.open(null);
    }
  }

  /* ------------------------------------------------------------------ */
  /* Carrossel                                                           */
  /* ------------------------------------------------------------------ */
  var Carousel = (function () {
    var root = $("#destaques");
    var slides = $$(".slide", root);
    var tabs = $$(".carousel__tab", root);
    var toggleBtn = $("[data-carousel-toggle]", root);
    var live = $("[data-carousel-live]", root);
    var names = ["MRO Brasil 2027", "Reviva 2026", "Associe-se à MANTAER"];
    var MS = 8000;
    var index = 0, timer = null, startedAt = 0, remaining = MS;
    var userPaused = reduceMotion.matches;
    var holds = { hover: false, focus: false, touch: false, hidden: false, dialog: false };
    var visible = true;
    root.style.setProperty("--carousel-ms", MS + "ms");

    function held() { return holds.hover || holds.focus || holds.touch || holds.hidden || holds.dialog; }
    function canPlay() { return !userPaused && visible; }

    function goTo(i, userAction) {
      index = (i + slides.length) % slides.length;
      slides.forEach(function (s, n) {
        var active = n === index;
        s.classList.toggle("is-active", active);
        s.setAttribute("aria-hidden", String(!active));
        if (active) s.removeAttribute("inert"); else s.setAttribute("inert", "");
      });
      tabs.forEach(function (t, n) { if (n === index) t.setAttribute("aria-current", "true"); else t.removeAttribute("aria-current"); });
      if (userAction) live.textContent = "Destaque " + (index + 1) + " de " + slides.length + ": " + names[index];
      restart();
    }

    function clear() { clearTimeout(timer); timer = null; }
    function restart() {
      clear();
      root.classList.remove("is-playing");
      void root.offsetWidth; // reinicia a barra de progresso
      remaining = MS;
      if (canPlay()) {
        root.classList.add("is-playing");
        if (!held()) schedule();
      }
      root.classList.toggle("is-hold", held());
    }
    function schedule() {
      clear();
      startedAt = Date.now();
      timer = setTimeout(function () { goTo(index + 1, false); }, remaining);
    }
    function updateHold() {
      root.classList.toggle("is-hold", held());
      if (!canPlay()) return;
      if (held()) {
        if (timer) { remaining = Math.max(400, remaining - (Date.now() - startedAt)); clear(); }
      } else if (!timer) {
        schedule();
      }
    }
    function setPaused(p) {
      userPaused = p;
      toggleBtn.querySelector("use").setAttribute("href", p ? "#i-play" : "#i-pause");
      toggleBtn.querySelector(".sr-only").textContent = p ? "Reproduzir destaques" : "Pausar destaques";
      restart();
    }

    $("[data-carousel-prev]", root).addEventListener("click", function () { goTo(index - 1, true); });
    $("[data-carousel-next]", root).addEventListener("click", function () { goTo(index + 1, true); });
    toggleBtn.addEventListener("click", function () { setPaused(!userPaused); });
    tabs.forEach(function (t, n) {
      t.addEventListener("click", function () { goTo(n, true); });
      t.addEventListener("keydown", function (e) {
        var d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
        if (!d) return;
        e.preventDefault();
        goTo(index + d, true);
        tabs[index].focus();
      });
    });

    root.addEventListener("mouseenter", function () { holds.hover = true; updateHold(); });
    root.addEventListener("mouseleave", function () { holds.hover = false; updateHold(); });
    root.addEventListener("focusin", function () { holds.focus = true; updateHold(); });
    root.addEventListener("focusout", function (e) { if (!root.contains(e.relatedTarget)) { holds.focus = false; updateHold(); } });
    doc.addEventListener("visibilitychange", function () { holds.hidden = doc.hidden; updateHold(); });

    /* Toque: deslizar troca o destaque; tocar pausa por alguns segundos. */
    var viewport = $(".carousel__viewport", root);
    var touchRelease = null, sx = 0, sy = 0, tracking = false;
    viewport.addEventListener("pointerdown", function (e) {
      if (e.pointerType === "mouse") return;
      tracking = true; sx = e.clientX; sy = e.clientY;
      clearTimeout(touchRelease); holds.touch = true; updateHold();
    });
    viewport.addEventListener("pointerup", function (e) {
      if (!tracking) return;
      tracking = false;
      var dx = e.clientX - sx, dy = e.clientY - sy;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.2) goTo(index + (dx < 0 ? 1 : -1), true);
      touchRelease = setTimeout(function () { holds.touch = false; updateHold(); }, 5000);
    });
    viewport.addEventListener("pointercancel", function () {
      tracking = false;
      touchRelease = setTimeout(function () { holds.touch = false; updateHold(); }, 5000);
    });

    reduceMotion.addEventListener && reduceMotion.addEventListener("change", function (e) { if (e.matches) setPaused(true); });

    setPaused(userPaused);
    goTo(0, false);

    return {
      setDialog: function (open) { holds.dialog = open; updateHold(); },
      setVisible: function (v) {
        if (v === visible) return;
        visible = v;
        restart();
      }
    };
  })();

  window.MROCarousel = Carousel;

  /* ------------------------------------------------------------------ */
  /* Galeria Reviva 2026                                                 */
  /* ------------------------------------------------------------------ */
  var Gallery = (function () {
    var list = $("[data-gallery]");
    var items = $$(".g-item", list);
    var count = $("[data-gallery-count]");
    var labels = { todos: "itens", fotos: "fotos", videos: "vídeos", depoimentos: "depoimentos" };
    var lb = setupDialog($("#dialog-lightbox"));
    var lbImg = $("[data-lightbox-img]");
    var lbCap = $("[data-lightbox-caption]");
    var lbCount = $("[data-lightbox-count]");
    var photos = [], pos = 0;

    function setFilter(f) {
      var n = 0;
      items.forEach(function (it) {
        var show = f === "todos" || it.getAttribute("data-type") === f;
        it.hidden = !show;
        if (show) n++;
      });
      $$(".filter").forEach(function (a) {
        if (a.getAttribute("data-filter") === f) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current");
      });
      count.textContent = "Exibindo " + n + " " + (n === 1 ? labels[f].replace(/s$/, "") : labels[f]);
    }

    function show(i) {
      pos = (i + photos.length) % photos.length;
      var btn = photos[pos];
      var thumb = $("img", btn);
      lbImg.src = btn.getAttribute("data-full");
      lbImg.alt = thumb.alt;
      lbCap.textContent = btn.getAttribute("data-caption");
      lbCount.textContent = (pos + 1) + " de " + photos.length;
    }

    list.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-lightbox]");
      if (!btn) return;
      photos = $$("[data-lightbox]", list).filter(function (b) { return !b.closest(".g-item").hidden; });
      show(photos.indexOf(btn));
      lb.open(btn);
    });
    $("[data-lightbox-prev]").addEventListener("click", function () { show(pos - 1); });
    $("[data-lightbox-next]").addEventListener("click", function () { show(pos + 1); });
    lb.el.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { e.preventDefault(); show(pos + 1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); show(pos - 1); }
    });
    lb.el.addEventListener("close", function () {
      // devolve o foco à miniatura correspondente à última imagem exibida
      if (photos[pos]) photos[pos].focus();
    });
    var lsx = 0;
    lb.el.addEventListener("pointerdown", function (e) { lsx = e.clientX; });
    lb.el.addEventListener("pointerup", function (e) {
      if (e.pointerType === "mouse") return;
      var dx = e.clientX - lsx;
      if (Math.abs(dx) > 50) show(pos + (dx < 0 ? 1 : -1));
    });

    return { setFilter: setFilter };
  })();

  /* ------------------------------------------------------------------ */
  /* Formulário demonstrativo                                            */
  /* ------------------------------------------------------------------ */
  var Form = (function () {
    var holder = doc.createElement("div");
    holder.className = "form-root";
    holder.appendChild($("#tpl-form").content.cloneNode(true));
    var form = $("[data-lead-form]", holder);
    var done = $("[data-form-done]", holder);
    var summary = $("[data-form-errors]", holder);
    var submitBtn = $("[data-submit]", holder);
    var empresaReq = $("[data-empresa-req]", holder);
    var hint = $("[data-profile-hint]", holder);
    var attempted = false, busy = false;

    var PROFILE = {
      visitante: { label: "Visitante", empresa: false, hint: "Empresa opcional. O registro de interesse não representa compra, não emite ingresso e não confirma credenciamento." },
      expositor: { label: "Expositor", empresa: true, hint: "Empresa obrigatória. A solicitação não reserva espaço nem confirma contratação." },
      patrocinador: { label: "Patrocinador", empresa: true, hint: "Empresa obrigatória. O registro não conclui patrocínio; as condições são tratadas pela organização." }
    };

    function field(name) { return form.elements[name]; }
    function profile() { var r = form.querySelector('input[name="perfil"]:checked'); return r ? r.value : "visitante"; }

    function setProfile(p) {
      var r = form.querySelector('input[name="perfil"][value="' + p + '"]');
      if (r) r.checked = true;
      applyProfile();
    }
    function applyProfile() {
      var cfg = PROFILE[profile()];
      var emp = field("empresa");
      emp.required = cfg.empresa;
      emp.setAttribute("aria-required", String(cfg.empresa));
      empresaReq.textContent = cfg.empresa ? "(obrigatório)" : "(opcional)";
      hint.textContent = cfg.hint;
      if (attempted) validate(false);
    }

    var rules = {
      nome: function (v) { return v.trim().length < 2 ? "Informe seu nome." : ""; },
      email: function (v) {
        v = v.trim();
        if (!v) return "Informe seu e-mail.";
        return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v) ? "" : "Informe um e-mail válido, por exemplo nome@empresa.com.br.";
      },
      empresa: function (v) { return PROFILE[profile()].empresa && !v.trim() ? "Informe a empresa. O campo é obrigatório para expositores e patrocinadores." : ""; },
      telefone: function (v) {
        var d = v.replace(/\D/g, "");
        return v.trim() && (d.length < 10 || d.length > 13) ? "Informe o telefone com DDD, por exemplo (11) 5041-2088." : "";
      }
    };
    var LABELS = { nome: "Nome", email: "E-mail", empresa: "Empresa", telefone: "Telefone" };

    function setError(name, msg) {
      var input = field(name);
      var out = $("#f-" + name + "-erro", holder);
      input.setAttribute("aria-invalid", msg ? "true" : "false");
      out.textContent = msg;
      out.hidden = !msg;
    }

    function validate(withSummary) {
      var errors = [];
      Object.keys(rules).forEach(function (name) {
        var msg = rules[name](field(name).value);
        setError(name, msg);
        if (msg) errors.push({ name: name, msg: msg });
      });
      var ul = $("ul", summary);
      ul.innerHTML = "";
      errors.forEach(function (er) {
        var li = doc.createElement("li");
        var a = doc.createElement("a");
        a.href = "#f-" + er.name;
        a.textContent = LABELS[er.name] + ": " + er.msg;
        a.addEventListener("click", function (e) { e.preventDefault(); field(er.name).focus(); });
        li.appendChild(a);
        ul.appendChild(li);
      });
      if (withSummary || !errors.length) summary.hidden = !errors.length;
      return errors;
    }

    form.addEventListener("change", function (e) { if (e.target.name === "perfil") applyProfile(); });
    form.addEventListener("input", function (e) {
      if (!attempted || !rules[e.target.name]) return;
      setError(e.target.name, rules[e.target.name](e.target.value));
    });
    form.addEventListener("focusout", function (e) {
      if (attempted && rules[e.target.name]) validate(false);
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (busy) return;
      attempted = true;
      var errors = validate(true);
      if (errors.length) { summary.focus(); return; }
      busy = true;
      submitBtn.disabled = true;
      submitBtn.setAttribute("aria-disabled", "true");
      submitBtn.firstChild.nodeValue = "Testando… ";
      var tested = PROFILE[profile()].label;
      window.MROLeads.enviar({
        perfil: profile(), nome: field("nome").value, email: field("email").value,
        empresa: field("empresa").value, telefone: field("telefone").value, mensagem: field("mensagem").value
      }).then(function () {
        $("[data-done-profile]", holder).textContent = "Perfil testado: " + tested + ".";
        clearValues();
        form.hidden = true;
        done.hidden = false;
        done.focus();
      }).catch(function () {
        summary.hidden = false;
        $("ul", summary).innerHTML = "<li>Não foi possível concluir o teste. Seus dados foram mantidos; tente novamente.</li>";
        summary.focus();
      }).then(function () {
        busy = false;
        submitBtn.disabled = false;
        submitBtn.removeAttribute("aria-disabled");
        submitBtn.firstChild.nodeValue = "Testar formulário ";
      });
    });

    function clearValues() {
      ["nome", "email", "empresa", "telefone", "mensagem"].forEach(function (n) { field(n).value = ""; });
      ["nome", "email", "empresa", "telefone"].forEach(function (n) { setError(n, ""); });
      summary.hidden = true;
      attempted = false;
    }

    $("[data-form-reset]", holder).addEventListener("click", function () {
      done.hidden = true;
      form.hidden = false;
      field("nome").focus();
    });

    // IDs únicos: o formulário existe uma única vez e é movido entre páginas.
    function attach(pageEl) {
      var slot = $(".form-slot", pageEl);
      if (!slot) return;
      if (holder.parentNode !== slot) slot.appendChild(holder);
      if (!done.hidden) { done.hidden = true; form.hidden = false; }
      setProfile(slot.getAttribute("data-profile"));
    }

    return { attach: attach };
  })();

  /* ------------------------------------------------------------------ */
  /* Inicialização                                                       */
  /* ------------------------------------------------------------------ */
  $(".skip-link").addEventListener("click", function (e) {
    e.preventDefault();
    var h1 = $("[data-page]:not([hidden]) h1");
    (h1 || $("#conteudo")).focus();
  });

  /* Entrada suave dos blocos ao rolar (desativada com movimento reduzido via CSS). */
  (function () {
    var targets = $$([
      ".intro__text", ".factsheet", ".section-intro", ".pillar", ".feature", ".service__inner",
      ".cols__head", ".cols__body", ".section-head", ".paths__item", ".choose__item", ".secondary-path",
      ".form-layout__head", ".contact__main", ".contact__side", ".g-item", ".cta-band__inner", ".virtual__text", ".virtual__stage"
    ].join(","));
    if (!("IntersectionObserver" in window)) return;
    doc.documentElement.classList.add("js");
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add("is-in");
        io.unobserve(en.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    targets.forEach(function (el) {
      var siblings = Array.prototype.indexOf.call(el.parentNode.children, el);
      el.classList.add("reveal");
      // Cascata curta só em grupos pequenos (colunas, destaques); listas longas entram juntas.
      if (!el.matches(".g-item")) el.style.setProperty("--reveal-delay", Math.min(siblings, 3) * 0.06 + "s");
      io.observe(el);
    });
  })();

  /* Menu interno da Feira: marca a seção visível. */
  (function () {
    var spy = $("[data-scrollspy]");
    if (!spy || !("IntersectionObserver" in window)) return;
    var links = $$("[data-spy]", spy);
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        links.forEach(function (a) {
          if (a.getAttribute("data-spy") === en.target.id) a.setAttribute("aria-current", "location");
          else a.removeAttribute("aria-current");
        });
      });
    }, { rootMargin: "-35% 0px -60% 0px" });
    links.forEach(function (a) { var t = doc.getElementById(a.getAttribute("data-spy")); if (t) io.observe(t); });
  })();

  /* Banner em camadas: a foto rola mais devagar que o painel (parallax leve). */
  (function () {
    var banner = $("#destaques");
    if (!banner || reduceMotion.matches) return;
    var ticking = false;
    function update() {
      ticking = false;
      var r = banner.getBoundingClientRect();
      if (r.bottom < 0 || r.top > window.innerHeight || banner.offsetParent === null) return;
      banner.style.setProperty("--parallax", Math.max(0, -r.top).toFixed(1) + "px");
    }
    window.addEventListener("scroll", function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    reduceMotion.addEventListener && reduceMotion.addEventListener("change", function (e) {
      if (e.matches) banner.style.removeProperty("--parallax");
    });
    update();
  })();

  /* Feira virtual: o tour (página de terceiros) só carrega quando a pessoa pede. */
  (function () {
    var btn = $("[data-tour-open]");
    var stage = $("[data-tour-stage]");
    var link = $("[data-tour-link]");
    if (!btn || !stage || !link) return;
    btn.addEventListener("click", function () {
      if (stage.querySelector("iframe")) return;
      var frame = doc.createElement("iframe");
      frame.src = link.href;
      frame.title = "Tour virtual 360° da MRO Brasil 2026";
      frame.allow = "fullscreen; accelerometer; gyroscope; xr-spatial-tracking";
      frame.setAttribute("allowfullscreen", "");
      stage.innerHTML = "";
      stage.appendChild(frame);
      stage.classList.add("is-loaded");
      btn.disabled = true;
      btn.textContent = "Tour aberto";
      frame.focus();
    });
  })();

  /* Sombra discreta no cabeçalho após rolar. */
  var header = $(".site-header");
  window.addEventListener("scroll", function () {
    header.classList.toggle("is-scrolled", window.scrollY > 8);
  }, { passive: true });

  window.addEventListener("hashchange", render);
  if (!location.hash) history.replaceState(null, "", "#/");
  render();
  maybeShowPopup();
})();
