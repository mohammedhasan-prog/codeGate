import json
import hashlib
import time
from pathlib import Path
from .config import config_manager

class Cache:
    def __init__(self):
        self.cache_dir = Path.home() / ".codegate" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = config_manager.get("settings.cache_duration", 24) * 3600  # in seconds

    def _get_cache_key(self, code):
        return hashlib.sha256(code.encode()).hexdigest()

    def get(self, code):
        if not config_manager.get("settings.enable_caching"):
            return None

        cache_key = self._get_cache_key(code)
        cache_file = self.cache_dir / cache_key

        if cache_file.exists():
            if time.time() - cache_file.stat().st_mtime < self.cache_duration:
                with open(cache_file, "r") as f:
                    return json.load(f)
        return None

    def set(self, code, data):
        if not config_manager.get("settings.enable_caching"):
            return

        cache_key = self._get_cache_key(code)
        cache_file = self.cache_dir / cache_key
        with open(cache_file, "w") as f:
            json.dump(data, f)

cache = Cache()
