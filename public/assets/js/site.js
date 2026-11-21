/* Midway Storage - progressive enhancement only. Every page works without this file. */
(function () {
  var root = document.documentElement;

  // Mobile menu
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.nav-toggle');
  if (header && toggle) {
    toggle.addEventListener('click', function () {
      var open = header.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && header.classList.contains('nav-open')) {
        header.classList.remove('nav-open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus();
      }
    });
  }

  // Door failsafe: never leave the door covering the photo
  if (root.classList.contains('door-play')) {
    setTimeout(function () { root.classList.remove('door-play'); }, 3200);
  }

  // Red guide line draws itself when it scrolls into view
  var guides = document.querySelectorAll('[data-draw]');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('drawn'); io.unobserve(e.target); } });
    }, { threshold: 0.3 });
    guides.forEach(function (g) { io.observe(g); });
  } else {
    guides.forEach(function (g) { g.classList.add('drawn'); });
  }

  // Unit filters
  var filters = document.querySelector('.filters');
  var grid = document.querySelector('[data-units]');
  var count = document.querySelector('.filter-count');
  if (filters && grid) {
    filters.hidden = false;
    var cards = grid.querySelectorAll('.unit-card');
    filters.addEventListener('click', function (e) {
      var b = e.target.closest('button[data-filter]');
      if (!b) return;
      var f = b.getAttribute('data-filter'), n = 0;
      filters.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      cards.forEach(function (c) {
        var show = f === 'all' || (f === 'open' ? c.getAttribute('data-status') === 'rent' : c.getAttribute('data-group') === f);
        c.hidden = !show; if (show) n++;
      });
      if (count) count.textContent = n + (n === 1 ? ' size' : ' sizes') + ' shown';
    });
  }

  // Reviews: arrows, and Read more only on cards whose text is cut off
  document.querySelectorAll('[data-carousel]').forEach(function (wrap) {
    var track = wrap.querySelector('.rv-track');
    var section = wrap.closest('section');
    var nav = section && section.querySelector('.rv-nav');
    if (nav && track) {
      nav.hidden = false;
      nav.addEventListener('click', function (e) {
        var b = e.target.closest('button[data-dir]');
        if (!b) return;
        var card = track.querySelector('.rv');
        var step = card ? card.getBoundingClientRect().width + 22 : track.clientWidth;
        track.scrollBy({ left: step * Number(b.getAttribute('data-dir')), behavior: 'smooth' });
      });
    }
    function checkMore() {
      wrap.querySelectorAll('.rv').forEach(function (rv) {
        if (rv.classList.contains('open')) return;
        var p = rv.querySelector('blockquote p'), btn = rv.querySelector('.rv-more');
        if (p && btn) btn.hidden = p.scrollHeight <= p.clientHeight + 2;
      });
    }
    wrap.addEventListener('click', function (e) {
      var btn = e.target.closest('.rv-more');
      if (!btn) return;
      var rv = btn.closest('.rv'), open = rv.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.textContent = open ? 'Show less' : 'Read more';
    });
    checkMore();
    window.addEventListener('resize', checkMore);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(checkMore);
  });
})();
