import json
from .utils import setup_logging

logger = setup_logging(__name__)

class ConversionTasks:
    def __init__(self):
        logger.info("ConversionTasks initialized.")

    def csv_to_json(self, csv_data):
        if not csv_data:
            return []
        json_data = []
        for row in csv_data:
            json_row = {}
            for key, value in row.items():
                val_str = str(value).strip()
                if val_str.isdigit():
                    json_row[key] = int(val_str)
                elif val_str.replace('.', '', 1).isdigit():
                    json_row[key] = float(val_str)
                elif val_str.lower() in ['true', 'false']:
                    json_row[key] = val_str.lower() == 'true'
                elif val_str.lower() in ['null', '']:
                    json_row[key] = None
                else:
                    json_row[key] = val_str
            json_data.append(json_row)
        return json_data

    def json_to_csv(self, json_data, fieldnames=None):
        if not json_data:
            return [], []
        if fieldnames is None:
            all_keys = set()
            for item in json_data:
                for k, v in item.items():
                    if isinstance(v, dict):
                        for sub_k in v.keys():
                            all_keys.add(f"{k}.{sub_k}")
                    else:
                        all_keys.add(k)
            fieldnames = sorted(list(all_keys))
        csv_rows = []
        for item in json_data:
            row = {}
            for field in fieldnames:
                if '.' in field:
                    parts = field.split('.')
                    val = item.get(parts[0], {})
                    row[field] = val.get(parts[1], '') if isinstance(val, dict) else ''
                else:
                    val = item.get(field, '')
                    row[field] = json.dumps(val) if isinstance(val, (dict, list)) else val
            csv_rows.append(row)
        return csv_rows, fieldnames