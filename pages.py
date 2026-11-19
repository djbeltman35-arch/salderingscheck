#!/usr/bin/env python3
"""Bouwt de losse informatiepagina's van Salderingscheck.
Gebruik: python3 pages.py  (schrijft <slug>/index.html voor elke pagina)
Pas cijfers aan in de data hieronder en draai het script opnieuw."""
import json, html, os

SITE = "https://salderingscheck-nl.netlify.app"
GEWIJZIGD = "2026-11-16"
GEWIJZIGD_NL = "16 november 2026"

GC = '<script data-goatcounter="https://salderingscheck-nl.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>'

SUN_MARK = '<svg viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="12" fill="#f5b400"/><g stroke="#f5b400" stroke-width="5" stroke-linecap="round"><path d="M32 6v8M32 50v8M6 32h8M50 32h8M13.6 13.6l5.6 5.6M44.8 44.8l5.6 5.6M13.6 50.4l5.6-5.6M44.8 19.2l5.6-5.6"/></g></svg>'
DECO = '''<svg class="deco" viewBox="0 0 260 260" aria-hidden="true"><g stroke="#f5b400" stroke-width="10" stroke-linecap="round" opacity=".55"><path d="M170 18v24M170 158v24M90 100h24M226 100h24M113 43l17 17M210 140l17 17M113 157l17-17M210 60l17-17"/></g><circle cx="170" cy="100" r="44" fill="#f5b400" opacity=".9"/><g transform="translate(118 168) skewX(-20)" opacity=".75"><rect width="128" height="62" rx="5" fill="#0a3d2f" stroke="#cfe9dd" stroke-width="3"/><path d="M32 0v62M64 0v62M96 0v62M0 31h128" stroke="#cfe9dd" stroke-width="2.5"/></g></svg>'''

SITES = [
    ("https://boodschappenvergelijk.nl/", "Goedkope Boodschappen", "Zie bij welke supermarkt je boodschappenlijst het goedkoopst is."),
    ("https://goedkopertanken.netlify.app/", "Tankwijzer", "Brandstofprijzen in NL, BE en DE: tank goedkoper over de grens."),
    ("https://foutcodezoeker.nl/", "Foutcodezoeker", "Wat betekent die foutcode? Repareer je apparaat zelf."),
    ("https://euroroadrules.eu/nl/", "EuroRoadRules", "Vignetten, tol en milieuzones in heel Europa."),
    ("https://vluchtwijzer.netlify.app/", "Vluchtwijzer", "Vind de goedkoopste vliegtickets."),
    ("https://allesoporde.netlify.app/", "Op Orde", "Houd vaste lasten, deadlines en toeslagen bij."),
]

PAGINAS = [
    ("/", "Salderingscheck: bereken het zelf"),
    ("/terugleverkosten-2027/", "Terugleverkosten 2027 per leverancier"),
    ("/thuisbatterij-terugverdientijd/", "Thuisbatterij: wanneer verdien je hem terug?"),
    ("/einde-salderen-wat-nu/", "Einde salderen: wat moet je regelen?"),
]


def e(s):
    return html.escape(s, quote=True)


