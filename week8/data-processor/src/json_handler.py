import json
import os
from .utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)

class JSONHandler:
    """Handles reading, writing, and basic manipulation of JSON files."""
    def __init__(self):
        logger.info("JSONHandler initialized.")

    def read_json(self, file_path):
        if not os.path.exists(file_path):
            logger.error(f"JSON file not found: {file_path}")
            return None
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                data = json.load(file)
            logger.info(f"Successfully read JSON from '{file_path}'.")
            return data
        except Exception as e:
            logger.error(f"Error reading JSON file '{file_path}': {e}")
            return None

    def write_json(self, data, file_path, indent=4):
        ensure_directory_exists(os.path.dirname(file_path))
        try:
            with open(file_path, mode='w', encoding='utf-8') as file:
                json.dump(data, file, indent=indent, ensure_ascii=False)
            logger.info(f"Successfully wrote JSON to '{file_path}'.")
            return True
        except Exception as e:
            logger.error(f"Error writing JSON file '{file_path}': {e}")
            return False

    def update_inventory(self, inventory_data, product_id, new_stock_level):
        if not isinstance(inventory_data, list):
            return False
        for product in inventory_data:
            if product.get("id") == product_id:
                product["stock"] = new_stock_level
                logger.info(f"Updated stock for '{product_id}' to {new_stock_level}.")
                return True
        return False

    def add_product(self, inventory_data, new_product):
        if not isinstance(inventory_data, list):
            return False
        inventory_data.append(new_product)
        logger.info(f"Added new product: {new_product.get('name', 'N/A')}.")
        return True