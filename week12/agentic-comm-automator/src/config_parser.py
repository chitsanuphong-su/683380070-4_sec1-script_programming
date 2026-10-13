import json
import os
from .utils import setup_logging

logger = setup_logging(__name__)

class ConfigParser:
    """
    Parses and validates the communication automation configuration from a JSON file.
    Supports send_email, send_sms, and process_inbox task types.
    """

    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {}

    def load_config(self):
        """Loads and validates configuration from the specified JSON file."""
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
        if not isinstance(self.config, dict):
            raise ValueError("Root configuration must be a JSON object.")

        required_top_level_fields = ["tasks"]
        for field in required_top_level_fields:
            if field not in self.config:
                raise ValueError(f"Missing required field in config: '{field}'")

        if not isinstance(self.config["tasks"], list):
            raise ValueError("Config field 'tasks' must be a list.")

        allowed_task_types = {"send_email", "send_sms", "process_inbox"}

        for i, task in enumerate(self.config["tasks"]):
            if not isinstance(task, dict):
                raise ValueError(f"Task {i} must be a dictionary.")

            if "type" not in task:
                raise ValueError(f"Task {i} is missing 'type' field.")
            if "name" not in task:
                raise ValueError(f"Task {i} (type: {task['type']}) is missing 'name' field.")

            task_type = task["type"]
            if task_type not in allowed_task_types:
                raise ValueError(f"Task {i} has unsupported task type: '{task_type}'.")

            if "parameters" not in task or not isinstance(task["parameters"], dict):
                raise ValueError(f"Task {i} ({task_type}) requires a 'parameters' object.")

            params = task["parameters"]

            # Validate send_email
            if task_type == "send_email":
                if "recipients" not in params or not isinstance(params["recipients"], dict):
                    raise ValueError(f"Task {i} (send_email) requires 'recipients' dictionary in parameters.")

                recipients = params["recipients"]
                if "to" not in recipients or not isinstance(recipients["to"], list) or len(recipients["to"]) == 0:
                    raise ValueError(f"Task {i} (send_email) 'recipients.to' must be a non-empty list.")

                if "cc" in recipients and not isinstance(recipients["cc"], list):
                    raise ValueError(f"Task {i} (send_email) 'recipients.cc' must be a list.")

                if "bcc" in recipients and not isinstance(recipients["bcc"], list):
                    raise ValueError(f"Task {i} (send_email) 'recipients.bcc' must be a list.")

                for req_tmpl in ["subject_template", "body_template"]:
                    if req_tmpl not in params or not isinstance(params[req_tmpl], str):
                        raise ValueError(f"Task {i} (send_email) requires '{req_tmpl}' string in parameters.")

                if "attachments" in params and not isinstance(params["attachments"], list):
                    raise ValueError(f"Task {i} (send_email) 'attachments' must be a list.")

            # Validate send_sms
            elif task_type == "send_sms":
                if "phone_numbers" not in params or not isinstance(params["phone_numbers"], list) or len(params["phone_numbers"]) == 0:
                    raise ValueError(f"Task {i} (send_sms) requires a non-empty 'phone_numbers' list.")

                if "message_template" not in params or not isinstance(params["message_template"], str) or not params["message_template"].strip():
                    raise ValueError(f"Task {i} (send_sms) requires a non-empty 'message_template' string.")

            # Validate process_inbox
            elif task_type == "process_inbox":
                if "search_criteria" not in params or not isinstance(params["search_criteria"], dict):
                    raise ValueError(f"Task {i} (process_inbox) requires 'search_criteria' dictionary in parameters.")

                if "rules" in params:
                    if not isinstance(params["rules"], list):
                        raise ValueError(f"Task {i} (process_inbox) 'rules' must be a list.")
                    for r_idx, rule in enumerate(params["rules"]):
                        if not isinstance(rule, dict) or "if" not in rule or "then" not in rule:
                            raise ValueError(f"Task {i} rule {r_idx} must contain 'if' and 'then' blocks.")
                        if not isinstance(rule["if"], dict) or not isinstance(rule["then"], dict):
                            raise ValueError(f"Task {i} rule {r_idx} 'if' and 'then' must be dictionaries.")

            if "output_context_key" in task:
                if not isinstance(task["output_context_key"], str) or not task["output_context_key"].strip():
                    raise ValueError(f"Task {i} 'output_context_key' must be a non-empty string.")

        logger.info("Configuration validated successfully.")
