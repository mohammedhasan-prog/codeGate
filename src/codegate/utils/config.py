import os
import yaml
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.config_path = Path.home() / ".codegate" / "config.yaml"
        self.config = self._load_config()

    def _load_config(self):
        if not self.config_path.exists():
            self._create_default_config()
        
        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)
            
        # Resolve environment variables
        if "api_key" in config.get("gemini", {}) and config["gemini"]["api_key"].startswith("${"):
            var_name = config["gemini"]["api_key"].strip("${}")
            config["gemini"]["api_key"] = os.environ.get(var_name)

        return config

    def _create_default_config(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        default_config = {
            "gemini": {
                "api_key": "${GEMINI_API_KEY}",
                "model": "gemini-1.5-pro",
                "temperature": 0.1,
                "max_tokens": 4000,
            },
            "settings": {
                "save_history": True,
                "history_path": "~/.codegate/history.json",
                "enable_caching": True,
                "cache_duration": 24,
            },
            "output": {
                "colored": True,
                "verbose": False,
            },
        }
        with open(self.config_path, "w") as f:
            yaml.dump(default_config, f, default_flow_style=False)

    def get(self, key, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

config_manager = ConfigManager()
