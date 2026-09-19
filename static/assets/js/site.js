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
      if (e.key !== 'Escape' || !lang.classList.contains('open')) return;
      var dentro = lang.contains(document.activeElement);
      close();
      if (dentro) langBtn.focus();
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
    var onMq = function (e) { if (e.matches && document.body.classList.contains('menu-open')) setMenu(false); };
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
    var condensar = function () { shell.classList.toggle('scrolled', scrollY > 24); };
    condensar();  // la página puede abrirse ya desplazada (recarga, enlace a #contact)
    addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () { condensar(); ticking = false; });
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


  /* ── Horario: «obert ara / tancat» con la hora de Vilanova ─── */
  var obert = document.querySelector('.obert[data-horari]');
  if (obert) {
    var H;
    try { H = JSON.parse(obert.getAttribute('data-horari')); } catch (e) { H = null; }
    var aMin = function (t) { var p = t.split(':'); return +p[0] * 60 + +p[1]; };
    var hora = function (t) {
      if (H.t.hourFmt !== 'ca') return t;
      var p = t.split(':'), h = String(+p[0]);
      return (p[1] === '00' ? h : h + '.' + p[1]) + '\u00a0h';
    };
    // fecha y minutos actuales en Europe/Madrid, sea cual sea la zona del visitante
    var ahora = function () {
      var f = {};
      new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Madrid', year: 'numeric', month: '2-digit',
        day: '2-digit', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' })
        .formatToParts(new Date()).forEach(function (x) { f[x.type] = x.value; });
      return { fecha: f.year + '-' + f.month + '-' + f.day, min: +f.hour * 60 + +f.minute };
    };
    var tramos = function (fecha) {
      for (var i = 0; i < H.special.length; i++) if (H.special[i].date === fecha) return H.special[i].intervals;
      var dia = (new Date(fecha + 'T12:00:00Z').getUTCDay() + 6) % 7;   // lunes = 0
      return H.week[dia] || [];
    };
    var sumaDias = function (fecha, n) {
      var d = new Date(fecha + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() + n);
      return d.toISOString().slice(0, 10);
    };
    var pintar = function () {
      var n = ahora(), hoy = tramos(n.fecha), texto = null, abierto = false;
      for (var i = 0; i < hoy.length; i++) {
        if (n.min >= aMin(hoy[i][0]) && n.min < aMin(hoy[i][1])) {
          abierto = true; texto = H.t.closes.replace('{h}', hora(hoy[i][1])); break;
        }
      }
      if (!abierto) {
        for (var k = 0; k < 8 && !texto; k++) {
          var fecha = sumaDias(n.fecha, k), tr = tramos(fecha);
          for (var j = 0; j < tr.length; j++) {
            if (k > 0 || aMin(tr[j][0]) > n.min) {
              var dia = (new Date(fecha + 'T12:00:00Z').getUTCDay() + 6) % 7;
              var cuando = k === 0 ? H.t.today : k === 1 ? H.t.tomorrow : H.t.on + H.days[dia];
              texto = H.t.opens.replace('{d}', cuando).replace('{h}', hora(tr[j][0]));
              break;
            }
          }
        }
      }
      var html = '<span class="obert-punt" aria-hidden="true"></span><b>' + (abierto ? H.t.open : H.t.closed) +
                 '</b>' + (texto ? '<span>· ' + texto + '</span>' : '');
      if (obert.innerHTML !== html) obert.innerHTML = html;
      obert.classList.toggle('is-obert', abierto);
      obert.hidden = false;
    };
    if (H && H.week && H.t) { pintar(); setInterval(pintar, 60000); }
  }

})();
