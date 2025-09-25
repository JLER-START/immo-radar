from typing import List, Dict
from .base import BaseAdapter

class ImmowebAdapter(BaseAdapter):
    def run(self, global_filters: dict) -> List[Dict]:
        # NOTE:
        # Many big portals actively prohibit scraping in their Terms of Service
        # and deploy anti-bot measures. Before implementing, verify robots.txt
        # and the site's ToS; consider contacting the site for API access.
        # This placeholder exists so you can wire in a custom adapter later.
        return []
