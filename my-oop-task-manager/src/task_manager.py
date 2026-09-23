import json
import os
from typing import List
from src.task import Task

class TaskManager:
    """Manages the collection of Task objects and data persistence."""
    def __init__(self, data_file: str = None):
        if data_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            self.data_file = os.path.join(data_dir, "tasks.json")
        else:
            self.data_file = data_file
        
        self.tasks: List[Task] = []
        self.load_tasks()

    def _get_next_id(self) -> int:
        if not self.tasks:
            return 1
        return max(task.id for task in self.tasks) + 1

    def add_task(self, description: str):
        new_id = self._get_next_id()
        task = Task(new_id, description)
        self.tasks.append(task)
        self.save_tasks()
        print(f"Task '{description}' added with ID {new_id}.")

    def list_tasks(self):
        if not self.tasks:
            print("No tasks found.")
            return
        print("\n--- Your Tasks ---")
        for task in self.tasks:
            print(task)

    def complete_task(self, task_id: int):
        for task in self.tasks:
            if task.id == task_id:
                if not task.completed:
                    task.mark_complete()
                    self.save_tasks()
                    print(f"Task ID {task_id} marked as completed.")
                else:
                    print(f"Task ID {task_id} is already completed.")
                return
        print(f"Error: Task with ID {task_id} not found.")

    def delete_task(self, task_id: int):
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(i)
                self.save_tasks()
                print(f"Task ID {task_id} deleted successfully.")
                return
        print(f"Error: Task with ID {task_id} not found.")

    def save_tasks(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump([task.to_dict() for task in self.tasks], f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving tasks: {e}")

    def load_tasks(self):
        if not os.path.exists(self.data_file):
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.tasks = [Task(item.get("id", item.get("task_id")), item.get("description", ""), item.get("completed", False)) for item in data]
        except Exception as e:
            print(f"Error loading tasks: {e}")
