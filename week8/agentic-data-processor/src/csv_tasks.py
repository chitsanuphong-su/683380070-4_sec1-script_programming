import csv
import os
from collections import defaultdict
from .utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)

class CSVTasks:
    def __init__(self):
        logger.info("CSVTasks initialized.")

    def load_csv(self, file_path):
        if not os.path.exists(file_path):
            logger.error(f"CSV file not found: {file_path}")
            return None
        try:
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                data = list(reader)
            logger.info(f"Successfully loaded {len(data)} rows from '{file_path}'.")
            return data
        except Exception as e:
            logger.error(f"Error loading CSV file '{file_path}': {e}")
            return None

    def save_csv(self, data, file_path, fieldnames=None):
        if not data:
            logger.warning("No data provided to save to CSV.")
            return False
        ensure_directory_exists(os.path.dirname(file_path))
        if fieldnames is None and isinstance(data[0], dict):
            fieldnames = list(data[0].keys())
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            logger.info(f"Successfully saved {len(data)} rows to '{file_path}'.")
            return True
        except Exception as e:
            logger.error(f"Error saving CSV file '{file_path}': {e}")
            return False

    def transform_csv_aggregate(self, data, group_by_field, aggregate_field, aggregate_type="sum"):
        if not data:
            return []
        aggregated_data = defaultdict(lambda: {'_count': 0, '_sum': 0.0})
        for row in data:
            group_value = row.get(group_by_field)
            if group_value is None:
                continue
            try:
                numeric_value = float(row.get(aggregate_field, 0))
                aggregated_data[group_value]['_sum'] += numeric_value
                aggregated_data[group_value]['_count'] += 1
            except (ValueError, TypeError):
                continue
        results = []
        for group_value, metrics in aggregated_data.items():
            result_row = {group_by_field: group_value}
            if aggregate_type == "sum":
                result_row[f'Total_{aggregate_field}'] = round(metrics['_sum'], 2)
            elif aggregate_type == "count":
                result_row[f'Count_{aggregate_field}'] = metrics['_count']
            elif aggregate_type == "average":
                result_row[f'Average_{aggregate_field}'] = round(metrics['_sum'] / metrics['_count'], 2) if metrics['_count'] > 0 else 0.0
            results.append(result_row)
        return results

    def filter_csv(self, data, filter_field, operator, value):
        if not data:
            return []
        filtered_data = []
        for row in data:
            field_value = row.get(filter_field)
            if field_value is None:
                continue
            try:
                compare_value = float(field_value) if isinstance(value, (int, float)) else str(field_value)
                ops = {
                    '>': compare_value > value,
                    '<': compare_value < value,
                    '>=': compare_value >= value,
                    '<=': compare_value <= value,
                    '==': compare_value == value,
                    '!=': compare_value != value
                }
                if ops.get(operator, False):
                    filtered_data.append(row)
            except Exception:
                continue
        return filtered_data