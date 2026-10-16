"""
Unit tests for Task, DueDateTask, and PriorityTask models in src/task.py.
"""

import datetime
import pytest

from src.task import Task, DueDateTask, PriorityTask


class TestTask:
    def test_task_creation_valid(self):
        t = Task(1, "Complete assignment")
        assert t.id == 1
        assert t.description == "Complete assignment"
        assert t.completed is False
        assert t.tags == []

    def test_task_validation_invalid_id(self):
        with pytest.raises(ValueError):
            Task(-1, "Valid description")
        with pytest.raises(ValueError):
            Task(0, "Valid description")
        with pytest.raises(TypeError):
            Task("1", "Valid description")  # type: ignore
        with pytest.raises(TypeError):
            Task(True, "Valid description")  # bool is subclass of int

    def test_task_validation_invalid_description(self):
        with pytest.raises(ValueError):
            Task(1, "")
        with pytest.raises(ValueError):
            Task(1, "   ")
        with pytest.raises(TypeError):
            Task(1, None)  # type: ignore

    def test_mark_complete(self):
        t = Task(1, "Read documentation")
        assert t.completed is False
        t.mark_complete()
        assert t.completed is True

    def test_tags_initialization_and_normalization(self):
        t = Task(1, "Clean room", tags=[" Chores ", "HOME", "chores", "URGENT"])
        assert t.tags == ["chores", "home", "urgent"]

    def test_add_tag(self):
        t = Task(1, "Coding")
        t.add_tag(" Python ")
        t.add_tag("python")  # Duplicate
        t.add_tag("")  # Empty
        t.add_tag("   ")  # Whitespace only
        assert t.tags == ["python"]

    def test_remove_tag(self):
        t = Task(1, "Coding", tags=["python", "scripting"])
        t.remove_tag(" PYTHON ")
        assert t.tags == ["scripting"]
        t.remove_tag("nonexistent")
        assert t.tags == ["scripting"]

    def test_to_dict_and_str(self):
        t = Task(1, "Study", completed=True, tags=["study", "exam"])
        d = t.to_dict()
        assert d == {
            "id": 1,
            "description": "Study",
            "completed": True,
            "tags": ["study", "exam"],
            "_type": "Task",
        }
        s = str(t)
        assert "ID: 1" in s
        assert "Description: Study" in s
        assert "Status: Completed" in s
        assert "Tags: study, exam" in s


class TestDueDateTask:
    def test_due_date_task_creation_with_str(self):
        t = DueDateTask(2, "Submit project", "2026-12-31", tags=["school"])
        assert t.id == 2
        assert t.description == "Submit project"
        assert t.due_date == datetime.date(2026, 12, 31)
        assert t.tags == ["school"]

    def test_due_date_task_creation_with_date_object(self):
        target_date = datetime.date(2026, 11, 15)
        t = DueDateTask(3, "Meeting", target_date)
        assert t.due_date == target_date

    def test_due_date_invalid_format(self):
        with pytest.raises(ValueError):
            DueDateTask(1, "Bad date", "2026-02-30")  # Invalid date in calendar
        with pytest.raises(ValueError):
            DueDateTask(1, "Bad format", "31-12-2026")
        with pytest.raises(TypeError):
            DueDateTask(1, "Bad type", 12345)  # type: ignore

    def test_to_dict_and_str(self):
        t = DueDateTask(4, "Lab report", "2026-10-25", tags=["lab"])
        d = t.to_dict()
        assert d["_type"] == "DueDateTask"
        assert d["due_date"] == "2026-10-25"
        assert d["tags"] == ["lab"]
        s = str(t)
        assert "Due: 2026-10-25" in s
        assert "Tags: lab" in s


class TestPriorityTask:
    def test_priority_task_creation_valid(self):
        t1 = PriorityTask(5, "Fix bug", "High", tags=["bug"])
        t2 = PriorityTask(6, "Update docs", "medium")
        t3 = PriorityTask(7, "Refactor", " LOW ")
        assert t1.priority == "High"
        assert t2.priority == "Medium"
        assert t3.priority == "Low"

    def test_priority_task_invalid(self):
        with pytest.raises(ValueError):
            PriorityTask(1, "Invalid priority", "Urgent")
        with pytest.raises(TypeError):
            PriorityTask(1, "Invalid type", 100)  # type: ignore

    def test_to_dict_and_str(self):
        t = PriorityTask(8, "Security patch", "High", tags=["security"])
        d = t.to_dict()
        assert d["_type"] == "PriorityTask"
        assert d["priority"] == "High"
        s = str(t)
        assert "Priority: High" in s
        assert "Tags: security" in s