def pagina(slug, titel, h1, lead, beschrijving, body, faq, kruimel):
    url = f"{SITE}/{slug}/"
    graph = [
        {"@type": "Article", "headline": titel, "description": beschrijving, "inLanguage": "nl-NL",
         "datePublished": "2026-11-16", "dateModified": GEWIJZIGD, "mainEntityOfPage": url,
         "author": {"@type": "Person", "name": "Erik", "email": "djbeltman35@gmail.com"},
         "publisher": {"@type": "Organization", "name": "Salderingscheck", "url": SITE + "/"},
         "image": f"{SITE}/icons/og-{slug}.png"},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Salderingscheck", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": kruimel, "item": url}]},
    ]
    if faq:
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
    faq_html = ""
    if faq:
        faq_html = '<section class="card faq" aria-labelledby="h-faq"><h2 id="h-faq">Veelgestelde vragen</h2>' + "".join(
            f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in faq) + "</section>"
    andere = "".join(f'<a href="{u}"><b>{e(n)}</b><span>{e(t)}</span></a>' for u, n, t in PAGINAS_LINKS(slug))
    sites = "".join(f'<a href="{u}"><b>{e(n)}</b><span>{e(t)}</span></a>' for u, n, t in SITES)
    return f'''<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(titel)}</title>
<meta name="description" content="{e(beschrijving)}">
<link rel="canonical" href="{url}">
{GC}
<meta name="theme-color" content="#0e7c4a">
<link rel="preload" href="/fonts/big-shoulders-display-800.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/atkinson-hyperlegible-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/artikel.css">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" href="/icons/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<meta property="og:type" content="article">
<meta property="og:locale" content="nl_NL">
<meta property="og:site_name" content="Salderingscheck">
<meta property="og:title" content="{e(titel)}">
<meta property="og:description" content="{e(beschrijving)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/icons/og-{slug}.png">
<meta name="robots" content="max-image-preview:large">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
<header class="hero">
  {DECO}
  <div class="wrap">
    <a class="brand" href="/"><span class="mark" aria-hidden="true">{SUN_MARK}</span><b>Salderings<span>check</span></b></a>
    <nav class="crumbs" aria-label="Kruimelpad"><a href="/">Salderingscheck</a> › {e(kruimel)}</nav>
    <h1>{e(h1)}</h1>
    <p class="lead">{e(lead)}</p>
    <p class="meta">Bijgewerkt op <time datetime="{GEWIJZIGD}">{GEWIJZIGD_NL}</time> door Erik</p>
  </div>
</header>
<main class="wrap">
{body}
{faq_html}
  <section class="card" aria-labelledby="h-lees"><h2 id="h-lees">Lees ook</h2><div class="meer">{andere}</div></section>
  <section class="card" aria-labelledby="h-meer"><h2 id="h-meer">Meer gratis bespaarsites</h2><div class="meer">{sites}</div></section>
  <footer>
    <p>Gemaakt door Erik · <a href="mailto:djbeltman35@gmail.com">djbeltman35@gmail.com</a> · We tellen alleen anonieme bezoeken, zonder cookies.</p>
    <p>Aan deze informatie kunnen geen rechten worden ontleend. Controleer tarieven altijd bij je leverancier.</p>
  </footer>
</main>
</body>
</html>
'''


def PAGINAS_LINKS(huidig):
    teksten = {
        "/": "Bereken in 1 minuut wat het einde van salderen jou kost.",
        "/terugleverkosten-2027/": "Netto vergoeding per leverancier op een rij.",
        "/thuisbatterij-terugverdientijd/": "Wanneer een thuisbatterij loont, met rekenvoorbeelden.",
        "/einde-salderen-wat-nu/": "Checklist: dit regel je voor en na 1 januari 2027.",
    }
    return [(u, n, teksten[u]) for u, n in PAGINAS if u != f"/{huidig}/"]


CTA = '''<div class="cta"><b>{tekst}</b><a href="/#h-invoer">Bereken het voor jouw situatie <span aria-hidden="true">→</span></a></div>'''

# ---------------------------------------------------------------------------
# 1. Terugleverkosten 2027 per leverancier
# Bron: energiethuisadvies.nl (stand 9 november 2026), op basis van modelcontracten en tarievenbladen van leveranciers.
EEN_JAAR = [  # leverancier, vergoeding, terugleverkosten, netto (cent per kWh), btw-opmerking, bron (datum)
    ("Eneco", 9.920, 4.844, 5.08, "incl. btw", "modelcontract, 9-11-2026"),
    ("Oxxio", 9.315, 4.844, 4.47, "incl. btw", "modelcontract, 9-11-2026"),
    ("Vattenfall", 9.090, 4.985, 4.10, "btw niet vermeld", "aanbod, 20-10-2026"),
    ("DELTA Energie", 10.016, 6.516, 3.50, "vergoeding excl., kosten incl. btw", "tarieven, 5-11-2026"),
    ("Essent", 10.088, 7.008, 3.08, "incl. btw", "aanbod, 17-10-2026"),
    ("Energiedirect", 9.775, 8.775, 1.0, "vergoeding excl., kosten incl. btw", "tarievenblad, 1-11-2026"),
    ("Coolblue Energie", 10.10, 9.60, 0.50, "btw niet apart vermeld", "modelcontract, 5-11-2026"),
    ("Pure Energie", 11.500, 11.251, 0.25, "vergoeding excl., kosten incl. btw", "modelcontract, 26-10-2026"),
    ("Vandebron", 8.600, 8.350, 0.25, "incl. btw", "tarievenblad, 16-10-2026"),
    ("Zonopnaam Energie", 10.00, 10.00, 0.0, "kosten incl. btw", "tarievenblad, nov 2026"),
]
OVERIG = [  # leverancier, contract, vergoeding, kosten, netto, bron
    ("Eneco", "variabel", 13.165, 4.845, 8.32, "modelcontract, 9-11-2026"),
    ("Oxxio", "variabel", 12.601, 4.844, 7.76, "modelcontract, 9-11-2026"),
    ("DELTA Energie", "3 jaar vast", 8.879, 5.379, 3.50, "tarieven, 5-11-2026"),
    ("Essent", "3 jaar vast", 9.442, 7.821, 1.62, "aanbod, 17-10-2026"),
    ("Energiedirect", "3 jaar vast", 7.826, 6.826, 1.0, "tarievenblad, 1-11-2026"),
    ("NextEnergy", "variabel (voorlopig)", 13.04, 12.54, 0.50, "modelcontract, 19-10-2026"),
    ("Zonopnaam Energie", "vast (modelcontract)", 8.90, 8.90, 0.0, "modelcontract, okt 2026"),
]
DYNAMISCH_GEEN_TLK = ["Zonneplan", "NextEnergy", "Frank Energie (met Slim Sturen)", "easyEnergy", "ANWB Energie", "Sunergy",
                      "Samsam", "EnergyZero", "Hegg Energy", "Budget Energie", "Coolblue Energie", "Tibber"]


