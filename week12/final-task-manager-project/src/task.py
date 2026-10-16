"""
Task data models for the Enhanced Task Manager application.
Defines base Task, DueDateTask, and PriorityTask with full tag support and validation.
"""

import datetime
from typing import List, Optional, Union, Dict, Any


class Task:
    """
    Base class for all tasks in the task manager.
    Includes an ID, description, completed status, and a 'tags' attribute for categorization.
    """

    def __init__(
        self,
        id: int,
        description: str,
        completed: bool = False,
        tags: Optional[List[str]] = None,
    ):
        """
        Initialize a base Task object.

        Raises:
            TypeError: If id is not an int or description is not a string.
            ValueError: If id is <= 0 or description is empty.
        """
        if not isinstance(id, int) or isinstance(id, bool):
            raise TypeError("Task ID must be an integer.")
        if id <= 0:
            raise ValueError("Task ID must be a positive integer.")

        if not isinstance(description, str):
            raise TypeError("Description must be a string.")
        stripped_desc = description.strip()
        if not stripped_desc:
            raise ValueError("Description cannot be empty.")

        self.id: int = id
        self.description: str = stripped_desc
        self.completed: bool = bool(completed)

        # Ensure tags is always a unique list of lowercase stripped strings
        self.tags: List[str] = []
        if tags is not None:
            if not isinstance(tags, (list, tuple, set)):
                raise TypeError("Tags must be a collection of strings.")
            for t in tags:
                self.add_tag(str(t))

    def mark_complete(self) -> None:
        """Marks the task as completed."""
        self.completed = True

    def add_tag(self, tag: str) -> None:
        """Adds a normalized tag to the task, preventing duplicates and empty tags."""
        if not isinstance(tag, str):
            tag = str(tag)
        normalized_tag = tag.strip().lower()
        if normalized_tag and normalized_tag not in self.tags:
            self.tags.append(normalized_tag)

    def remove_tag(self, tag: str) -> None:
        """Removes a tag from the task if present."""
        if not isinstance(tag, str):
            tag = str(tag)
        normalized_tag = tag.strip().lower()
        if normalized_tag in self.tags:
            self.tags.remove(normalized_tag)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Task object to a dictionary for JSON serialization.
        Includes a '_type' field, tags list, and core attributes.
        """
        return {
            "id": self.id,
            "description": self.description,
            "completed": self.completed,
            "tags": list(self.tags),
            "_type": "Task",
        }

    def __str__(self) -> str:
        """Returns a human-readable string representation of the task."""
        status = "Completed" if self.completed else "Pending"
        tags_str = f" | Tags: {', '.join(self.tags)}" if self.tags else ""
        return f"ID: {self.id} | Description: {self.description} | Status: {status}{tags_str}"

    def __repr__(self) -> str:
        return (
            f"Task(id={self.id}, description='{self.description}', "
            f"completed={self.completed}, tags={self.tags})"
        )


class DueDateTask(Task):
    """
    A task with an additional due date, stored as a datetime.date object.
    Inherits from the base Task class.
    """

    def __init__(
        self,
        id: int,
        description: str,
        due_date: Union[str, datetime.date],
        completed: bool = False,
        tags: Optional[List[str]] = None,
    ):
        """
        Initialize a DueDateTask.

        Raises:
            TypeError: If due_date is not a str or datetime.date.
            ValueError: If due_date string is not in valid YYYY-MM-DD format.
        """
        super().__init__(id, description, completed, tags)

        if isinstance(due_date, datetime.date) and not isinstance(due_date, datetime.datetime):
            self.due_date: datetime.date = due_date
        elif isinstance(due_date, datetime.datetime):
            self.due_date = due_date.date()
        elif isinstance(due_date, str):
            try:
                self.due_date = datetime.datetime.strptime(due_date.strip(), "%Y-%m-%d").date()
            except ValueError as e:
                raise ValueError(f"Invalid date format or value '{due_date}'. Expected YYYY-MM-DD.") from e
        else:
            raise TypeError("due_date must be a string in YYYY-MM-DD format or a datetime.date object")

    def to_dict(self) -> Dict[str, Any]:
        """Overrides to_dict to include due_date (formatted as string) and its own type identifier."""
        base_dict = super().to_dict()
        base_dict["due_date"] = self.due_date.strftime("%Y-%m-%d")
        base_dict["_type"] = "DueDateTask"
        return base_dict

    def __str__(self) -> str:
        """Overrides __str__ to include the due date formatted consistently."""
        base_str = super().__str__()
        formatted_due = self.due_date.strftime("%Y-%m-%d")
        if " | Tags:" in base_str:
            base_str_without_tags, tags_part = base_str.split(" | Tags:", 1)
            return f"{base_str_without_tags} | Due: {formatted_due} | Tags:{tags_part}"
        return f"{base_str} | Due: {formatted_due}"

    def __repr__(self) -> str:
        return (
            f"DueDateTask(id={self.id}, description='{self.description}', "
            f"due_date='{self.due_date.strftime('%Y-%m-%d')}', completed={self.completed}, tags={self.tags})"
        )


class PriorityTask(Task):
    """
    A task with an additional priority level (High, Medium, Low).
    Inherits from the base Task class.
    """

    ALLOWED_PRIORITIES = ["High", "Medium", "Low"]

    def __init__(
        self,
        id: int,
        description: str,
        priority: str,
        completed: bool = False,
        tags: Optional[List[str]] = None,
    ):
        """
        Initialize a PriorityTask.

        Raises:
            TypeError: If priority is not a string.
            ValueError: If priority is not one of High, Medium, Low.
        """
        super().__init__(id, description, completed, tags)

        if not isinstance(priority, str):
            raise TypeError("Priority must be a string.")

        normalized_priority = priority.strip().capitalize()
        if normalized_priority not in self.ALLOWED_PRIORITIES:
            raise ValueError(f"Priority must be one of {self.ALLOWED_PRIORITIES}")

        self.priority: str = normalized_priority

    def to_dict(self) -> Dict[str, Any]:
        """Overrides to_dict to include priority and its own type identifier."""
        base_dict = super().to_dict()
        base_dict["priority"] = self.priority
        base_dict["_type"] = "PriorityTask"
        return base_dict

    def __str__(self) -> str:
        """Overrides __str__ to include the priority level."""
        base_str = super().__str__()
        if " | Tags:" in base_str:
            base_str_without_tags, tags_part = base_str.split(" | Tags:", 1)
            return f"{base_str_without_tags} | Priority: {self.priority} | Tags:{tags_part}"
        return f"{base_str} | Priority: {self.priority}"

    def __repr__(self) -> str:
        return (
            f"PriorityTask(id={self.id}, description='{self.description}', "
            f"priority='{self.priority}', completed={self.completed}, tags={self.tags})"
        )
