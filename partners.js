// Floating "Member of" badge: shown at the top of the page and while scrolling,
// hidden when scrolling stops mid-page, and handed over to the footer badges at the bottom.
(function () {
  var el = document.querySelector('.partners');
  if (!el) return;
  el.classList.add('auto');
  var dock = document.querySelector('.foot .badges');
  var docked = false, hover = false, timer = null;

  function show(v) { el.classList.toggle('show', v); }
  function settle() { show(!docked && (window.scrollY < 120 || hover)); }
  function later() { clearTimeout(timer); timer = setTimeout(settle, 1200); }

  window.addEventListener('scroll', function () { if (!docked) show(true); later(); }, { passive: true });
  el.addEventListener('mouseenter', function () { hover = true; });
  el.addEventListener('mouseleave', function () { hover = false; later(); });
  el.addEventListener('focusin', function () { hover = true; show(true); });
  el.addEventListener('focusout', function () { hover = false; later(); });

  if (dock && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      docked = es[0].isIntersecting;
      if (docked) show(false); else settle();
    }, { rootMargin: '0px 0px -24px 0px' }).observe(dock);
  }
  setTimeout(settle, 400);
})();