def ct(v):
    return f"{v:.3f}".rstrip("0").rstrip(".").replace(".", ",") if v else "0"


def ct2(v):
    return f"{v:.2f}".replace(".", ",")


def euro(v):
    return f"€ {round(v):,}".replace(",", ".")


def tabel_een_jaar():
    rows = []
    for i, (lev, verg, kost, netto, btw, bron) in enumerate(EEN_JAAR):
        cls = ' class="top3"' if i < 3 else ""
        rows.append(f'<tr{cls}><td><b>{e(lev)}</b><br><span class="bron">{e(btw)} · {e(bron)}</span></td>'
                    f'<td class="num"><b>{ct2(netto)}</b></td><td class="num">{euro(netto * 25)}</td>'
                    f'<td class="num">{ct(verg)}</td><td class="num">{ct(kost)}</td></tr>')
    return ('<div class="tablewrap"><table><caption class="note capt">'
            'Cent per kWh, vanaf 1 januari 2027. Per jaar: netto opbrengst bij 2.500 kWh teruglevering.</caption>'
            '<thead><tr><th scope="col">Leverancier (1 jaar vast)</th><th scope="col" class="num">Netto</th>'
            '<th scope="col" class="num">Per jaar*</th><th scope="col" class="num">Vergoeding</th>'
            '<th scope="col" class="num">Teruglever&shy;kosten</th></tr></thead><tbody>' + "".join(rows) + '</tbody></table></div>')


def tabel_overig():
    rows = "".join(f'<tr><td><b>{e(l)}</b><br><span class="bron">{e(c)} · {e(b)}</span></td><td class="num"><b>{ct2(n)}</b></td>'
                   f'<td class="num">{euro(n * 25)}</td><td class="num">{ct(v)}</td><td class="num">{ct(k)}</td></tr>'
                   for l, c, v, k, n, b in OVERIG)
    return ('<div class="tablewrap"><table><thead><tr><th scope="col">Leverancier en contract</th><th scope="col" class="num">Netto</th>'
            '<th scope="col" class="num">Per jaar*</th><th scope="col" class="num">Vergoeding</th><th scope="col" class="num">Teruglever&shy;kosten</th>'
            '</tr></thead><tbody>' + rows + '</tbody></table></div>')


