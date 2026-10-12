import json
import os
from datetime import datetime
from typing import Set

CACHE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache", "seen_items.json")
MAX_CACHE_SIZE = 3000

class CacheManager:
    def __init__(self, cache_path: str = CACHE_PATH):
        self.cache_path = cache_path
        self.seen_ids: Set[str] = set()
        self.load()

    def load(self):
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.seen_ids = set(data.get("seen_ids", []))
            except Exception as e:
                print(f"[Cache] Warning: Could not read cache ({e}), initializing empty.")
                self.seen_ids = set()
        else:
            self.seen_ids = set()

    def is_seen(self, item_id: str) -> bool:
        return item_id in self.seen_ids

    def mark_seen(self, item_id: str):
        self.seen_ids.add(item_id)

    def save(self):
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        # Keep the most recent items if cache exceeds limit
        ids_list = list(self.seen_ids)
        if len(ids_list) > MAX_CACHE_SIZE:
            ids_list = ids_list[-MAX_CACHE_SIZE:]
            self.seen_ids = set(ids_list)

        data = {
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "seen_count": len(ids_list),
            "seen_ids": ids_list
        }
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
