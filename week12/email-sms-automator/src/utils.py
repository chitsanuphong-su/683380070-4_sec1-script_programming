import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env from the project root directory
_CURRENT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CURRENT_DIR.parent
_ENV_FILE_PATH = _PROJECT_ROOT / ".env"

if _ENV_FILE_PATH.exists():
    load_dotenv(dotenv_path=_ENV_FILE_PATH)
else:
    load_dotenv()


def setup_logging(name: str, level=logging.INFO) -> logging.Logger:
    """Sets up a logger for specific modules without duplicate handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger


def get_env_variable(var_name: str) -> str:
    """
    Retrieves an environment variable, raising a ValueError if not found or empty.
    Avoids exposing secret values in logs/exceptions.
    """
    value = os.getenv(var_name)
    if value is None or not value.strip():
        raise ValueError(
            f"Environment variable '{var_name}' not set or empty. "
            f"Please check your .env file or environment settings."
        )
    return value.strip()


def ensure_directory_exists(path: str) -> str:
    """Ensures that a directory exists, creating it if necessary."""
    try:
        os.makedirs(path, exist_ok=True)
        return path
    except OSError as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating directory {path}: {e}")
        raise
