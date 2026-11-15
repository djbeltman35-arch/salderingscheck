# Salderingscheck

Gratis rekentool: wat kost het einde van de salderingsregeling (1 januari 2027) jou, en wat is het slimst om te doen?

Live: https://salderingscheck-nl.netlify.app/

## Bestanden

- `index.html` – pagina, teksten, SEO en opmaak
- `calc.js` – alle berekeningen en uitgangspunten (`DEFAULTS` bovenaan)
- `app.js` – interface; **partnerlinks staan bovenaan in `PARTNERS`**
- `sw.js`, `manifest.webmanifest`, `icons/` – installeerbare app en offline werken

## Partnerlinks toevoegen

In `app.js`, blok `PARTNERS`: vervang de `url` door je affiliate-link van Daisycon of Awin en zet `affiliate: true`.
Dan krijgt de link automatisch `rel="sponsored"` en verschijnt onderaan de melding over partnerlinks.

## Uitgangspunten bijwerken

Alle tarieven staan in `calc.js` onder `DEFAULTS`. Pas bij wijzigingen ook de teksten in `index.html` (blok "Goed om te weten") en de datum onder "Bronnen" aan.
Verhoog bij elke wijziging `CACHE` in `sw.js` (bijv. `salderingscheck-v2`), zodat bezoekers met de app direct de nieuwe versie krijgen.
