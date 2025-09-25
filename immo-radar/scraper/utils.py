import re, time, hashlib, requests, dateparser, os
from datetime import datetime, timezone
from urllib.parse import urljoin

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ImmoScraper/1.0; +https://github.com/)"
}

def now_utc_iso():
    return datetime.now(timezone.utc).isoformat()

def http_get(url, sleep=1.0, headers=None):
    time.sleep(sleep)  # be polite
    resp = requests.get(url, headers=headers or DEFAULT_HEADERS, timeout=25)
    resp.raise_for_status()
    return resp.text, resp.url  # return final URL after redirects

def parse_price_to_eur(text: str):
    if not text:
        return None
    t = text.lower().replace("\xa0"," ").replace(",", ".")
    # keep digits and dots
    nums = re.findall(r"[0-9.]+", t)
    if not nums:
        return None
    try:
        val = float("".join(nums))
        return val
    except:
        return None

def make_uid(source: str, url: str):
    return hashlib.sha256(f"{source}|{url}".encode()).hexdigest()[:16]

def parse_human_date_to_iso(text: str, tz: str = "Europe/Brussels"):
    if not text:
        return None
    dt = dateparser.parse(text, settings={"TIMEZONE": tz, "RETURN_AS_TIMEZONE_AWARE": True})
    if not dt:
        return None
    return dt.astimezone(timezone.utc).isoformat()
