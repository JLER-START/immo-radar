from typing import List, Dict
from .base import BaseAdapter

class ZimmoAdapter(BaseAdapter):
    def run(self, global_filters: dict) -> List[Dict]:
        # See note in ImmowebAdapter. Verify legal/ToS constraints first.
        return []