TLK_BODY = f'''
  <section class="card">
    <div class="kort"><p><b>In het kort:</b> vanaf 1 januari 2027 krijg je per teruggeleverde kWh een vergoeding, maar betaal je ook terugleverkosten. Wat netto overblijft, verschilt enorm: bij 1 jaar vast van <b>0 cent</b> (Zonopnaam Energie) tot <b>5,08 cent</b> (Eneco). Bij 2.500 kWh teruglevering is dat het verschil tussen € 0 en € 127 per jaar.</p></div>
    <h2>Netto terugleververgoeding 2027, 1 jaar vast</h2>
    <p>Gesorteerd van hoog naar laag. Netto is vergoeding min terugleverkosten.</p>
    {tabel_een_jaar()}
    <h2>Variabel en meerjarig</h2>
    {tabel_overig()}
    <p class="note">* Netto per kWh × 2.500 kWh. Variabele tarieven kunnen nog wijzigen. Leveranciers vermelden btw niet allemaal op dezelfde manier; zie de opmerking per regel.</p>
    <h2>Nog niet (volledig) bekend</h2>
    <p>Greenchoice, UnitedConsumers en Engie hadden op 9 november 2026 nog geen officiële bedragen voor 2027 gepubliceerd. Vergelijkingsdata van WeetWatt (14 november 2026) noemt voorlopig Greenchoice 0,25 ct, United Consumers 0,50 ct en ENGIE 0,89 ct netto. Innova Energie noemt alleen terugleverkosten (9,59 ct inclusief btw). Budget Energie rekent met een vast bedrag per dag en staat daarom niet in de tabel.</p>
    <h2>Dynamisch contract: vaak geen terugleverkosten</h2>
    <p>Bij een dynamisch contract krijg je voor teruglevering de marktprijs van dat uur. Die is laag als de zon fel schijnt. Deze aanbieders rekenen in 2027 geen terugleverkosten bij hun dynamische contract:</p>
    <div class="chips">{"".join(f"<span>{e(x)}</span>" for x in DYNAMISCH_GEEN_TLK)}</div>
    <p>Sommige aanbieders rekenen wel een verkoopvergoeding, zoals Powerpeers (2,48 ct per kWh). Zonneplan geeft 2 ct inkoopvergoeding plus 10% bonus op de marktprijs.</p>
    {CTA.format(tekst="Wat betekent dit voor jou? Kies je leverancier in de Salderingscheck en zie direct je extra kosten per jaar.")}
    <h2>Zo vergelijk je eerlijk</h2>
    <ul>
      <li><b>Kijk naar netto, niet naar de vergoeding.</b> Een hoge vergoeding met hoge terugleverkosten levert minder op dan een lage vergoeding zonder kosten.</li>
      <li><b>Kijk ook naar je stroomprijs.</b> Haal je meer stroom van het net dan je teruglevert, dan telt de prijs per kWh afname zwaarder dan de terugleververgoeding.</li>
      <li><b>Overstappen kan vaak kosteloos</b> als je leverancier je voorwaarden wijzigt door het einde van salderen.</li>
    </ul>
    <h2>Bronnen</h2>
    <ul class="note">
      <li><a href="https://www.energiethuisadvies.nl/kennisbank/terugleverkosten-2027" rel="noopener">Energiethuisadvies: terugleverkosten 2027 per leverancier</a> (stand 9 november 2026, op basis van modelcontracten en tarievenbladen)</li>
      <li><a href="https://weetwatt.nl/terugleverkosten" rel="noopener">WeetWatt: terugleverkosten per energieleverancier</a> (14 november 2026)</li>
      <li><a href="https://www.energievergelijk.nl/nieuws/bij-deze-energieleveranciers-betaal-je-geen-terugleverkosten-in-2027" rel="noopener">Energievergelijk: geen terugleverkosten in 2027</a></li>
      <li><a href="https://www.rijksoverheid.nl/onderwerpen/energie-thuis/salderingsregeling" rel="noopener">Rijksoverheid: salderingsregeling</a></li>
    </ul>
  </section>'''

TLK_FAQ = [
    ("Welke leverancier heeft de hoogste terugleververgoeding in 2027?",
     "Bij 1 jaar vast heeft Eneco de hoogste netto vergoeding: 5,08 cent per kWh, gevolgd door Oxxio (4,47 ct) en Vattenfall (4,10 ct), stand 9 november 2026. Bij variabele contracten liggen Eneco (8,32 ct) en Oxxio (7,76 ct) nog hoger, maar die tarieven kunnen wijzigen."),
    ("Wat zijn terugleverkosten?",
     "Kosten die je leverancier per teruggeleverde kWh rekent, omdat hij jouw stroom moet afnemen en verwerken. Vanaf 2027 staan ze per kWh op je rekening en worden ze verrekend met de terugleververgoeding."),
    ("Hoeveel moet mijn leverancier minimaal vergoeden?",
     "Van 2027 tot 2030 minimaal 50% van het kale leveringstarief: de stroomprijs zonder energiebelasting en btw. Daar gaan de terugleverkosten nog vanaf."),
    ("Betaal ik terugleverkosten bij een dynamisch contract?",
     "Bij veel aanbieders niet, zoals Zonneplan, Frank Energie, ANWB Energie, Tibber en easyEnergy. Je krijgt dan wel de marktprijs van dat uur, die laag is als de zon fel schijnt."),
]

