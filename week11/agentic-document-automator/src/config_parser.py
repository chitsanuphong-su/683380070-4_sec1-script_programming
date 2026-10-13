# agentic-document-automator/src/config_parser.py
import json
import os
try:
    from .utils import setup_logging
except ImportError:
    from utils import setup_logging

logger = setup_logging(__name__)


class ConfigParser:
    """
    Parses and validates the document automation configuration from a JSON file.
    """

    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {}

    def load_config(self):
        """Loads the configuration from the specified JSON file."""
        if not os.path.exists(self.config_path):
            logger.critical(f"Configuration file not found: {self.config_path}")
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            self._validate_config()
            logger.info(f"Configuration loaded successfully from {self.config_path}")
            return self.config
        except json.JSONDecodeError as e:
            logger.critical(f"Invalid JSON format in config file: {e}")
            raise ValueError(f"Invalid JSON format in config file: {e}")
        except Exception as e:
            logger.critical(f"An error occurred while loading config: {e}")
            raise

    def _validate_config(self):
        """
        Validates the loaded configuration to ensure required fields and task structures are present.
        """
        required_top_level_fields = ["global_data", "tasks"]
        for field in required_top_level_fields:
            if field not in self.config:
                raise ValueError(f"Missing required field in config: '{field}'")

        if not isinstance(self.config["global_data"], dict):
            raise ValueError("Config field 'global_data' must be a dictionary.")

        if not isinstance(self.config["tasks"], list):
            raise ValueError("Config field 'tasks' must be a list.")

        valid_task_types = {
            "generate_word_report",
            "apply_pdf_watermark",
            "merge_pdfs",
            "extract_word_text",
            "extract_pdf_text"
        }

        # Basic validation for each task
        for i, task in enumerate(self.config["tasks"]):
            if not isinstance(task, dict):
                raise ValueError(f"Task {i} must be a dictionary.")

            if "type" not in task:
                raise ValueError(f"Task {i} is missing 'type' field.")

            task_type = task["type"]
            if task_type not in valid_task_types:
                logger.warning(f"Task {i} specifies unsupported or custom task type: '{task_type}'")

            # Specific validations per task type
            if task_type == "generate_word_report":
                if not task.get("template_path") or not task.get("output_path"):
                    raise ValueError(f"Task {i} (generate_word_report) requires 'template_path' and 'output_path'.")
            elif task_type == "apply_pdf_watermark":
                if not task.get("input_pdf") or not task.get("output_pdf") or not task.get("watermark_text"):
                    raise ValueError(f"Task {i} (apply_pdf_watermark) requires 'input_pdf', 'output_pdf', and 'watermark_text'.")
            elif task_type == "merge_pdfs":
                if not task.get("input_pdfs") or not task.get("output_pdf"):
                    raise ValueError(f"Task {i} (merge_pdfs) requires 'input_pdfs' and 'output_pdf'.")
                if not isinstance(task["input_pdfs"], list) or len(task["input_pdfs"]) == 0:
                    raise ValueError(f"Task {i} (merge_pdfs) 'input_pdfs' must be a non-empty list.")
            elif task_type == "extract_word_text":
                if not task.get("input_docx") or not task.get("output_text_file"):
                    raise ValueError(f"Task {i} (extract_word_text) requires 'input_docx' and 'output_text_file'.")
            elif task_type == "extract_pdf_text":
                if not task.get("input_pdf") or not task.get("output_text_file"):
                    raise ValueError(f"Task {i} (extract_pdf_text) requires 'input_pdf' and 'output_text_file'.")

        logger.info("Configuration validated.")
