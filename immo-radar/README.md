# Immo Radar — gratis, modulair scraper + dashboard

Jij wilt 2× per dag automatische updates van bouwgronden/panden in een mooi overzicht dat je via een URL kan delen. Dit project doet dat **gratis** met:
- **GitHub Actions** om 2× per dag te draaien (backend/scheduler).
- **Python** + `requests` + `BeautifulSoup` om te scrapen.
- **GitHub Pages** om een **statische website** te hosten (frontend).
- **Zonder** betaalde servers of databases.

> ⚠️ **Belangrijk (legal/ToS):** Sommige immosites **verbieden** scrapers in hun gebruiksvoorwaarden en blokkeren bots. Controleer steeds **robots.txt** en de **Terms of Service**. Gebruik dit project enkel op sites die toestemming geven, of vraag een API/CSV-export aan.

---

## Stap 1 — Maak een GitHub repo
1. Maak (of gebruik) een GitHub-account.
2. Maak een **nieuwe public repository** aan, bv. `immo-radar`.
3. Download dit zip-bestand en upload de inhoud naar je repo, of push via Git.

## Stap 2 — Activeer GitHub Pages
1. Ga in je repo naar **Settings → Pages**.
2. Kies **Source: Deploy from a branch**.
3. Selecteer branch **main** en folder **/ (root)** of **/docs** als je dat verkiest (hier gebruiken we root).
4. Sla op — je krijgt een publieke URL, bv. `https://jouwnaam.github.io/immo-radar`.

## Stap 3 — Scheduler aanzetten
- In `.github/workflows/scrape.yml` staat een **cron** die 2× per dag draait (ongeveer 07:05 en 19:05 Brussel-tijd, afhankelijk van zomer-/winteruur).
- Je kan ook handmatig draaien via **Actions → Scrape 2x per day → Run workflow**.

## Stap 4 — Configureren wat je zoekt
- Open `scraper/config.yaml`.
- Pas aan:
  - `filters.keywords`, `filters.locations`, `filters.price_max_eur`.
  - Voeg sites toe onder `sites:`.
- Voor eenvoudige sites kan je de **config-gedreven** `generic_css` adapter gebruiken met CSS-selectors (zie voorbeeld).
- Voor grote portalen (bv. Immoweb, Zimmo) zijn vaak **custom adapters** en juridische checks nodig — placeholders vind je in `sites/immoweb.py` en `sites/zimmo.py`.

## Stap 5 — Code draaien (lokaal, optioneel)
1. Installeer Python 3.11+ en `pip`.
2. In de projectmap:
   ```bash
   pip install -r scraper/requirements.txt
   python scraper/main.py
   ```
3. Resultaten komen in `scraper/output/listings.json` en worden gekopieerd naar `frontend/data/listings.json`.
4. Open `frontend/index.html` in je browser om het dashboard te bekijken.

## Hoe werkt het? (architectuur)
- **Scraper (backend):** GitHub Actions draait `python scraper/main.py`. De scrapers halen nieuwe listings op en zetten alles in één JSON-bestand.
- **Opslag:** Geen externe DB — de JSON wordt **gecommit** naar je Git-repo (gratis). Zo heb je automatisch **versiegeschiedenis**.
- **Frontend (URL voor Lies):** GitHub Pages serveert `frontend/` met een net overzicht, filters en sortering.

## Nieuw site toevoegen (generic_css)
Voor simpele sites met voorspelbare HTML-lijsten:
```yaml
- name: "MijnSite"
  adapter: "generic_css"
  start_urls:
    - "https://mijnsite.be/zoek?q=bouwgrond"
  selectors:
    list: ".listing"
    title: ".listing-title::text"
    url: ".listing-title a::attr(href)"
    location: ".listing-location::text"
    price: ".price::text"
    date_posted: ".date::text"
    url_prefix: "https://mijnsite.be"
```
> Tip: Rechtsklik → “Inspecteren” in je browser om CSS-selectors te vinden.

## Duplicaten & 'Nieuw' badge
- Listings krijgen een stabiele `uid` op basis van `source + url`.
- We bewaren `first_seen` en `last_seen`. Alles wat recenter dan 36u is, krijgt **Nieuw**.

## Grenzen & uitbreiden
- **Dynamische pagina’s** of sites met JavaScript rendering vereisen Playwright/Selenium (lastiger gratis te hosten). Start daarom met **statische** of **lichte** sites.
- Voor notificaties kan je later een **RSS** genereren of **email** koppelen, maar dit project focust op een gedeelde URL.

## Veelvoorkomende problemen
- *Niets verschijnt op de site*: wacht tot de eerste workflow gelopen heeft of run handmatig via Actions.
- *Selectoren matchen niet*: de HTML van de site is anders — pas je `selectors` aan.
- *403/anti-bot*: site blokkeert scrapers; probeer trager te scrapen of kies een andere bron met toestemming.

## Juridisch & fair use
- Scrape traag en beleefd (rate limiting).
- Respecteer robots.txt, ToS en vraag toestemming waar nodig.
- Gebruik bij voorkeur bronnen die **expliciet** scraping toestaan of een **API** bieden.

Veel succes! Stuck? Voeg de doel-sites hier toe en ik schrijf je adapters.
