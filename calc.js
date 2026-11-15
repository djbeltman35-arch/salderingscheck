/* Salderingscheck - rekenkern. Werkt in browser (window.SC) en Node (module.exports). */
(function (root) {
  'use strict';

  // Uitgangspunten (bijgewerkt november 2026). Bronnen staan op de pagina.
  var DEFAULTS = {
    stroomprijs: 0.27,          // all-in prijs per kWh afname incl. belastingen
    vergoedingNu: 0.05,         // netto terugleververgoeding 2026 over je overschot (na saldering)
    netto27Vast: 0.005,         // netto vergoeding 2027 vast/variabel (vergoeding min terugleverkosten)
    netto27Dyn: 0.03,           // schatting netto vergoeding 2027 dynamisch (marktprijs tijdens zonuren, vaak geen terugleverkosten)
    opbrengstPerWp: 0.9,        // kWh per wattpiek per jaar in Nederland (900 vollasturen)
    directAandeel: 0.30,        // deel van de opwek dat je gemiddeld direct zelf gebruikt
    batterijRendement: 0.90,    // rondgangsrendement (laden + ontladen)
    batterijBruikbaar: 0.90,    // bruikbaar deel van de capaciteit
    batterijCycli: 250,         // max. volle cycli per jaar voor een kleine batterij (zonnige dagen maart t/m oktober)
    batterijLevensduur: 12,     // jaren (10 tot 15 jaar gangbaar)
    prijsPluginPerKwh: 420,     // plug-and-play, gemiddeld incl. btw
    prijsVastKleinPerKwh: 775,  // vaste installatie < 8 kWh, incl. btw en installatie
    prijsVastGrootPerKwh: 650,  // vaste installatie >= 8 kWh, incl. btw en installatie
    btwAfdrachtPerKwh: 15       // forfaitaire btw-afdracht bij btw-teruggave
  };

  // Verschuifbaar verbruik naar zonuren (grove indicatie, kWh per jaar)
  var APPARATEN = [
    { id: 'was', naam: 'Wasmachine overdag', kwh: 100 },
    { id: 'vaat', naam: 'Vaatwasser overdag', kwh: 120 },
    { id: 'droger', naam: 'Wasdroger overdag', kwh: 150 },
    { id: 'boiler', naam: 'Boiler of warmtepompboiler op zon', kwh: 300 },
    { id: 'wp', naam: 'Warmtepomp/airco overdag voorverwarmen of koelen', kwh: 250 },
    { id: 'ev', naam: 'Elektrische auto thuis overdag laden', kwh: 1000 }
  ];

  function num(v, fallback) {
    var n = typeof v === 'string' ? parseFloat(v.replace(',', '.')) : v;
    return isFinite(n) ? n : fallback;
  }
  function clamp(v, lo, hi) { return Math.min(hi, Math.max(lo, v)); }

  // Bepaal afname en teruglevering uit de invoer
  function verbruiksprofiel(inp) {
    var d = DEFAULTS;
    if (inp.modus === 'schatten') {
      var panelen = clamp(num(inp.panelen, 10), 0, 200);
      var wp = clamp(num(inp.wp, 400), 100, 1000);
      var verbruik = clamp(num(inp.verbruik, 3000), 0, 100000);
      var opwek = panelen * wp * d.opbrengstPerWp;
      var direct = Math.min(opwek * d.directAandeel, verbruik * 0.5);
      return {
        opwek: opwek,
        direct: direct,
        teruglevering: Math.max(0, opwek - direct),
        afname: Math.max(0, verbruik - direct),
        geschat: true
      };
    }
    return {
      opwek: null,
      direct: null,
      teruglevering: clamp(num(inp.teruglevering, 0), 0, 200000),
      afname: clamp(num(inp.afname, 0), 0, 200000),
      geschat: false
    };
  }

  function batterijPrijsPerKwh(type, cap) {
    if (type === 'plugin') return DEFAULTS.prijsPluginPerKwh;
    return cap < 8 ? DEFAULTS.prijsVastKleinPerKwh : DEFAULTS.prijsVastGrootPerKwh;
  }

  function batterijBerekening(p, inst) {
    var d = DEFAULTS;
    var cap = inst.cap;
    // Afnemende meeropbrengst: de eerste kWh opslag wordt bijna elke zonnige dag gevuld,
    // extra capaciteit steeds minder vaak. Maximum: 70% van je teruglevering en 60% van je afname.
    var maxOpslag = Math.max(0, Math.min(p.T * 0.7, p.A * 0.6));
    var lineair = cap * d.batterijBruikbaar * d.batterijCycli;
    var opgeslagen = maxOpslag > 0 ? maxOpslag * (1 - Math.exp(-lineair / maxOpslag)) : 0;
    var geleverd = opgeslagen * d.batterijRendement;
    var besparing = geleverd * p.prijs - opgeslagen * p.v27 + (inst.handel || 0);
    var bruto = cap * (inst.prijsPerKwh != null ? inst.prijsPerKwh : batterijPrijsPerKwh(inst.type, cap));
    var kosten = bruto;
    if (inst.btw && inst.type !== 'plugin') {
      kosten = bruto * 100 / 121 + cap * d.btwAfdrachtPerKwh;
    }
    var terugverdientijd = besparing > 0 ? kosten / besparing : Infinity;
    var netto = besparing * d.batterijLevensduur - kosten;
    return {
      cap: cap,
      type: inst.type,
      opgeslagen: opgeslagen,
      besparing: besparing,
      kosten: kosten,
      terugverdientijd: terugverdientijd,
      nettoLevensduur: netto
    };
  }

  function bereken(inp) {
    var d = DEFAULTS;
    var prof = verbruiksprofiel(inp);
    var T = prof.teruglevering, A = prof.afname;
    var prijs = clamp(num(inp.stroomprijs, d.stroomprijs), 0.05, 1.5);
    var contract = inp.contract === 'dynamisch' ? 'dynamisch' : 'vast';
    var vNu = clamp(num(inp.vergoedingNu, d.vergoedingNu), -0.5, 0.5);
    var vVast = clamp(num(inp.netto27Vast, d.netto27Vast), -0.5, 0.5);
    var vDyn = clamp(num(inp.netto27Dyn, d.netto27Dyn), -0.5, 0.5);
    var v27 = contract === 'dynamisch' ? vDyn : vVast;
    var tlkNu = clamp(num(inp.tlkNu, 0), 0, 5000);

    // 2026: met saldering
    var saldeerbaar = Math.min(T, A);
    var overschot = Math.max(0, T - A);
    var kostenNu = (A - saldeerbaar) * prijs - overschot * vNu + tlkNu;
    // 2027: zonder saldering
    var kosten27 = A * prijs - T * v27;
    var extra = kosten27 - kostenNu;

    var p = { T: T, A: A, prijs: prijs, v27: v27 };
    var opties = [];

    // Optie: ander contract
    var altType = contract === 'dynamisch' ? 'vast' : 'dynamisch';
    var vAlt = altType === 'dynamisch' ? vDyn : vVast;
    opties.push({
      id: 'contract',
      titel: altType === 'dynamisch' ? 'Overstappen naar een dynamisch contract' : 'Overstappen naar een vast of variabel contract',
      besparing: T * (vAlt - v27),
      kosten: 0,
      altType: altType
    });

    // Optie: slimmer verbruiken
    var gekozen = (inp.apparaten || []);
    var verschuifTotaal = 0;
    APPARATEN.forEach(function (a) { if (gekozen.indexOf(a.id) !== -1) verschuifTotaal += a.kwh; });
    var verschuif = Math.min(verschuifTotaal, T * 0.8, A * 0.8);
    opties.push({
      id: 'slim',
      titel: 'Slimmer verbruiken: apparaten aan als de zon schijnt',
      besparing: Math.max(0, verschuif) * (prijs - v27),
      kosten: 0,
      kwh: verschuif,
      gekozen: gekozen.length
    });

    // Optie: thuisbatterij
    var bType = inp.batterijType === 'vast' ? 'vast' : 'plugin';
    var cap = clamp(num(inp.batterijCap, bType === 'plugin' ? 2.7 : 10), 0.5, 40);
    var prijsPerKwh = inp.batterijPrijs != null && inp.batterijPrijs !== '' ? clamp(num(inp.batterijPrijs, null), 50, 3000) : null;
    var handel = clamp(num(inp.handel, 0), 0, 2000);
    var btw = !!inp.btw;
    var bat = batterijBerekening(p, { cap: cap, type: bType, prijsPerKwh: prijsPerKwh, handel: handel, btw: btw });

    // Beste grootte voor deze situatie (max netto over levensduur)
    var beste = null;
    var maxCap = bType === 'plugin' ? 8 : 25;
    for (var c = 1; c <= maxCap; c += 0.5) {
      var r = batterijBerekening(p, { cap: c, type: bType, prijsPerKwh: prijsPerKwh, handel: handel * (c / cap), btw: btw });
      if (!beste || r.nettoLevensduur > beste.nettoLevensduur) beste = r;
    }
    bat.beste = beste;
    bat.id = 'batterij';
    bat.titel = bType === 'plugin' ? 'Plug-and-play thuisbatterij' : 'Vaste thuisbatterij (met installateur)';
    opties.push(bat);

    return {
      profiel: prof,
      prijs: prijs,
      contract: contract,
      v27: v27,
      kostenNu: kostenNu,
      kosten27: kosten27,
      extra: extra,
      saldeerbaar: saldeerbaar,
      opties: opties
    };
  }

  var api = { DEFAULTS: DEFAULTS, APPARATEN: APPARATEN, bereken: bereken, batterijPrijsPerKwh: batterijPrijsPerKwh };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.SC = api;
})(this);
