import re, json
from typing import List, Dict, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base import BaseAdapter
from ..utils import http_get, parse_price_to_eur, make_uid, parse_human_date_to_iso, now_utc_iso

IMMO_BASE = "https://www.immoscoop.be"

def find_detail_links(html: str) -> List[str]:
    """
    Pak alle detail-URL's uit HTML of embedded JSON.
    We zoeken naar strings die op '/te-koop/...' lijken.
    """
    links = set(re.findall(r'\/te-koop\/[a-z0-9\-\/]+', html, flags=re.IGNORECASE))
    # kleine sanity: geen /te-koop/op-lijst... etc
    links = {u for u in links if not u.startswith("/te-koop/op-")}
    return sorted(links)

def pick_og(soup: BeautifulSoup, prop: str) -> Optional[str]:
    el = soup.find("meta", attrs={"property": prop}) or soup.find("meta", attrs={"name": prop})
    return el.get("content").strip() if el and el.get("content") else None

def parse_jsonld_price(soup: BeautifulSoup) -> Optional[float]:
    # Zoek schema.org JSON-LD met offers->price
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(tag.string or "")
        except Exception:
            continue
        # kan lijst of object zijn
        candidates = data if isinstance(data, list) else [data]
        for obj in candidates:
            offer = obj.get("offers") if isinstance(obj, dict) else None
            if isinstance(offer, dict):
                price = offer.get("price") or offer.get("highPrice") or offer.get("lowPrice")
                if price:
                    return parse_price_to_eur(str(price))
            # soms zit price elders
            if isinstance(obj, dict) and "price" in obj:
                return parse_price_to_eur(str(obj["price"]))
    return None

class ImmoscoopListAdapter(BaseAdapter):
    """
    1) vind alle detail-links op de lijstpagina (uit HTML/embedded JSON)
    2) haal per detailpagina titel/prijs/locatie uit og: meta's en JSON-LD
    """
    def run(self, global_filters: dict) -> List[Dict]:
        out: List[Dict] = []
        for url in self.cfg.get("start_urls", []):
            html, final_url = http_get(url)
            detail_rel = find_detail_links(html)
            for rel in detail_rel:
                abs_url = urljoin(IMMO_BASE, rel)

                try:
                    dhtml, dfinal = http_get(abs_url, sleep=0.5)
                except Exception:
                    continue

                soup = BeautifulSoup(dhtml, "lxml")

                title = pick_og(soup, "og:title") or (soup.find("h1").get_text(strip=True) if soup.find("h1") else None)
                location = pick_og(soup, "og:description")
                price_eur = parse_jsonld_price(soup)

                if not title:
                    # fallback: iets uit <title>
                    t = soup.find("title")
                    if t:
                        title = t.get_text(strip=True)

                if not title:
                    continue  # zonder titel nemen we het item niet op

                out.append({
                    "uid": make_uid(self.name, abs_url),
                    "title": title,
                    "url": abs_url,
                    "location": location,
                    "price_eur": price_eur,
                    "date_posted_raw": None,
                    "date_posted_iso": None,
                    "source": self.name,
                    "scraped_at": now_utc_iso()
                })
        return out