# ---------------------------------------------------------------------------
# 2. Thuisbatterij terugverdientijd (berekend met calc.js, 10 panelen / 3.000 kWh en 16 panelen / 4.000 kWh, netto vergoeding 2 ct)
BATTERIJ = [  # situatie, type, kWh, prijs/kWh, aanschaf, besparing/jaar, terugverdientijd, netto na 12 jaar
    ("Plug-and-play", 2.7, 300, 810, 105, 7.7, 453),
    ("Plug-and-play", 2.7, 420, 1134, 105, 10.8, 129),
    ("Plug-and-play", 5, 300, 1500, 160, 9.4, 422),
    ("Plug-and-play", 5, 420, 2100, 160, 13.1, -178),
    ("Vast met installatie", 5, 650, 3250, 160, 20.3, -1328),
    ("Vast met installatie", 10, 650, 6500, 220, 29.5, -3854),
]


def tabel_batterij():
    rows = []
    for t, cap, prijs, aanschaf, bespaar, tvt, netto in BATTERIJ:
        nclass = "goed" if netto > 0 else "neg"
        teken = "+" if netto > 0 else "−"
        rows.append(f'<tr><td>{e(t)}</td><td class="num">{str(cap).replace(".", ",")} kWh</td><td class="num">€ {prijs}</td>'
                    f'<td class="num">{euro(aanschaf)}</td><td class="num">{euro(bespaar)}</td>'
                    f'<td class="num"><b>{str(tvt).replace(".", ",")} jaar</b></td><td class="num {nclass}">{teken}{euro(abs(netto))}</td></tr>')
    return ('<div class="tablewrap"><table><thead><tr><th scope="col">Soort</th><th scope="col" class="num">Grootte</th>'
            '<th scope="col" class="num">Prijs/kWh</th><th scope="col" class="num">Aanschaf</th><th scope="col" class="num">Besparing/jaar</th>'
            '<th scope="col" class="num">Terugverdiend</th><th scope="col" class="num">Na 12 jaar</th></tr></thead><tbody>'
            + "".join(rows) + '</tbody></table></div>')


BAT_BODY = f'''
  <section class="card">
    <div class="kort"><p><b>In het kort:</b> een kleine plug-and-play batterij van rond de € 300 per kWh verdient zich in ongeveer 8 jaar terug. Een grote vaste batterij met installatie verdient zich bij een gemiddeld huishouden meestal <b>niet</b> terug binnen de levensduur van 10 tot 15 jaar.</p></div>
    <h2>Rekenvoorbeelden</h2>
    <p>Huishouden met 10 zonnepanelen (400 Wp) en 3.000 kWh verbruik, stroomprijs € 0,27, netto terugleververgoeding 2 cent per kWh.</p>
    {tabel_batterij()}
    <p class="note">Berekend met dezelfde rekenmethode als de Salderingscheck: 90% bruikbare capaciteit, 90% rendement, afnemende meeropbrengst bij grotere batterijen, levensduur 12 jaar. Zonder extra opbrengst uit handel in stroom.</p>
    {CTA.format(tekst="Vul je eigen panelen, verbruik en offerteprijs in en zie de terugverdientijd en de beste grootte voor jou.")}
    <h2>Waarom kleiner vaak beter is</h2>
    <p>De eerste kWh opslag wordt bijna elke zonnige dag vol en 's avonds weer leeg. Elke extra kWh wordt minder vaak gebruikt, vooral in de winter, als je weinig overschot hebt. Daardoor groeit de besparing veel langzamer dan de prijs.</p>
    <h2>Vijf dingen die bepalen of hij loont</h2>
    <ol class="steps">
      <li><b>Prijs per kWh opslag</b>Plug-and-play kost gemiddeld ruim € 400 per kWh, vast met installatie € 600 tot € 850. Test-Aankoop adviseert te mikken op rond € 300 en niet meer dan € 450 per kWh.</li>
      <li><b>Hoeveel je teruglevert</b>Zonder overschot overdag valt er niets op te slaan.</li>
      <li><b>Je verbruik 's avonds</b>De batterij levert alleen op als je de opgeslagen stroom ook gebruikt.</li>
      <li><b>Je netto terugleververgoeding</b>Krijg je 5 cent per kWh terug, dan levert opslaan minder op dan bij 0 cent. Zie de <a href="/terugleverkosten-2027/">tabel per leverancier</a>.</li>
      <li><b>Handel met een dynamisch contract</b>Met slim laden en ontladen kun je extra verdienen, maar dat wisselt sterk. Reken alleen met wat een aanbieder echt garandeert.</li>
    </ol>
    <h2>Goed om te weten</h2>
    <ul>
      <li>Een plug-and-play batterij via het stopcontact mag wettelijk maximaal 800 watt aan je huis leveren.</li>
      <li>Er is geen landelijke subsidie voor thuisbatterijen. Pas op voor advertenties die dat beweren.</li>
      <li>Btw terugvragen kan onder voorwaarden als je handelt in stroom. Je draagt dan wel een vast bedrag van ongeveer € 15 per kWh capaciteit af.</li>
      <li>De ACM waarschuwt dat veel aanbieders het te rooskleurig voorstellen. Reken dus altijd zelf.</li>
    </ul>
    <h2>Bronnen</h2>
    <ul class="note">
      <li><a href="https://www.test-aankoop.be/woning-energie/hernieuwbare-energie/nieuws/beste-plug-and-play-thuisbatterijen" rel="noopener">Test-Aankoop: beste plug-and-play thuisbatterijen</a></li>
      <li><a href="https://id.nl/energie-en-klimaat/elektriciteit/batterijen/dit-zijn-de-10-meest-gestelde-vragen-over-thuisbatterijen" rel="noopener">ID.nl: meest gestelde vragen over thuisbatterijen</a></li>
      <li><a href="https://www.autoblog.nl/nieuws/hoera-de-thuisbatterij-is-eindelijk-betaalbaar-7150321" rel="noopener">Autoblog: ACM over thuisbatterijen</a></li>
      <li><a href="https://www.energiethuisadvies.nl/kennisbank/terugleverkosten-2027" rel="noopener">Energiethuisadvies: terugleverkosten 2027</a></li>
    </ul>
  </section>'''

