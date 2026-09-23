import os
from src.csv_handler import CSVHandler
from src.json_handler import JSONHandler
from src.utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)

def main():
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    ensure_directory_exists(data_dir)

    input_csv_path = os.path.join(data_dir, 'input_sales.csv')
    output_filtered_csv_path = os.path.join(data_dir, 'output_filtered_sales.csv')
    input_json_path = os.path.join(data_dir, 'input_inventory.json')
    output_updated_json_path = os.path.join(data_dir, 'output_updated_inventory.json')

    csv_proc = CSVHandler()
    json_proc = JSONHandler()

    logger.info("--- Starting CSV Data Processing Workflow ---")
    sales_data = csv_proc.read_csv_as_dicts(input_csv_path)
    if sales_data:
        processed_results = csv_proc.process_sales_data(sales_data, min_sale_amount=100.0)
        filtered_sales = processed_results["filtered_sales"]
        sales_summary = processed_results["summary"]
        
        csv_fieldnames = list(sales_data[0].keys())
        summary_row = {
            'OrderID': 'SUMMARY',
            'Product': 'Total/Avg',
            'Amount': sales_summary['Total Sales'],
            'Price': sales_summary['Average Item Price'],
            'Customer': f"Count: {sales_summary['Filtered Sales Count']}"
        }
        csv_proc.write_dicts_to_csv(filtered_sales + [summary_row], output_filtered_csv_path, csv_fieldnames)

    logger.info("--- Starting JSON Data Processing Workflow ---")
    inventory_data = json_proc.read_json(input_json_path)
    if inventory_data:
        json_proc.update_inventory(inventory_data, "PROD001", 60)
        json_proc.update_inventory(inventory_data, "PROD003", 75)
        new_product = {
            "id": "PROD004",
            "name": "Gaming Headset",
            "category": "Audio",
            "stock": 90,
            "details": {"brand": "SoundBlaster", "features": ["Noise Cancelling"]}
        }
        json_proc.add_product(inventory_data, new_product)
        json_proc.write_json(inventory_data, output_updated_json_path, indent=2)

if __name__ == "__main__":
    main()