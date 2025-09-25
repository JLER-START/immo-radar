from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict
from .base import BaseAdapter
from ..utils import http_get, parse_price_to_eur, make_uid, parse_human_date_to_iso, now_utc_iso

class GenericCSSAdapter(BaseAdapter):
    """
    Config-driven scraper for simple, static list pages.
    Requires in cfg:
      start_urls: [str, ...]
      selectors:
        list: ".row"                           # CSS voor elk kaartje (container of <a>)
        title: ".title::text"
        url: ".title a::attr(href)"            # of "::attr(href)" als list het <a>-element zelf is
        location: ".location::text"
        price: ".price::text"
        date_posted: ".date::text"
        url_prefix: "https://example.com"      # optioneel
    """
    def run(self, global_filters: dict) -> List[Dict]:
        sel = self.cfg.get("selectors", {})
        out: List[Dict] = []

        for url in self.cfg.get("start_urls", []):
            html, final_url = http_get(url)
            soup = BeautifulSoup(html, "lxml")
            cards = soup.select(sel.get("list")) if sel.get("list") else []

            for card in cards:
                # Helper om uit 'CSS::text' of 'CSS::attr(href)' te lezen.
                # Nieuw: als er GEEN CSS vóór '::' staat, gebruik dan het kaartje zelf (card).
                def pick(selector: str | None):
                    if not selector:
                        return None
                    if "::" in selector:
                        css, kind = selector.split("::", 1)
                        el = card if not css.strip() else card.select_one(css)
                        if not el:
                            return None
                        if kind == "text":
                            return el.get_text(strip=True)
                        if kind.startswith("attr(") and kind.endswith(")"):
                            attr = kind[5:-1]
                            return el.get(attr)
                        if kind.startswith("attr"):
                            start = kind.find("(") + 1
                            end = kind.rfind(")")
                            attr = kind[start:end]
                            return el.get(attr)
                        return None
                    else:
                        el = card.select_one(selector)
                        return el.get_text(strip=True) if el else None

                title = pick(sel.get("title"))
                url_rel = pick(sel.get("url"))
                # URL absolutiseren
                url_abs = url_rel
                if url_rel and self.cfg.get("selectors", {}).get("url_prefix"):
                    url_abs = urljoin(self.cfg["selectors"]["url_prefix"], url_rel)
                elif url_rel and str(url_rel).startswith("/"):
                    url_abs = urljoin(final_url, url_rel)

                location = pick(sel.get("location"))
                price_eur = parse_price_to_eur(pick(sel.get("price")))
                date_raw = pick(sel.get("date_posted"))
                date_iso = parse_human_date_to_iso(date_raw) if date_raw else None

                if not title or not url_abs:
                    continue

                out.append({
                    "uid": make_uid(self.name, url_abs),
                    "title": title,
                    "url": url_abs,
                    "location": location,
                    "price_eur": price_eur,
                    "date_posted_raw": date_raw,
                    "date_posted_iso": date_iso,
                    "source": self.name,
                    "scraped_at": now_utc_iso()
                })

        return out