BAT_FAQ = [
    ("Wat is de terugverdientijd van een thuisbatterij?",
     "Bij een gemiddeld huishouden met zonnepanelen: ongeveer 8 jaar voor een kleine plug-and-play batterij van rond € 300 per kWh, ruim 10 jaar bij € 420 per kWh, en vaak 20 jaar of meer voor een vaste batterij met installatie. De levensduur is 10 tot 15 jaar."),
    ("Welke grootte thuisbatterij heb ik nodig?",
     "Meestal kleiner dan je denkt. De eerste kWh leveren het meest op. Voor veel huishoudens rendeert 2 tot 5 kWh het best. De Salderingscheck rekent de beste grootte voor jouw situatie uit."),
    ("Is er subsidie op een thuisbatterij?",
     "Nee, er is geen landelijke subsidie voor thuisbatterijen. Onder voorwaarden kun je wel de btw terugvragen als je handelt in stroom."),
    ("Mag ik een thuisbatterij in het stopcontact steken?",
     "Ja, een plug-and-play batterij mag via het stopcontact maximaal 800 watt aan je huis leveren."),
]

# ---------------------------------------------------------------------------
# 3. Einde salderen: wat nu?
WATNU_BODY = f'''
  <section class="card">
    <div class="kort"><p><b>In het kort:</b> de salderingsregeling stopt op 1 januari 2027, in één keer en zonder afbouw. Dat geldt ook als je vaste contract doorloopt. Met deze zes stappen beperk je de schade.</p></div>
    <h2>Checklist: zo bereid je je voor</h2>
    <ol class="steps">
      <li><b>Reken uit wat het jou kost</b>Met je teruglevering en afname van de jaarafrekening zie je in de <a href="/#h-invoer">Salderingscheck</a> wat je vanaf 2027 per jaar extra betaalt.</li>
      <li><b>Check je netto terugleververgoeding</b>Vergoeding min terugleverkosten verschilt per leverancier van 0 tot ruim 5 cent per kWh bij 1 jaar vast. Bekijk de <a href="/terugleverkosten-2027/">tabel per leverancier</a>.</li>
      <li><b>Overweeg over te stappen</b>Wijzigt je leverancier je voorwaarden door het einde van salderen, dan mag je vaak kosteloos opzeggen. Vergelijk ook de stroomprijs per kWh.</li>
      <li><b>Gebruik meer zonnestroom zelf</b>Laat wasmachine, vaatwasser en droger overdag draaien, laad je auto als de zon schijnt en zet een boiler of warmtepomp op zonnestroom. Dat kost niets.</li>
      <li><b>Pas je termijnbedrag aan</b>Je teruglevering levert minder op, dus de kans op een naheffing groeit. Verhoog je voorschot op tijd.</li>
      <li><b>Thuisbatterij: eerst rekenen</b>Een kleine, goedkope batterij kan lonen, een grote vaak niet. Lees <a href="/thuisbatterij-terugverdientijd/">wanneer een thuisbatterij zich terugverdient</a>.</li>
    </ol>
    {CTA.format(tekst="Begin bij stap 1: zie in 1 minuut wat het einde van salderen jou kost.")}
    <h2>Wat verandert er precies?</h2>
    <p>Nu mag je je teruggeleverde stroom wegstrepen tegen de stroom die je van het net haalt, inclusief energiebelasting en btw. Vanaf 1 januari 2027 betaal je voor alle stroom van het net de volle prijs. Voor teruglevering krijg je alleen een terugleververgoeding, waar terugleverkosten vanaf gaan. Van 2027 tot 2030 moet die vergoeding minimaal 50% van het kale leveringstarief zijn.</p>
    <h2>Verdienen zonnepanelen zich nog terug?</h2>
    <p>Ja. Volgens de Rijksoverheid verdienen zonnepanelen zich ook na 2027 terug, maar het duurt langer. Hoe meer zonnestroom je zelf gebruikt, hoe sneller.</p>
    <h2>Bronnen</h2>
    <ul class="note">
      <li><a href="https://www.rijksoverheid.nl/onderwerpen/energie-thuis/salderingsregeling" rel="noopener">Rijksoverheid: salderingsregeling</a></li>
      <li><a href="https://selectra.nl/energie/zonnepanelen/salderingsregeling" rel="noopener">Selectra: einde salderingsregeling</a></li>
      <li><a href="https://www.energiethuisadvies.nl/kennisbank/terugleverkosten-2027" rel="noopener">Energiethuisadvies: terugleverkosten 2027</a></li>
    </ul>
  </section>'''

