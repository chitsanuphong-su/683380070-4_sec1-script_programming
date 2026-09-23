# Agentic Data Processor

An automated, JSON-configured data processing pipeline built in Python. It executes ETL-style tasks across CSV and JSON datasets—including data aggregation, dynamic JSON path updates, format conversions, and structured audit logging.

## Features

- **Config-Driven Architecture:** Define data processing workflows declaratively via `configs/data_pipeline_config.json`.
- **CSV Data Operations:** Load, filter, aggregate, and save structured CSV data.
- **JSON Data Operations:** Load, save, query nested paths, and update deep JSON structures dynamically.
- **Format Conversion:** Convert flat CSV data to typed JSON objects seamlessly.
- **Audit Logging:** Automatically generates timestamped JSON execution reports in the `reports/` directory.

---

## Project Structure

```text
agentic-data-processor/
│
├── configs/
│   └── data_pipeline_config.json   # Pipeline task configurations
├── data/
│   ├── input_sales.csv             # Sample CSV input
│   └── input_inventory.json        # Sample JSON input
├── reports/                        # Auto-generated audit logs
├── src/
│   ├── __init__.py
│   ├── config_parser.py            # Validates and loads pipeline configs
│   ├── conversion_tasks.py        # CSV/JSON conversion utilities
│   ├── csv_tasks.py                # CSV loading, saving, and aggregation
│   ├── data_agent.py              # Main task runner and logger
│   ├── json_tasks.py               # JSON loading, updating, and querying
│   └── utils.py                    # Logging setup and directory helpers
├── .gitignore
├── main.py                         # Application entry point
└── README.md