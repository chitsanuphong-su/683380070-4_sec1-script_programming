# enhanced-task-manager-design/src/data_persistence.py
import json
import os
import datetime  # Needed for DueDateTask reconstruction

try:
    from .task import Task, DueDateTask, PriorityTask
except ImportError:
    from task import Task, DueDateTask, PriorityTask


class DataPersistence:
    """
    Handles loading and saving of tasks to/from a JSON file.
    Centralizes all file I/O and serialization/deserialization logic.
    """

    def __init__(self, data_file='data/tasks.json'):
        self.data_file = data_file
        # Adjust path for common project structure
        self._data_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..', self.data_file
        )

    def load_tasks(self):
        """
        Loads tasks from the JSON file, reconstructing Task objects.
        Handles different task types based on the '_type' field.
        """
        if not os.path.exists(self._data_file_path):
            os.makedirs(os.path.dirname(self._data_file_path), exist_ok=True)
            return []

        try:
            with open(self._data_file_path, 'r', encoding='utf-8') as f:
                raw_tasks = json.load(f)
            loaded_tasks = []
            for t_dict in raw_tasks:
                task_type = t_dict.pop('_type', 'Task')  # Default to 'Task'
                # Ensure 'tags' key is present, default to empty list if missing
                t_dict.setdefault('tags', [])

                if task_type == "Task":
                    loaded_tasks.append(Task(**t_dict))
                elif task_type == "DueDateTask":
                    loaded_tasks.append(DueDateTask(**t_dict))
                elif task_type == "PriorityTask":
                    loaded_tasks.append(PriorityTask(**t_dict))
                else:
                    print(f"Warning: Unknown task type '{task_type}' encountered. Skipping task ID {t_dict.get('id', 'N/A')}.")
            return loaded_tasks
        except json.JSONDecodeError:
            print("Warning: tasks.json is empty or corrupted. Starting with an empty task list.")
            return []
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"An unexpected error occurred during task loading: {e}. Starting with an empty list.")
            return []

    def save_tasks(self, tasks):
        """
        Saves a list of Task objects to the JSON file.
        Uses the to_dict method of each Task object (polymorphically).
        """
        tasks_as_dicts = [task.to_dict() for task in tasks]
        os.makedirs(os.path.dirname(self._data_file_path), exist_ok=True)
        with open(self._data_file_path, 'w', encoding='utf-8') as f:
            json.dump(tasks_as_dicts, f, indent=4)
