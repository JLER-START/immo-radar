from abc import ABC, abstractmethod
from typing import List, Dict

class BaseAdapter(ABC):
    """
    Contract for site scrapers. Each adapter returns a list of dict listings:
    {
      "uid": str,                # stable unique id (e.g., hash of source+url)
      "title": str,
      "url": str,
      "location": str|None,
      "price_eur": float|None,
      "date_posted_raw": str|None,
      "date_posted_iso": str|None,  # ISO 8601 if parseable
      "source": str,             # site name
      "scraped_at": str          # ISO 8601 UTC timestamp
    }
    """
    def __init__(self, name: str, cfg: dict):
        self.name = name
        self.cfg = cfg

    @abstractmethod
    def run(self, global_filters: dict) -> List[Dict]:
        pass
