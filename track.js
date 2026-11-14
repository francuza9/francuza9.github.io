// Visitor analytics: Microsoft Clarity (clicks, scrolling, session replay) plus named events
// for the actions that matter. Open any page with ?notrack once to stop it in that browser;
// ?track turns it back on.
(function () {
  var off = false;
  try {
    if (/[?&]notrack\b/.test(location.search)) localStorage.setItem('notrack', '1');
    if (/[?&]track\b/.test(location.search)) localStorage.removeItem('notrack');
    off = localStorage.getItem('notrack') === '1';
  } catch (e) {}
  if (off) return;

  (function (c, l, a, r, i, t, y) {
    c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
    t = l.createElement(r); t.async = 1; t.src = 'https://www.clarity.ms/tag/' + i;
    y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
  })(window, document, 'clarity', 'script', 'zdq617famz');

  function ev(name) { try { window.clarity('event', name); } catch (e) {} }
  window.clarity('set', 'lang', document.documentElement.lang || 'en');

  document.addEventListener('click', function (e) {
    var el = e.target.closest && e.target.closest('a, button');
    if (!el) return;
    if (el.dataset.video) return ev(el.dataset.video.indexOf('yvito-demo') > -1 ? 'demo_open' : 'video_open');
    if (el.dataset.yt) return ev('reel_open');
    var h = el.getAttribute('href') || '';
    if (!h) return;
    if (h.indexOf('tel:') === 0) return ev('call_click');
    if (h.indexOf('mailto:') === 0) return ev('email_click');
    if (el.closest('.langs')) return ev('lang_switch');
    if (/dialyzeai\.html/.test(h)) return ev('case_study_open');
    if (/^https?:/.test(h) && el.hostname !== location.hostname) ev('out_' + el.hostname.replace(/^www\./, '').split('.')[0]);
  }, true);

  // How much of the demo people actually watch
  var half = false;
  document.addEventListener('timeupdate', function (e) {
    var v = e.target;
    if (!half && v.src && v.src.indexOf('yvito-demo') > -1 && v.duration && v.currentTime > v.duration / 2) { half = true; ev('demo_half'); }
  }, true);
  document.addEventListener('ended', function (e) {
    if (e.target.src && e.target.src.indexOf('yvito-demo') > -1) ev('demo_finished');
  }, true);
})();
