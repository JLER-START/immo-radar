import json, os, yaml, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict

from .sites.base import BaseAdapter
from .sites.generic_css import GenericCSSAdapter
from .sites.immoweb import ImmowebAdapter
from .sites.zimmo import ZimmoAdapter
from .sites.immoscoop_list import ImmoscoopListAdapter
from .utils import now_utc_iso

ADAPTERS = {
    "generic_css": GenericCSSAdapter,
    "immoweb": ImmowebAdapter,
    "zimmo": ZimmoAdapter,
    "immoscoop_list": ImmoscoopListAdapter,   # <— deze regel toevoegen
}

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "output" / "listings.json"
FRONTEND_DATA = ROOT.parent / "frontend" / "data" / "listings.json"

def load_cfg():
    with open(ROOT/"config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def merge_first_seen(existing: Dict[str, Dict], items: List[Dict]) -> List[Dict]:
    now = now_utc_iso()
    existing_by_uid = {x.get("uid"): x for x in existing}
    merged = []
    for it in items:
        uid = it.get("uid")
        if not uid:
            continue
        prev = existing_by_uid.get(uid)
        if prev and prev.get("first_seen"):
            it["first_seen"] = prev["first_seen"]
        else:
            it["first_seen"] = now
        it["last_seen"] = now
        merged.append(it)
    return merged

def run_all():
    cfg = load_cfg()
    gfilters = cfg.get("filters", {})
    all_items: List[Dict] = []

    for site in cfg.get("sites", []):
        name = site.get("name", "onbekend")
        adapter_key = site.get("adapter")
        if adapter_key not in ADAPTERS:
            print(f"[WARN] Onbekende adapter: {adapter_key}")
            continue
        adapter_cls = ADAPTERS[adapter_key]
        adapter = adapter_cls(name, site)
        try:
            items = adapter.run(gfilters)
            all_items.extend(items)
            print(f"[OK] {name}: {len(items)} items")
        except Exception as e:
            print(f"[ERR] {name}: {e}")

    # Load existing
    existing = []
    if OUT_JSON.exists():
        try:
            existing = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        except Exception:
            existing = []

    merged = merge_first_seen({x.get("uid"): x for x in existing}, all_items)

    # Sort newest first by 'date_posted_iso' then 'first_seen'
    def sort_key(x):
        return (
            x.get("date_posted_iso") or "",
            x.get("first_seen") or ""
        )
    merged.sort(key=sort_key, reverse=True)

    OUT_JSON.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    # also copy to frontend
    FRONTEND_DATA.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_JSON} and {FRONTEND_DATA}")

if __name__ == "__main__":
    run_all()
