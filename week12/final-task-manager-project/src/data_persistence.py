"""
Data persistence layer for Enhanced Task Manager.
Handles loading and atomic saving of tasks to/from a JSON file with corrupted file preservation.
"""

import json
import os
import shutil
import tempfile
import logging
from typing import List, Dict, Any, Union

from .task import Task, DueDateTask, PriorityTask

logger = logging.getLogger(__name__)


class DataPersistence:
    """
    Handles loading and saving of tasks to/from a JSON file.
    Centralizes all file I/O and serialization/deserialization logic.
    """

    def __init__(self, data_file: str = "data/tasks.json"):
        """
        Initialize DataPersistence with relative or absolute data file path.
        Resolves paths safely relative to the project directory root.
        """
        self.data_file = data_file
        if os.path.isabs(data_file):
            self._data_file_path = data_file
        else:
            # Resolves relative to project root (parent of 'src')
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self._data_file_path = os.path.normpath(os.path.join(project_root, data_file))

    @property
    def data_file_path(self) -> str:
        """Returns the absolute resolved path to the data file."""
        return self._data_file_path

    def load_tasks(self) -> List[Union[Task, DueDateTask, PriorityTask]]:
        """
        Loads tasks from the JSON file, reconstructing polymorphic Task objects.
        Handles missing files, backward compatibility (missing tags), and malformed data.

        Returns:
            List of Task, DueDateTask, or PriorityTask objects.
        """
        if not os.path.exists(self._data_file_path):
            dir_name = os.path.dirname(self._data_file_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            return []

        # Check if file is completely empty (0 bytes)
        if os.path.getsize(self._data_file_path) == 0:
            logger.warning("tasks.json is empty. Starting with an empty task list.")
            return []

        try:
            with open(self._data_file_path, "r", encoding="utf-8") as f:
                raw_tasks = json.load(f)

            if not isinstance(raw_tasks, list):
                logger.error("Invalid JSON structure: top-level element is not a list.")
                self._backup_corrupted_file()
                return []

            loaded_tasks: List[Union[Task, DueDateTask, PriorityTask]] = []
            for t_dict in raw_tasks:
                if not isinstance(t_dict, dict):
                    logger.warning("Skipping non-dict task entry: %s", t_dict)
                    continue

                task_type = t_dict.pop("_type", "Task")
                # Backward compatibility: ensure 'tags' key is present
                t_dict.setdefault("tags", [])

                try:
                    if task_type == "Task":
                        loaded_tasks.append(Task(**t_dict))
                    elif task_type == "DueDateTask":
                        loaded_tasks.append(DueDateTask(**t_dict))
                    elif task_type == "PriorityTask":
                        loaded_tasks.append(PriorityTask(**t_dict))
                    else:
                        logger.warning(
                            "Unknown task type '%s' encountered. Skipping task ID %s.",
                            task_type,
                            t_dict.get("id", "N/A"),
                        )
                except (ValueError, TypeError) as item_err:
                    logger.warning(
                        "Skipping invalid task record (ID: %s): %s",
                        t_dict.get("id", "N/A"),
                        item_err,
                    )
            return loaded_tasks

        except json.JSONDecodeError as jde:
            logger.error("Warning: tasks.json is empty or corrupted: %s", jde)
            self._backup_corrupted_file()
            return []
        except FileNotFoundError:
            return []
        except Exception as e:
            logger.error("An unexpected error occurred during task loading: %s", e)
            return []

    def _backup_corrupted_file(self) -> None:
        """Backs up a corrupted data file to avoid accidental overwrite and data loss."""
        try:
            if os.path.exists(self._data_file_path):
                backup_path = f"{self._data_file_path}.corrupted.bak"
                shutil.copy2(self._data_file_path, backup_path)
                logger.info("Preserved corrupted data file as '%s'", backup_path)
        except Exception as e:
            logger.error("Failed to backup corrupted file: %s", e)

    def save_tasks(self, tasks: List[Union[Task, DueDateTask, PriorityTask]]) -> bool:
        """
        Saves a list of Task objects to the JSON file using atomic write.
        Uses the to_dict method of each Task object polymorphically.

        Returns:
            bool: True if saving succeeded, False otherwise.
        """
        tasks_as_dicts: List[Dict[str, Any]] = [task.to_dict() for task in tasks]
        dir_name = os.path.dirname(self._data_file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        # Atomic save strategy using a temp file in the same directory
        temp_fd = None
        temp_path = None
        try:
            temp_fd, temp_path = tempfile.mkstemp(
                dir=dir_name if dir_name else None,
                prefix="tasks_tmp_",
                suffix=".json",
            )
            with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                temp_fd = None  # fdopen transfers ownership
                json.dump(tasks_as_dicts, f, indent=4, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())

            # Atomic replace (Windows Python 3.3+ supports atomic os.replace)
            os.replace(temp_path, self._data_file_path)
            return True
        except Exception as e:
            logger.error("Failed to save tasks safely: %s", e)
            if temp_fd is not None:
                try:
                    os.close(temp_fd)
                except OSError:
                    pass
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            return False