WATNU_FAQ = [
    ("Wanneer stopt de salderingsregeling?",
     "Op 1 januari 2027, in één keer en zonder afbouw. Tot en met 31 december 2026 saldeer je nog volledig."),
    ("Geldt het einde van salderen ook als mijn vaste contract doorloopt?",
     "Ja. Het wettelijke einde geldt voor iedereen, ook met een vast contract dat na 1 januari 2027 doorloopt."),
    ("Moet ik mijn termijnbedrag aanpassen?",
     "Dat is verstandig. Omdat teruglevering minder oplevert, betaal je vanaf 2027 meer. Een hoger voorschot voorkomt een grote naheffing bij de jaarafrekening."),
    ("Wat kan ik het beste doen na het einde van salderen?",
     "Zelf meer zonnestroom gebruiken is gratis en levert het meest op. Daarna: een leverancier kiezen met een goede netto terugleververgoeding, en alleen een thuisbatterij kopen als die zich binnen de levensduur terugverdient."),
]


OVER_BODY = f'''
  <section class="card" aria-labelledby="h-wie"><h2 id="h-wie">Wie maakt dit?</h2>
  <p>Salderingscheck is gemaakt door Erik uit Rijssen. Hij bouwt gratis sites die mensen helpen geld te besparen, zoals Tankwijzer en Goedkope Boodschappen. Er zit geen energieleverancier of batterijfabrikant achter.</p></section>
  <section class="card" aria-labelledby="h-hoe"><h2 id="h-hoe">Hoe rekenen we?</h2>
  <ul>
  <li><b>Opwek:</b> gemiddeld 0,9 kWh per wattpiek per jaar. Ken je je echte cijfers, vul dan de meterstanden in.</li>
  <li><b>Direct verbruik:</b> standaard 30% van je opwek, met een maximum van de helft van je verbruik.</li>
  <li><b>2026 met saldering</b> vergelijken we met <b>2027 zonder saldering</b>: wat je teruglevert, krijg je dan alleen nog vergoed tegen de netto terugleververgoeding van je leverancier.</li>
  <li><b>Netto vergoeding</b> per leverancier komt uit de gepubliceerde tarieven (zie <a href="/terugleverkosten-2027/">terugleverkosten 2027</a>). We controleren dit elke maand.</li>
  <li><b>Thuisbatterij:</b> 250 laadcycli per jaar, 90% bruikbaar, 90% rendement, levensduur 12 jaar, met afnemende meeropbrengst bij grotere batterijen.</li>
  </ul>
  <p>Het blijft een schatting. Je echte uitkomst hangt af van je verbruikspatroon, je contract en het weer.</p></section>
  <section class="card" aria-labelledby="h-privacy"><h2 id="h-privacy">Privacy</h2>
  <p>Alles wat je invult blijft op je eigen apparaat; er gaat niets naar een server. We tellen alleen anonieme bezoeken met GoatCounter, zonder cookies en zonder je te volgen op andere sites.</p></section>
  <section class="card" aria-labelledby="h-geld"><h2 id="h-geld">Hoe verdient deze site geld?</h2>
  <p>De site is gratis. Bij sommige links naar winkels of vergelijkers kan Erik een kleine vergoeding krijgen als je iets koopt. Dat kost jou niets extra en verandert niets aan de berekening: de uitkomst en de volgorde van leveranciers worden nooit door een partner bepaald. Zulke links zijn gemarkeerd.</p></section>
  <section class="card" aria-labelledby="h-widget"><h2 id="h-widget">Zet de rekentool op je eigen site</h2>
  <p>Heb je een site over zonnepanelen, wonen of geld besparen? Plaats de gratis widget met deze code:</p>
  <pre class="code"><code>&lt;iframe src="{SITE}/embed/" title="Salderingscheck: wat kost het einde van salderen?" width="100%" height="500" style="border:0;max-width:440px" loading="lazy"&gt;&lt;/iframe&gt;</code></pre>
  <p><a href="/embed/">Bekijk de widget</a>. Gratis, zonder cookies of reclame.</p></section>
  <section class="card" aria-labelledby="h-contact"><h2 id="h-contact">Fout gezien of een vraag?</h2>
  <p>Mail Erik: <a href="mailto:djbeltman35@gmail.com">djbeltman35@gmail.com</a>. Klopt een tarief niet meer, dan passen we het zo snel mogelijk aan.</p></section>
'''

