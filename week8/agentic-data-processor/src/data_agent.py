import os
import json
import datetime
from .utils import setup_logging, log_audit_entry, ensure_directory_exists
from .csv_tasks import CSVTasks
from .json_tasks import JSONTasks
from .conversion_tasks import ConversionTasks

logger = setup_logging(__name__)

class DataAgent:
    def __init__(self, config):
        self.config = config
        self.audit_log = []
        self.data_store = {}
        self.start_time = datetime.datetime.now()
        self.csv_tasks = CSVTasks()
        self.json_tasks = JSONTasks()
        self.conversion_tasks = ConversionTasks()

    def _process_task(self, task):
        task_type = task.get("type")
        task_name = task.get("name", task_type)
        input_data_key = task.get("input_data_key")
        output_data_key = task.get("output_data_key")

        current_data = self.data_store.get(input_data_key) if input_data_key else None
        log_audit_entry(self.audit_log, "INFO", f"Starting task '{task_name}'", task_type)

        try:
            task_output_data = None
            success = False

            if task_type == "load_csv":
                task_output_data = self.csv_tasks.load_csv(task.get("file_path"))
                success = task_output_data is not None
            elif task_type == "save_csv":
                success = self.csv_tasks.save_csv(current_data, task.get("file_path"), task.get("fieldnames"))
            elif task_type == "transform_csv_aggregate":
                task_output_data = self.csv_tasks.transform_csv_aggregate(
                    current_data, task.get("group_by_field"), task.get("aggregate_field"), task.get("aggregate_type", "sum")
                )
                success = task_output_data is not None
            elif task_type == "load_json":
                task_output_data = self.json_tasks.load_json(task.get("file_path"))
                success = task_output_data is not None
            elif task_type == "save_json":
                success = self.json_tasks.save_json(current_data, task.get("file_path"), task.get("indent", 2))
            elif task_type == "update_json_data":
                task_output_data = self.json_tasks.update_json_data(current_data, task.get("updates"))
                success = task_output_data is not None
            elif task_type == "query_json_data":
                task_output_data = self.json_tasks.query_json_data(current_data, task.get("path"))
                success = True
            elif task_type == "csv_to_json_conversion":
                task_output_data = self.conversion_tasks.csv_to_json(current_data)
                success = task_output_data is not None

            if success and output_data_key and task_output_data is not None:
                self.data_store[output_data_key] = task_output_data
                log_audit_entry(self.audit_log, "SUCCESS", f"Task '{task_name}' finished.", task_type)
        except Exception as e:
            log_audit_entry(self.audit_log, "ERROR", f"Task '{task_name}' failed: {e}", task_type)

    def _generate_audit_report(self, output_dir):
        ensure_directory_exists(output_dir)
        report_filename = f"audit_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(output_dir, report_filename)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.audit_log, f, indent=4, ensure_ascii=False)

    def run(self):
        for task in self.config.get("tasks", []):
            self._process_task(task)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._generate_audit_report(os.path.join(project_root, 'reports'))