(function () {
  'use strict';
  var SC = window.SC, $ = function (i) { return document.getElementById(i); };
  var eur = new Intl.NumberFormat('nl-NL', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 });
  var lev = $('leverancier');
  SC.LEVERANCIERS.forEach(function (l) { var o = document.createElement('option'); o.value = l.id; o.textContent = l.naam + ' (' + String(l.netto).replace('.', ',') + ' ct)'; lev.appendChild(o); });
  function update() {
    var l = SC.LEVERANCIERS.filter(function (x) { return x.id === lev.value; })[0];
    var r = SC.bereken({ modus: 'schatten', panelen: $('panelen').value, wp: 400, verbruik: $('verbruik').value, contract: 'vast', netto27Vast: l ? l.netto / 100 : SC.DEFAULTS.netto27Vast });
    var e = Math.max(0, r.extra);
    $('extra').textContent = eur.format(Math.round(e)).replace(/\s/g, '');
    $('maand').textContent = '± ' + eur.format(Math.round(e / 12)) + ' per maand';
    var q = new URLSearchParams({ bron: 'widget', modus: 'schatten', panelen: $('panelen').value, verbruik: $('verbruik').value });
    if (l) { q.set('leverancier', l.id); q.set('netto27Vast', String(l.netto / 100)); }
    $('cta').href = 'https://salderingscheck-nl.netlify.app/?' + q.toString();
  }
  ['panelen', 'verbruik', 'leverancier'].forEach(function (i) { $(i).addEventListener('input', update); });
  update();
  // Hoogte doorgeven aan de insluitende pagina
  function hoogte() { try { parent.postMessage({ salderingscheck: document.documentElement.scrollHeight }, '*'); } catch (e) { /* niet erg */ } }
  window.addEventListener('load', hoogte); window.addEventListener('resize', hoogte);
})();