TE_BOUWEN = [
    ("terugleverkosten-2027", "Terugleverkosten 2027 per leverancier: wat houd je netto over?",
     "Terugleverkosten 2027 per leverancier", "Vergoeding, terugleverkosten en wat je netto overhoudt per teruggeleverde kWh, voor alle bekende leveranciers op een rij.",
     "Netto terugleververgoeding 2027 per energieleverancier: van 0 tot ruim 5 cent per kWh bij 1 jaar vast. Vergelijk Eneco, Oxxio, Vattenfall, DELTA, Essent en meer.",
     TLK_BODY, TLK_FAQ, "Terugleverkosten 2027"),
    ("thuisbatterij-terugverdientijd", "Thuisbatterij terugverdientijd 2027: wanneer loont hij?",
     "Wanneer verdien je een thuisbatterij terug?", "Eerlijke rekenvoorbeelden voor plug-and-play en vaste thuisbatterijen na het einde van salderen.",
     "Terugverdientijd van een thuisbatterij na 2027: kleine plug-and-play rond 8 jaar, grote vaste batterij vaak nooit. Rekenvoorbeelden en de vijf dingen die bepalen of hij loont.",
     BAT_BODY, BAT_FAQ, "Thuisbatterij terugverdientijd"),
    ("einde-salderen-wat-nu", "Einde salderen 2027: wat moet je regelen? Checklist",
     "Einde salderen: wat moet je nu regelen?", "Zes stappen om je voor te bereiden op 1 januari 2027, als de salderingsregeling stopt.",
     "Einde salderingsregeling op 1 januari 2027: checklist met zes stappen. Kosten berekenen, leverancier vergelijken, zelf meer verbruiken, voorschot aanpassen en eerlijk over de thuisbatterij.",
     WATNU_BODY, WATNU_FAQ, "Einde salderen: wat nu?"),
    ("over", "Over Salderingscheck: wie, hoe we rekenen en privacy",
     "Over de Salderingscheck", "Wie de site maakt, hoe de berekening werkt, wat er met je gegevens gebeurt en hoe je de rekentool op je eigen site zet.",
     "Over Salderingscheck: onafhankelijke, gratis rekentool van Erik. Uitleg van de berekening, bronnen, privacy zonder cookies en een gratis widget voor je eigen site.",
     OVER_BODY, None, "Over"),
]

if __name__ == "__main__":
    for slug, titel, h1, lead, besch, body, faq, kruimel in TE_BOUWEN:
        os.makedirs(slug, exist_ok=True)
        with open(os.path.join(slug, "index.html"), "w", encoding="utf-8") as f:
            f.write(pagina(slug, titel, h1, lead, besch, body, faq, kruimel))
        print("geschreven:", slug)
