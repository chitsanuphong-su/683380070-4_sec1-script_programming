import json
import os

class ConfigParser:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {}

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self._validate_config()
        return self.config

    def _validate_config(self):
        required_fields = ["start_url", "pagination_selector", "item_container_selector", "item_data_selectors"]
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required field in config: '{field}'")