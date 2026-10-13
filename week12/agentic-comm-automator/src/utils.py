import logging
import os
import json
import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the project's own .env file if present
load_dotenv()

def setup_logging(name, level=logging.INFO):
    """Sets up a logger for specific modules with clean formatting and no duplicate handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

def get_env_variable(var_name, default=None):
    """
    Retrieves an environment variable, raising a ValueError if not found and no default is provided.
    Does not expose sensitive credentials in error messages.
    """
    value = os.getenv(var_name, default)
    if value is None:
        raise ValueError(
            f"Environment variable '{var_name}' not set. Please check your .env file or environment settings."
        )
    return value

def ensure_directory_exists(path):
    """Ensures that a directory exists, creating it if necessary."""
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating directory {path}: {e}")
        raise

def log_audit_entry(audit_log_list, status, message, task_type="N/A", details=None):
    """
    Adds a sanitized, structured entry to the audit log list and logs to console.
    Ensures credentials or sensitive payload details are not leaked.
    """
    # Sanitize details to prevent accidental credential or sensitive leaks
    sanitized_details = {}
    if details:
        if isinstance(details, dict):
            for k, v in details.items():
                if any(sec in k.lower() for sec in ["password", "token", "secret", "auth"]):
                    sanitized_details[k] = "******"
                else:
                    sanitized_details[k] = v
        else:
            sanitized_details = {"info": str(details)}

    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "status": status,
        "task_type": task_type,
        "message": message,
        "details": sanitized_details
    }
    audit_log_list.append(log_entry)

    logger = logging.getLogger("CommunicationAudit")
    if status in ("ERROR", "CRITICAL"):
        logger.error(f"AUDIT LOG - {status}: {message} | Task: {task_type}")
    elif status == "WARNING":
        logger.warning(f"AUDIT LOG - {status}: {message} | Task: {task_type}")
    else:
        logger.info(f"AUDIT LOG - {status}: {message} | Task: {task_type}")
