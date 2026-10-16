"""
Task Manager business logic layer for Enhanced Task Manager.
Handles core CRUD, advanced keyword search, multi-criteria filtering, and flexible sorting.
"""

import datetime
import logging
from typing import List, Optional, Tuple, Union, Dict, Any

from .task import Task, DueDateTask, PriorityTask
from .data_persistence import DataPersistence

logger = logging.getLogger(__name__)


class TaskManager:
    """
    Manages the collection of various Task objects.
    Focuses on business logic: add, list, complete, delete, search, filter, sort.
    """

    PRIORITY_MAP: Dict[str, int] = {"High": 1, "Medium": 2, "Low": 3}
    REVERSE_PRIORITY_MAP: Dict[int, str] = {1: "High", 2: "Medium", 3: "Low"}

    def __init__(self, data_file: str = "data/tasks.json"):
        """Initialize TaskManager and load initial tasks from persistence."""
        self.persistence = DataPersistence(data_file)
        self.tasks: List[Union[Task, DueDateTask, PriorityTask]] = self.persistence.load_tasks()
        self.next_id: int = self._get_next_task_id()

    def _get_next_task_id(self) -> int:
        """Generates the next unique ID for a new task."""
        if not self.tasks:
            return 1
        return max(task.id for task in self.tasks) + 1

    def _save_changes(self) -> bool:
        """Internal helper to save tasks via the persistence layer."""
        return self.persistence.save_tasks(self.tasks)

    # --- Basic CRUD Operations ---

    def add_normal_task(
        self, description: str, tags: Optional[List[str]] = None
    ) -> Optional[Task]:
        """
        Creates, adds and persists a standard Task.

        Returns:
            Created Task instance, or None if validation fails.
        """
        try:
            new_task = Task(self.next_id, description, tags=tags)
            self.tasks.append(new_task)
            self.next_id += 1
            self._save_changes()
            return new_task
        except (ValueError, TypeError) as e:
            logger.error("Failed to add normal task: %s", e)
            return None

    def add_due_date_task(
        self,
        description: str,
        due_date_str: Union[str, datetime.date],
        tags: Optional[List[str]] = None,
    ) -> Optional[DueDateTask]:
        """
        Creates, adds and persists a DueDateTask.

        Returns:
            Created DueDateTask instance, or None if validation fails.
        """
        try:
            new_task = DueDateTask(self.next_id, description, due_date_str, tags=tags)
            self.tasks.append(new_task)
            self.next_id += 1
            self._save_changes()
            return new_task
        except (ValueError, TypeError) as e:
            logger.error("Failed to add due date task: %s", e)
            return None

    def add_priority_task(
        self,
        description: str,
        priority: str,
        tags: Optional[List[str]] = None,
    ) -> Optional[PriorityTask]:
        """
        Creates, adds and persists a PriorityTask.

        Returns:
            Created PriorityTask instance, or None if validation fails.
        """
        try:
            new_task = PriorityTask(self.next_id, description, priority, tags=tags)
            self.tasks.append(new_task)
            self.next_id += 1
            self._save_changes()
            return new_task
        except (ValueError, TypeError) as e:
            logger.error("Failed to add priority task: %s", e)
            return None

    def get_task_by_id(
        self, task_id: int
    ) -> Optional[Union[Task, DueDateTask, PriorityTask]]:
        """Helper to find a task by ID."""
        return next((task for task in self.tasks if task.id == task_id), None)

    def complete_task(self, task_id: int) -> Tuple[bool, str]:
        """
        Marks an existing task as completed.

        Returns:
            Tuple of (success_boolean, message).
        """
        task = self.get_task_by_id(task_id)
        if task:
            if not task.completed:
                task.mark_complete()
                self._save_changes()
                return True, "Task marked as completed."
            return False, "Task is already completed."
        return False, "Task not found."

    def delete_task(self, task_id: int) -> Tuple[bool, str]:
        """
        Removes a task by ID and persists changes.

        Returns:
            Tuple of (success_boolean, message).
        """
        original_len = len(self.tasks)
        self.tasks = [task for task in self.tasks if task.id != task_id]
        if len(self.tasks) < original_len:
            self._save_changes()
            return True, "Task deleted successfully."
        return False, "Task not found."

    def get_all_tasks(self) -> List[Union[Task, DueDateTask, PriorityTask]]:
        """Returns a copy of all tasks for listing."""
        return list(self.tasks)

    # --- Search Logic ---

    def search_tasks(
        self, keyword: str
    ) -> List[Union[Task, DueDateTask, PriorityTask]]:
        """
        Searches tasks by keyword across description and tags (case-insensitive partial match).
        Eliminates duplicate task returns.
        """
        if not keyword or not keyword.strip():
            return []

        keyword_lower = keyword.strip().lower()
        found_tasks: List[Union[Task, DueDateTask, PriorityTask]] = []
        for task in self.tasks:
            # Search in description
            if keyword_lower in task.description.lower():
                found_tasks.append(task)
                continue  # Avoid duplicate insertion
            # Search in tags
            if any(keyword_lower in tag for tag in task.tags):
                found_tasks.append(task)
        return found_tasks

    # --- Filter Logic ---

    def filter_tasks(
        self,
        status: Optional[bool] = None,
        due_date_before: Optional[Union[datetime.date, str]] = None,
        due_date_after: Optional[Union[datetime.date, str]] = None,
        priority_level: Optional[str] = None,
        contains_tags: Optional[List[str]] = None,
    ) -> List[Union[Task, DueDateTask, PriorityTask]]:
        """
        Filters tasks by combining multiple criteria with AND logic.

        Args:
            status: bool, True for completed, False for pending, None for all.
            due_date_before: datetime.date or YYYY-MM-DD str. Tasks due on or before.
            due_date_after: datetime.date or YYYY-MM-DD str. Tasks due on or after.
            priority_level: "High", "Medium", "Low".
            contains_tags: List of tags. Task must contain ALL specified tags.
        """
        filtered_tasks = list(self.tasks)

        # Parse date parameters if passed as strings
        date_before: Optional[datetime.date] = None
        if due_date_before:
            if isinstance(due_date_before, str):
                date_before = datetime.datetime.strptime(due_date_before.strip(), "%Y-%m-%d").date()
            elif isinstance(due_date_before, datetime.date):
                date_before = due_date_before

        date_after: Optional[datetime.date] = None
        if due_date_after:
            if isinstance(due_date_after, str):
                date_after = datetime.datetime.strptime(due_date_after.strip(), "%Y-%m-%d").date()
            elif isinstance(due_date_after, datetime.date):
                date_after = due_date_after

        # 1. Filter by completion status
        if status is not None:
            filtered_tasks = [t for t in filtered_tasks if t.completed == bool(status)]

        # 2. Filter by due date before (inclusive, DueDateTask only)
        if date_before is not None:
            filtered_tasks = [
                t for t in filtered_tasks
                if isinstance(t, DueDateTask) and t.due_date <= date_before
            ]

        # 3. Filter by due date after (inclusive, DueDateTask only)
        if date_after is not None:
            filtered_tasks = [
                t for t in filtered_tasks
                if isinstance(t, DueDateTask) and t.due_date >= date_after
            ]

        # 4. Filter by priority level (PriorityTask only)
        if priority_level:
            norm_priority = priority_level.strip().capitalize()
            filtered_tasks = [
                t for t in filtered_tasks
                if isinstance(t, PriorityTask) and t.priority == norm_priority
            ]

        # 5. Filter by tags (task must contain ALL specified tags, case-insensitive)
        if contains_tags:
            clean_tags = [str(tag).strip().lower() for tag in contains_tags if str(tag).strip()]
            if clean_tags:
                filtered_tasks = [
                    t for t in filtered_tasks
                    if all(req_tag in [t_tag.lower() for t_tag in t.tags] for req_tag in clean_tags)
                ]

        return filtered_tasks

    # --- Sort Logic ---

    def sort_tasks(
        self, criterion: str = "id", reverse: bool = False
    ) -> List[Union[Task, DueDateTask, PriorityTask]]:
        """
        Sorts tasks by a given criterion.
        Supported criteria: 'id', 'description', 'completed', 'due_date', 'priority'.

        Polymorphic handling:
        - Tasks without due dates are grouped consistently at the end (or beginning if reverse).
        - Tasks without priority are grouped consistently at the end (or beginning if reverse).
        - Secondary sorting key is task.id for stable deterministic ordering.
        """
        tasks_to_sort = list(self.tasks)
        norm_criterion = str(criterion).strip().lower()

        if norm_criterion == "id":
            tasks_to_sort.sort(key=lambda t: t.id, reverse=reverse)
        elif norm_criterion == "description":
            tasks_to_sort.sort(key=lambda t: (t.description.lower(), t.id), reverse=reverse)
        elif norm_criterion == "completed":
            # False (Pending) before True (Completed)
            tasks_to_sort.sort(key=lambda t: (t.completed, t.id), reverse=reverse)
        elif norm_criterion == "due_date":
            # For DueDateTask, sort by date. Other tasks are placed at the end.
            if not reverse:
                tasks_to_sort.sort(
                    key=lambda t: (0 if isinstance(t, DueDateTask) else 1,
                                   t.due_date if isinstance(t, DueDateTask) else datetime.date.max,
                                   t.id)
                )
            else:
                tasks_to_sort.sort(
                    key=lambda t: (1 if isinstance(t, DueDateTask) else 0,
                                   t.due_date if isinstance(t, DueDateTask) else datetime.date.min,
                                   t.id),
                    reverse=True
                )
        elif norm_criterion == "priority":
            # Sort PriorityTasks by mapped numerical priority (High: 1, Medium: 2, Low: 3)
            # Other tasks are placed at the end.
            if not reverse:
                tasks_to_sort.sort(
                    key=lambda t: (0 if isinstance(t, PriorityTask) else 1,
                                   self.PRIORITY_MAP.get(t.priority, 99) if isinstance(t, PriorityTask) else 99,
                                   t.id)
                )
            else:
                tasks_to_sort.sort(
                    key=lambda t: (1 if isinstance(t, PriorityTask) else 0,
                                   self.PRIORITY_MAP.get(t.priority, 0) if isinstance(t, PriorityTask) else 0,
                                   t.id),
                    reverse=True
                )
        else:
            # Fallback to ID sorting
            tasks_to_sort.sort(key=lambda t: t.id, reverse=reverse)

        return tasks_to_sort
