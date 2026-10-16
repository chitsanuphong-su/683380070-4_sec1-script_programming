"""
Unit tests for TaskManager business logic in src/task_manager.py.
"""

import datetime
import pytest

from src.task_manager import TaskManager
from src.task import Task, DueDateTask, PriorityTask


class TestTaskManager:
    @pytest.fixture
    def manager(self, tmp_path):
        json_file = str(tmp_path / "test_tasks.json")
        return TaskManager(data_file=json_file)

    def test_add_normal_task(self, manager):
        task = manager.add_normal_task("Read book", tags=["study", "reading"])
        assert task is not None
        assert task.id == 1
        assert task.description == "Read book"
        assert task.tags == ["study", "reading"]
        assert len(manager.get_all_tasks()) == 1

    def test_add_due_date_task(self, manager):
        task = manager.add_due_date_task("Submit homework", "2026-11-01", tags=["school"])
        assert isinstance(task, DueDateTask)
        assert task.id == 1
        assert task.due_date == datetime.date(2026, 11, 1)

    def test_add_due_date_task_invalid_date(self, manager):
        task = manager.add_due_date_task("Invalid date", "not-a-date")
        assert task is None
        assert len(manager.get_all_tasks()) == 0

    def test_add_priority_task(self, manager):
        task = manager.add_priority_task("Fix production issue", "High", tags=["work"])
        assert isinstance(task, PriorityTask)
        assert task.priority == "High"

    def test_add_priority_task_invalid_priority(self, manager):
        task = manager.add_priority_task("Bad priority", "Critical")
        assert task is None

    def test_unique_ids_and_persistence_restart(self, tmp_path):
        json_file = str(tmp_path / "restart_tasks.json")
        mgr1 = TaskManager(data_file=json_file)
        t1 = mgr1.add_normal_task("Task 1")
        t2 = mgr1.add_due_date_task("Task 2", "2026-12-01")
        assert t1.id == 1
        assert t2.id == 2

        # Restart TaskManager using same file
        mgr2 = TaskManager(data_file=json_file)
        assert mgr2.next_id == 3
        t3 = mgr2.add_priority_task("Task 3", "Low")
        assert t3.id == 3

    def test_complete_task(self, manager):
        task = manager.add_normal_task("Finish lab")
        success, msg = manager.complete_task(task.id)
        assert success is True
        assert "completed" in msg
        assert task.completed is True

        # Already completed
        success2, msg2 = manager.complete_task(task.id)
        assert success2 is False
        assert "already completed" in msg2

        # Nonexistent task
        success3, msg3 = manager.complete_task(999)
        assert success3 is False
        assert "not found" in msg3

    def test_delete_task(self, manager):
        t1 = manager.add_normal_task("Keep me")
        t2 = manager.add_normal_task("Delete me")

        success, msg = manager.delete_task(t2.id)
        assert success is True
        assert len(manager.get_all_tasks()) == 1
        assert manager.get_task_by_id(t2.id) is None

        # Delete nonexistent
        success2, msg2 = manager.delete_task(999)
        assert success2 is False

    def test_search_tasks(self, manager):
        t1 = manager.add_normal_task("Study Python Programming", tags=["python", "coding"])
        t2 = manager.add_due_date_task("Buy groceries", "2026-11-15", tags=["home", "food"])
        t3 = manager.add_priority_task("Python Web Project", "High", tags=["django", "web"])

        # Partial match in description
        res1 = manager.search_tasks("python")
        assert len(res1) == 2
        assert t1 in res1 and t3 in res1

        # Match in tags
        res2 = manager.search_tasks("coding")
        assert len(res2) == 1
        assert res2[0] == t1

        # Case-insensitive
        res3 = manager.search_tasks("GROCERIES")
        assert len(res3) == 1
        assert res3[0] == t2

        # Empty keyword
        assert manager.search_tasks("") == []
        assert manager.search_tasks("   ") == []

        # No match
        assert manager.search_tasks("nonexistent") == []

    def test_filter_tasks(self, manager):
        t1 = manager.add_normal_task("Task 1", tags=["work", "urgent"])
        t2 = manager.add_due_date_task("Task 2", "2026-05-01", tags=["work"])
        t3 = manager.add_due_date_task("Task 3", "2026-12-01", tags=["home"])
        t4 = manager.add_priority_task("Task 4", "High", tags=["urgent"])
        t5 = manager.add_priority_task("Task 5", "Low", tags=["personal"])

        manager.complete_task(t1.id)

        # 1. Filter by status
        completed = manager.filter_tasks(status=True)
        assert len(completed) == 1
        assert completed[0].id == t1.id

        pending = manager.filter_tasks(status=False)
        assert len(pending) == 4

        # 2. Filter by due_date_before
        before = manager.filter_tasks(due_date_before="2026-06-01")
        assert len(before) == 1
        assert before[0].id == t2.id

        # 3. Filter by due_date_after
        after = manager.filter_tasks(due_date_after=datetime.date(2026, 10, 1))
        assert len(after) == 1
        assert after[0].id == t3.id

        # 4. Filter by priority
        high = manager.filter_tasks(priority_level="High")
        assert len(high) == 1
        assert high[0].id == t4.id

        # 5. Filter by tags (ALL tags match)
        work_urgent = manager.filter_tasks(contains_tags=["work", "urgent"])
        assert len(work_urgent) == 1
        assert work_urgent[0].id == t1.id

        # 6. Combined filter: pending AND urgent
        combined = manager.filter_tasks(status=False, contains_tags=["urgent"])
        assert len(combined) == 1
        assert combined[0].id == t4.id

    def test_sort_tasks(self, manager):
        t1 = manager.add_due_date_task("Beta task", "2026-12-01")
        t2 = manager.add_priority_task("Alpha task", "High")
        t3 = manager.add_normal_task("Gamma task")
        t4 = manager.add_due_date_task("Delta task", "2026-03-01")
        t5 = manager.add_priority_task("Epsilon task", "Low")

        # Sort by ID
        s_id = manager.sort_tasks(criterion="id")
        assert [t.id for t in s_id] == [1, 2, 3, 4, 5]

        # Sort by description
        s_desc = manager.sort_tasks(criterion="description")
        assert [t.description for t in s_desc] == [
            "Alpha task", "Beta task", "Delta task", "Epsilon task", "Gamma task"
        ]

        # Sort by due_date: DueDateTasks sorted first (Delta: 2026-03-01, Beta: 2026-12-01), others after
        s_due = manager.sort_tasks(criterion="due_date")
        assert s_due[0].id == 4  # Delta
        assert s_due[1].id == 1  # Beta
        assert set(t.id for t in s_due[2:]) == {2, 3, 5}

        # Sort by priority: PriorityTasks sorted High(t2) -> Low(t5), others after
        s_prio = manager.sort_tasks(criterion="priority")
        assert s_prio[0].id == 2  # High
        assert s_prio[1].id == 5  # Low
        assert set(t.id for t in s_prio[2:]) == {1, 3, 4}
