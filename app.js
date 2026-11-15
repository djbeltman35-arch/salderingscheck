/* Salderingscheck - interface */
(function () {
  'use strict';

  // === Partnerlinks =========================================================
  // Vervang url door je affiliate-link (Daisycon/Awin) en zet affiliate op true.
  // Dan krijgt de link rel="sponsored" en verschijnt de melding over partnerlinks.
  var PARTNERS = {
    batterijPlugin: [
      { naam: 'Bekijk plug-and-play thuisbatterijen', url: 'https://www.ankersolix.com/nl', affiliate: false }
    ],
    batterijVast: [
      { naam: 'Vergelijk offertes van installateurs', url: 'https://www.homedeal.nl/thuisbatterij/', affiliate: false }
    ],
    contract: [
      { naam: 'Vergelijk netto terugleververgoedingen 2027', url: 'https://www.energievergelijk.nl/onderwerpen/terugleververgoeding', affiliate: false }
    ]
  };
  // ==========================================================================

  var SC = window.SC;
  var $ = function (id) { return document.getElementById(id); };
  var STORE = 'salderingscheck-v2';
  var VELDEN = ['panelen', 'wp', 'verbruik', 'afname', 'teruglevering', 'contract', 'leverancier', 'stroomprijs', 'tlkNu', 'vergoedingNu', 'netto27Vast', 'netto27Dyn'];

  var state = {
    modus: 'schatten',
    apparaten: [],
    batterijType: 'plugin',
    batterijCap: 2.7,
    batterijPrijs: '',
    btw: false,
    handel: 0
  };

  var eur = new Intl.NumberFormat('nl-NL', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 });
  var nr = new Intl.NumberFormat('nl-NL', { maximumFractionDigits: 0 });
  var nr1 = new Intl.NumberFormat('nl-NL', { maximumFractionDigits: 1 });
  function fmtEur(v) { var r = Math.round(v); return (r < 0 ? '−' : '') + eur.format(Math.abs(r)).replace(/\u00a0/g, ' '); }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]; }); }

  // --- Opslaan en laden ---
  function lees() {
    var inp = { modus: state.modus, apparaten: state.apparaten.slice(), batterijType: state.batterijType, batterijCap: state.batterijCap, batterijPrijs: state.batterijPrijs, btw: state.btw, handel: state.handel };
    VELDEN.forEach(function (k) { inp[k] = $(k).value; });
    return inp;
  }
  function bewaar(inp) { try { localStorage.setItem(STORE, JSON.stringify(inp)); } catch (e) { /* geen opslag */ } }
  function zet(inp) {
    if (!inp) return;
    VELDEN.forEach(function (k) { if (inp[k] != null && inp[k] !== '') { $(k).value = inp[k]; if (k === 'leverancier') $(k).dataset.waarde = inp[k]; } });
    ['modus', 'batterijType', 'batterijPrijs'].forEach(function (k) { if (inp[k] != null) state[k] = inp[k]; });
    if (inp.batterijCap != null && isFinite(parseFloat(inp.batterijCap))) state.batterijCap = parseFloat(inp.batterijCap);
    if (inp.handel != null && isFinite(parseFloat(inp.handel))) state.handel = parseFloat(inp.handel);
    if (inp.btw != null) state.btw = inp.btw === true || inp.btw === '1';
    if (inp.apparaten) state.apparaten = Array.isArray(inp.apparaten) ? inp.apparaten : String(inp.apparaten).split(',').filter(Boolean);
  }
  function uitUrl() {
    var q = new URLSearchParams(location.search);
    if (!q.toString()) return null;
    var o = {};
    q.forEach(function (v, k) { o[k] = v; });
    return o;
  }
  function naarUrl(inp) {
    var q = new URLSearchParams();
    Object.keys(inp).forEach(function (k) {
      var v = inp[k];
      if (Array.isArray(v)) v = v.join(',');
      if (typeof v === 'boolean') v = v ? '1' : '0';
      if (v !== '' && v != null) q.set(k, v);
    });
    return location.origin + location.pathname + '?' + q.toString();
  }

  // --- Opties opbouwen (eenmalig) ---
  function partnerHtml(lijst) {
    return lijst.map(function (p) {
      var rel = p.affiliate ? 'sponsored noopener' : 'noopener';
      return '<a class="btn ghost" href="' + esc(p.url) + '" target="_blank" rel="' + rel + '" data-partner="' + esc(p.naam) + '">' + esc(p.naam) + ' →</a>';
    }).join('');
  }

  function bouwOpties() {
    var box = $('opties');
    var apparaten = SC.APPARATEN.map(function (a) {
      return '<label><input type="checkbox" value="' + a.id + '"' + (state.apparaten.indexOf(a.id) !== -1 ? ' checked' : '') + '> <span>' + esc(a.naam) + ' <span class="hint">(~' + a.kwh + ' kWh)</span></span></label>';
    }).join('');

    box.innerHTML =
      '<div class="opt" id="opt-batterij">' +
        '<h3><span id="bat-titel">Thuisbatterij</span><span class="pill" id="bat-pill"></span></h3>' +
        '<div class="save" id="bat-save"></div>' +
        '<div class="seg" role="group" aria-label="Soort batterij" style="margin:10px 0 6px">' +
          '<button type="button" data-bat="plugin">Plug-and-play</button>' +
          '<button type="button" data-bat="vast">Vast met installateur</button>' +
        '</div>' +
        '<div class="range"><label for="cap" class="sr">Capaciteit</label><input id="cap" type="range" min="1" max="8" step="0.1"><output id="cap-out"></output></div>' +
        '<div class="grid">' +
          '<label class="f">Prijs per kWh capaciteit<span class="inp"><input id="batPrijs" type="number" inputmode="decimal" min="50" step="10"><span class="unit">€/kWh</span></span><small id="batPrijs-hint"></small></label>' +
          '<label class="f">Extra opbrengst handel<span class="inp"><input id="handel" type="number" inputmode="decimal" min="0" step="10"><span class="unit">€/jaar</span></span><small>Alleen als je aanbieder dit garandeert. Sterk wisselend.</small></label>' +
        '</div>' +
        '<div class="checks" id="btw-wrap" style="grid-template-columns:1fr"><label><input type="checkbox" id="btw"> <span>Ik vraag de btw terug <span class="hint">(alleen bij handel in stroom, je betaalt ~€15/kWh afdracht)</span></span></label></div>' +
        '<div class="stats">' +
          '<div><b id="bat-kosten"></b><span>aanschaf</span></div>' +
          '<div><b id="bat-tvt"></b><span>terugverdientijd</span></div>' +
          '<div><b id="bat-netto"></b><span>netto na 12 jaar</span></div>' +
        '</div>' +
        '<div class="verdict" id="bat-verdict"></div>' +
        '<div class="actions" id="bat-partner"></div>' +
      '</div>' +
      '<div class="opt" id="opt-slim">' +
        '<h3><span>Slimmer verbruiken: apparaten aan als de zon schijnt</span><span class="pill good">Gratis</span></h3>' +
        '<div class="save" id="slim-save"></div>' +
        '<p class="hint" style="margin:4px 0 0">Vink aan wat je overdag kunt laten draaien:</p>' +
        '<div class="checks" id="apparaten">' + apparaten + '</div>' +
        '<p class="note" id="slim-note"></p>' +
      '</div>' +
      '<div class="opt" id="opt-contract">' +
        '<h3><span id="contract-titel"></span><span class="pill neutral" id="contract-pill">Gratis overstappen</span></h3>' +
        '<div class="save" id="contract-save"></div>' +
        '<p class="note" id="contract-note"></p>' +
        '<div class="actions">' + partnerHtml(PARTNERS.contract) + '</div>' +
      '</div>';

    box.querySelectorAll('[data-bat]').forEach(function (b) {
      b.addEventListener('click', function () {
        if (state.batterijType === b.dataset.bat) return;
        state.batterijType = b.dataset.bat;
        state.batterijCap = state.batterijType === 'plugin' ? 2.7 : 10;
        state.batterijPrijs = '';
        update();
      });
    });
    $('cap').addEventListener('input', function () { state.batterijCap = parseFloat(this.value); update(); });
    $('batPrijs').addEventListener('input', function () { state.batterijPrijs = this.value; update(); });
    $('handel').addEventListener('input', function () { state.handel = parseFloat(this.value) || 0; update(); });
    $('btw').addEventListener('change', function () { state.btw = this.checked; update(); });
    $('apparaten').addEventListener('change', function () {
      state.apparaten = Array.prototype.map.call(this.querySelectorAll('input:checked'), function (i) { return i.value; });
      update();
    });
  }

  // --- Weergave bijwerken ---
  function render(r) {
    var p = r.profiel;
    var extra = r.extra;
    $('extra').textContent = fmtEur(Math.abs(extra));
    $('extra').className = 'big ' + (extra > 0.5 ? 'bad' : 'good');
    $('uitkomst-intro').textContent = extra > 0.5 ? 'Vanaf 2027 betaal je voor stroom ongeveer' : 'Vanaf 2027 verandert er voor jou weinig:';
    $('extra-sub').textContent = extra > 0.5 ? 'per jaar meer dan nu (± ' + fmtEur(extra / 12) + ' per maand)' : (extra < -0.5 ? 'per jaar minder dan nu' : 'nauwelijks verschil');
    var he = $('heroExtra'); if (he) he.textContent = fmtEur(Math.max(0, extra)).replace(' ', '');
    $('kostenNu').textContent = fmtEur(r.kostenNu);
    $('kosten27').textContent = fmtEur(r.kosten27);
    var note = p.geschat
      ? 'Geschat: je panelen wekken ongeveer ' + nr.format(p.opwek) + ' kWh per jaar op. Daarvan gebruik je ~' + nr.format(p.direct) + ' kWh direct, je levert ~' + nr.format(p.teruglevering) + ' kWh terug en haalt ~' + nr.format(p.afname) + ' kWh van het net. Weet je je echte cijfers? Kies "Ik weet mijn cijfers" voor een preciezere uitkomst.'
      : 'Je levert ' + nr.format(p.teruglevering) + ' kWh terug en haalt ' + nr.format(p.afname) + ' kWh van het net.';
    if (p.teruglevering === 0) note = 'Je levert niets terug, dus het einde van salderen raakt jou niet.';
    $('profiel-note').textContent = note;

    var opt = {};
    r.opties.forEach(function (o) { opt[o.id] = o; });

    // Contract
    var c = opt.contract;
    $('contract-titel').textContent = c.titel;
    setSave('contract-save', c.besparing);
    var nettoCt = function (v) { return new Intl.NumberFormat('nl-NL', { maximumFractionDigits: 2 }).format(v * 100).replace(/^-/, '−') + ' ct'; };
    $('contract-note').textContent = c.besparing > 0.5
      ? (c.altType === 'dynamisch'
        ? 'Met een dynamisch contract krijg je naar schatting ' + nettoCt(c.altNetto) + ' netto per teruggeleverde kWh, tegen ' + nettoCt(r.v27) + ' nu. Je stroomprijs wisselt dan wel per uur.'
        : 'De hoogste netto vergoeding bij 1 jaar vast heeft nu ' + c.besteNaam + ': ' + nettoCt(c.altNetto) + ' per kWh, tegen ' + nettoCt(r.v27) + ' bij jou. Vergelijk ook de stroomprijs, want die telt zwaarder als je veel afneemt.')
      : 'Je zit al bij een van de hoogste netto vergoedingen. Overstappen levert op teruglevering weinig op.';
    $('contract-pill').textContent = c.besparing > 0.5 ? 'Gratis overstappen' : 'Niet voordeliger';
    $('contract-pill').className = 'pill ' + (c.besparing > 0.5 ? 'good' : 'neutral');

    // Slim
    var s = opt.slim;
    setSave('slim-save', s.besparing, s.gekozen === 0 ? 'Vink apparaten aan' : null);
    $('slim-note').textContent = s.gekozen ? 'Je gebruikt zo ~' + nr.format(s.kwh) + ' kWh extra zonnestroom zelf. Tip: zet apparaten op een uitgestelde start of gebruik een slimme stekker.' : '';

    // Batterij
    var b = opt.batterij;
    var isPlug = state.batterijType === 'plugin';
    $('bat-titel').textContent = b.titel;
    document.querySelectorAll('[data-bat]').forEach(function (btn) { btn.setAttribute('aria-pressed', String(btn.dataset.bat === state.batterijType)); });
    var cap = $('cap');
    cap.min = isPlug ? 1 : 3; cap.max = isPlug ? 8 : 25; cap.step = isPlug ? 0.1 : 0.5;
    cap.value = state.batterijCap;
    $('cap-out').textContent = nr1.format(state.batterijCap) + ' kWh';
    var stdPrijs = SC.batterijPrijsPerKwh(state.batterijType, state.batterijCap);
    var batPrijs = $('batPrijs');
    batPrijs.placeholder = String(stdPrijs);
    if (document.activeElement !== batPrijs) batPrijs.value = state.batterijPrijs;
    $('batPrijs-hint').textContent = 'Leeg = gemiddelde (€' + stdPrijs + '/kWh incl. btw' + (isPlug ? '' : ' en installatie') + '). Vul je offerte in voor een eerlijke vergelijking.';
    var handel = $('handel');
    if (document.activeElement !== handel) handel.value = state.handel || '';
    handel.placeholder = '0';
    $('btw-wrap').classList.toggle('hidden', isPlug);
    $('btw').checked = state.btw;

    setSave('bat-save', b.besparing);
    $('bat-kosten').textContent = fmtEur(b.kosten);
    $('bat-tvt').textContent = isFinite(b.terugverdientijd) ? nr1.format(b.terugverdientijd) + ' jaar' : 'nooit';
    $('bat-netto').textContent = (b.nettoLevensduur >= 0 ? '+' : '−') + fmtEur(Math.abs(b.nettoLevensduur));
    var pill = $('bat-pill'), verdict = $('bat-verdict');
    var tvt = b.terugverdientijd;
    var cls, pillTxt, txt;
    if (tvt <= 8) { cls = 'good'; pillTxt = 'Kan lonen'; txt = 'Deze batterij verdient zich ruim binnen de levensduur terug.'; }
    else if (tvt <= 12) { cls = 'warn'; pillTxt = 'Twijfelgeval'; txt = 'Deze batterij verdient zich net binnen de levensduur terug. Een lagere prijs per kWh maakt veel uit.'; }
    else { cls = 'bad'; pillTxt = 'Loont niet'; txt = 'Deze batterij verdient zich waarschijnlijk niet terug binnen de levensduur van ~12 jaar.'; }
    var best = b.beste;
    if (best) {
      if (best.nettoLevensduur > 0) {
        if (Math.abs(best.cap - state.batterijCap) >= 0.5) {
          txt += ' Voor jouw situatie rendeert <strong>' + nr1.format(best.cap) + ' kWh</strong> het best: ' + fmtEur(best.besparing) + ' per jaar, terugverdiend in ' + nr1.format(best.terugverdientijd) + ' jaar. <button type="button" class="btn ghost" id="pak-beste" style="min-height:34px;padding:4px 10px;margin-top:6px">Kies ' + nr1.format(best.cap) + ' kWh</button>';
        } else {
          txt += ' Dit is ongeveer de beste grootte voor jouw situatie.';
        }
      } else {
        txt += isPlug
          ? ' Bij deze prijs loont geen enkele grootte. Kijk of je een batterij onder de €300 per kWh kunt vinden.'
          : ' Bij deze prijs loont geen enkele grootte. Vergelijk een plug-and-play batterij, of vraag meerdere offertes aan.';
      }
    }
    pill.className = 'pill ' + cls; pill.textContent = pillTxt;
    verdict.className = 'verdict ' + cls; verdict.innerHTML = txt;
    var pak = $('pak-beste');
    if (pak) pak.addEventListener('click', function () { state.batterijCap = best.cap; update(); });
    $('bat-partner').innerHTML = partnerHtml(isPlug ? PARTNERS.batterijPlugin : PARTNERS.batterijVast);

    // Sorteren op besparing per jaar (batterij: netto na levensduur per jaar)
    var waarde = {
      'opt-contract': c.besparing,
      'opt-slim': s.gekozen ? s.besparing : -1,
      'opt-batterij': b.nettoLevensduur / 12
    };
    var box = $('opties');
    var volgorde = Object.keys(waarde).sort(function (a, z) { return waarde[z] - waarde[a]; });
    volgorde.forEach(function (id) { box.appendChild($(id)); });
    box.querySelectorAll('.opt').forEach(function (el) { el.classList.remove('top'); });
    if (waarde[volgorde[0]] > 0) $(volgorde[0]).classList.add('top');

    var heeftAff = Object.keys(PARTNERS).some(function (k) { return PARTNERS[k].some(function (x) { return x.affiliate; }); });
    $('disclosure').classList.toggle('hidden', !heeftAff);
  }

  function setSave(id, v, leeg) {
    var el = $(id);
    if (leeg) { el.textContent = leeg; el.className = 'save zero'; return; }
    if (v > 0.5) { el.textContent = '+ ' + fmtEur(v) + ' per jaar'; el.className = 'save'; }
    else { el.textContent = v < -0.5 ? 'Kost je ' + fmtEur(-v) + ' per jaar extra' : 'Levert niets op'; el.className = 'save zero'; }
  }

  function zetModus(m) {
    state.modus = m;
    document.querySelectorAll('[data-modus]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.modus === m)); });
    $('blok-schatten').classList.toggle('hidden', m !== 'schatten');
    $('blok-exact').classList.toggle('hidden', m !== 'exact');
  }

  var laatste = null;
  function update() {
    zetModus(state.modus);
    var inp = lees();
    var r = SC.bereken(inp);
    laatste = r;
    render(r);
    bewaar(inp);
  }

  // --- Aftellen ---
  function aftellen() {
    var eind = new Date('2027-01-01T00:00:00+01:00');
    var dagen = Math.ceil((eind - new Date()) / 86400000);
    var led = $('ledDagen');
    if (dagen > 0) {
      $('countdown').textContent = dagen === 1 ? 'Morgen stopt salderen' : 'Nog ' + dagen + ' dagen';
      if (led) led.innerHTML = dagen + '<small>' + (dagen === 1 ? 'dag' : 'dgn') + '</small>';
    } else {
      $('countdown').textContent = 'Salderen is gestopt';
      if (led) { led.innerHTML = '0<small>dgn</small>'; led.nextElementSibling.textContent = 'sinds 1 jan 2027'; led.previousElementSibling.textContent = 'Salderen gestopt'; }
    }
  }

  function toast(t) {
    var el = $('toast'); el.textContent = t; el.classList.add('show');
    clearTimeout(toast.t); toast.t = setTimeout(function () { el.classList.remove('show'); }, 2500);
  }

  // --- Start ---
  function init() {
    var opgeslagen = null;
    try { opgeslagen = JSON.parse(localStorage.getItem(STORE) || 'null'); } catch (e) { /* leeg */ }
    zet(uitUrl() || opgeslagen);
    if (uitUrl()) history.replaceState(null, '', location.pathname);
    bouwOpties();
    aftellen();

    var levSel = $('leverancier');
    SC.LEVERANCIERS.forEach(function (l) {
      var o = document.createElement('option');
      o.value = l.id; o.textContent = l.naam + ' (' + nr1.format(l.netto) + ' ct)';
      levSel.appendChild(o);
    });
    if (levSel.dataset.waarde) levSel.value = levSel.dataset.waarde;
    levSel.addEventListener('change', function () {
      var l = SC.LEVERANCIERS.filter(function (x) { return x.id === levSel.value; })[0];
      $('netto27Vast').value = l ? (l.netto / 100).toFixed(4).replace(/0+$/, '').replace(/\.$/, '') : String(SC.DEFAULTS.netto27Vast);
      if (l) $('contract').value = 'vast';
      update();
    });
    $('contract').addEventListener('change', function () { if (this.value === 'dynamisch') levSel.value = ''; });

    document.querySelectorAll('[data-modus]').forEach(function (b) {
      b.addEventListener('click', function () { state.modus = b.dataset.modus; update(); });
    });
    VELDEN.forEach(function (k) { $(k).addEventListener('input', update); });

    $('deel').addEventListener('click', function () {
      var url = naarUrl(lees());
      var tekst = laatste && laatste.extra > 0.5
        ? 'Het einde van salderen kost mij ' + fmtEur(laatste.extra) + ' per jaar. Reken het zelf uit:'
        : 'Reken uit wat het einde van salderen jou kost:';
      if (navigator.share) {
        navigator.share({ title: 'Salderingscheck', text: tekst, url: url }).catch(function () {});
      } else if (navigator.clipboard) {
        navigator.clipboard.writeText(tekst + ' ' + url).then(function () { toast('Link gekopieerd'); }, function () { prompt('Kopieer deze link:', url); });
      } else { prompt('Kopieer deze link:', url); }
    });
    $('reset').addEventListener('click', function () {
      try { localStorage.removeItem(STORE); } catch (e) { /* leeg */ }
      location.href = location.pathname;
    });

    // Installeren als app
    var installEvt = null;
    window.addEventListener('beforeinstallprompt', function (e) {
      e.preventDefault(); installEvt = e; $('install').style.display = 'inline-flex';
    });
    $('install').addEventListener('click', function () {
      if (!installEvt) return;
      installEvt.prompt();
      installEvt.userChoice.finally(function () { installEvt = null; $('install').style.display = 'none'; });
    });

    // Klikken op partnerlinks en delen tellen (anoniem, GoatCounter)
    function tel(pad, titel) {
      try { if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({ path: pad, title: titel, event: true }); } catch (e) { /* niet erg */ }
    }
    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[data-partner]');
      if (a) tel('klik-partner-' + a.getAttribute('data-partner').toLowerCase().replace(/[^a-z0-9]+/g, '-'), a.getAttribute('data-partner'));
    });
    $('deel').addEventListener('click', function () { tel('klik-delen', 'Deel mijn uitkomst'); });

    update();

    if ('serviceWorker' in navigator && location.protocol === 'https:') {
      navigator.serviceWorker.register('/sw.js').catch(function () {});
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
