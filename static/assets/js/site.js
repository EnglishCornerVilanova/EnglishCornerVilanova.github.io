/* English Corner — site behaviour
   Vanilla, no dependencies. Loaded with `defer`. */
(function () {
  'use strict';

  /* ── Language preference ─────────────────────────────── */
  /* The redirect itself lives in a blocking <head> script (see the
     template) so a returning visitor never sees the wrong language
     paint first. All this does is record an explicit choice. */
  document.querySelectorAll('[data-lang]').forEach(function (a) {
    a.addEventListener('click', function () {
      try { localStorage.setItem('ec-lang', a.getAttribute('data-lang')); } catch (e) {}
    });
  });

  /* ── Language menu (desktop) ─────────────────────────── */
  var lang = document.getElementById('langSwitch');
  if (lang) {
    var langBtn = lang.querySelector('.lang-btn');
    var close = function () {
      lang.classList.remove('open');
      langBtn.setAttribute('aria-expanded', 'false');
    };
    langBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = lang.classList.toggle('open');
      langBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('click', function (e) {
      if (!lang.contains(e.target)) close();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') close();
    });
  }

  /* ── Mobile drawer ───────────────────────────────────── */
  var burger = document.getElementById('burger');
  var drawer = document.getElementById('drawer');
  if (burger && drawer) {
    var setMenu = function (open) {
      document.body.classList.toggle('menu-open', open);
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      drawer.setAttribute('aria-hidden', open ? 'false' : 'true');
      if (open) {
        var first = drawer.querySelector('a');
        if (first) first.focus({ preventScroll: true });
      } else {
        burger.focus({ preventScroll: true });
      }
    };
    burger.addEventListener('click', function () {
      setMenu(!document.body.classList.contains('menu-open'));
    });
    drawer.addEventListener('click', function (e) {
      if (e.target.closest('a')) setMenu(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && document.body.classList.contains('menu-open')) setMenu(false);
    });
    // Keep the drawer from lingering if the viewport grows past the breakpoint.
    var mq = window.matchMedia('(min-width:941px)');
    var onMq = function (e) { if (e.matches) setMenu(false); };
    mq.addEventListener ? mq.addEventListener('change', onMq) : mq.addListener(onMq);
  }

  /* ── Scroll reveal ───────────────────────────────────── */
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var targets = document.querySelectorAll('.rv');
  if (reduce || !('IntersectionObserver' in window)) {
    targets.forEach(function (el) { el.classList.add('on'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('on'); io.unobserve(en.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    targets.forEach(function (el) { io.observe(el); });
  }

  /* ── Nav condense on scroll ──────────────────────────── */
  var shell = document.getElementById('navShell');
  if (shell) {
    var ticking = false;
    addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        shell.classList.toggle('scrolled', scrollY > 24);
        ticking = false;
      });
    }, { passive: true });
  }

  /* ── Marquee: duplicate for a seamless loop ──────────── */
  var track = document.getElementById('mqTrack');
  if (track) track.innerHTML += track.innerHTML;

  /* ── Map: load Google only after explicit consent ────── */
  var mapShell = document.getElementById('mapShell');
  if (mapShell) {
    var btn = mapShell.querySelector('[data-map-load]');
    if (btn) {
      btn.addEventListener('click', function () {
        var frame = document.createElement('iframe');
        frame.src = mapShell.getAttribute('data-map-src');
        frame.loading = 'lazy';
        frame.title = mapShell.getAttribute('data-map-title') || 'Map';
        frame.referrerPolicy = 'no-referrer-when-downgrade';
        frame.setAttribute('allowfullscreen', '');
        var label = btn.querySelector('[data-map-label]');
        if (label) label.textContent = mapShell.getAttribute('data-map-loading') || label.textContent;
        btn.disabled = true;
        mapShell.setAttribute('aria-busy', 'true');
        // el aviso se queda hasta que Google ha pintado; así no hay recuadro vacío
        var mostrar = function () {
          mapShell.classList.add('loaded');
          mapShell.removeAttribute('aria-busy');
        };
        frame.addEventListener('load', mostrar, { once: true });
        setTimeout(mostrar, 8000);
        mapShell.appendChild(frame);
      }, { once: true });
    }
  }

  /* ── Hero: los cromos se separan siguiendo el puntero ──── */
  /* Solo con ratón, en pantalla ancha y si no se ha pedido menos animación.
     El desplazamiento se escribe en dos variables CSS y lo reparte cada cromo
     según su profundidad, de modo que el collage gana relieve al moverse. */
  var heroArt = document.querySelector('.hero-visual');
  if (heroArt &&
      matchMedia('(hover:hover)').matches &&
      matchMedia('(min-width:941px)').matches &&
      !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var pend = 0, dx = 0, dy = 0;
    var pintar = function () {
      pend = 0;
      heroArt.style.setProperty('--px', dx.toFixed(1) + 'px');
      heroArt.style.setProperty('--py', dy.toFixed(1) + 'px');
    };
    var seguir = function (e) {
      var r = heroArt.getBoundingClientRect();
      dx = ((e.clientX - r.left) / r.width - 0.5) * 20;
      dy = ((e.clientY - r.top) / r.height - 0.5) * 12;
      if (!pend) pend = requestAnimationFrame(pintar);
    };
    heroArt.addEventListener('pointermove', seguir, { passive: true });
    heroArt.addEventListener('pointerleave', function () {
      dx = dy = 0;
      if (!pend) pend = requestAnimationFrame(pintar);
    });
  }

})();
