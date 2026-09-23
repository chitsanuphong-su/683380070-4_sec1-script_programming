import json
import os
from .utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)

class JSONTasks:
    def __init__(self):
        logger.info("JSONTasks initialized.")

    def load_json(self, file_path):
        if not os.path.exists(file_path):
            logger.error(f"JSON file not found: {file_path}")
            return None
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            logger.error(f"Error loading JSON file '{file_path}': {e}")
            return None

    def save_json(self, data, file_path, indent=2):
        ensure_directory_exists(os.path.dirname(file_path))
        try:
            with open(file_path, mode='w', encoding='utf-8') as file:
                json.dump(data, file, indent=indent, ensure_ascii=False)
            logger.info(f"Successfully saved JSON to '{file_path}'.")
            return True
        except Exception as e:
            logger.error(f"Error saving JSON file '{file_path}': {e}")
            return False

    def update_json_data(self, data, updates):
        if not data:
            return data
        modified_data = json.loads(json.dumps(data))
        for update in updates:
            path = update.get("path")
            value = update.get("value")
            operation = update.get("operation", "set")
            if path == "" and operation == "add_to_list" and isinstance(modified_data, list):
                modified_data.append(value)
                continue
            keys = path.split('.')
            current_node = modified_data
            for key in keys[:-1]:
                if isinstance(current_node, dict):
                    current_node = current_node.get(key)
                elif isinstance(current_node, list) and key.isdigit():
                    current_node = current_node[int(key)]
            target_key = keys[-1]
            if operation == "set":
                if isinstance(current_node, dict):
                    current_node[target_key] = value
                elif isinstance(current_node, list) and target_key.isdigit():
                    current_node[int(target_key)] = value
        return modified_data

    def query_json_data(self, data, path):
        if not data:
            return None
        keys = path.split('.')
        current_node = data
        for key in keys:
            if isinstance(current_node, dict):
                current_node = current_node.get(key)
            elif isinstance(current_node, list) and key.isdigit():
                current_node = current_node[int(key)]
            else:
                return None
        return current_node