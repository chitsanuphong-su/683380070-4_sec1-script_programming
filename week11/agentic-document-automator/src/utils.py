# agentic-document-automator/src/utils.py
import logging
import os
import json
import datetime

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_logging(name, level=logging.INFO, filename=None):
    """Sets up a logger for specific modules, allowing file output."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Ensure handlers are added only once
    if not logger.handlers:
        # Console handler
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # File handler (optional)
        if filename:
            ensure_directory_exists(os.path.dirname(filename))
            fh = logging.FileHandler(filename, encoding='utf-8')
            fh.setFormatter(formatter)
            logger.addHandler(fh)

    return logger


def ensure_directory_exists(path):
    """Ensures that a directory exists, creating it if necessary."""
    if not path:
        return
    try:
        os.makedirs(path, exist_ok=True)
        logging.info(f"Directory ensured: {path}")
    except OSError as e:
        logging.error(f"Error creating directory {path}: {e}")
        raise


def log_audit_entry(audit_log_list, status, message, task_type="N/A", details=None):
    """Adds an entry to the audit log list."""
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "status": status,
        "task_type": task_type,
        "message": message,
        "details": details if details is not None else {}
    }
    audit_log_list.append(log_entry)
    if status in ("ERROR", "CRITICAL"):
        logging.error(f"AUDIT LOG - {status}: {message} | Task: {task_type} | Details: {details}")
    elif status == "WARNING":
        logging.warning(f"AUDIT LOG - {status}: {message} | Task: {task_type}")
    else:
        logging.info(f"AUDIT LOG - {status}: {message} | Task: {task_type}")
