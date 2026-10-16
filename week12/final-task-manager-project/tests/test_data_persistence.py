"""
Unit tests for DataPersistence in src/data_persistence.py.
"""

import json
import os
import pytest

from src.data_persistence import DataPersistence
from src.task import Task, DueDateTask, PriorityTask


class TestDataPersistence:
    def test_save_and_load_round_trip(self, tmp_path):
        json_file = str(tmp_path / "tasks.json")
        dp = DataPersistence(json_file)

        tasks = [
            Task(1, "Base task", completed=False, tags=["base", "test"]),
            DueDateTask(2, "Due task", "2026-11-20", completed=True, tags=["due"]),
            PriorityTask(3, "Priority task", "High", completed=False, tags=["high"]),
        ]

        save_res = dp.save_tasks(tasks)
        assert save_res is True
        assert os.path.exists(json_file)

        loaded = dp.load_tasks()
        assert len(loaded) == 3
        assert isinstance(loaded[0], Task) and not isinstance(loaded[0], DueDateTask)
        assert loaded[0].description == "Base task"
        assert loaded[0].tags == ["base", "test"]

        assert isinstance(loaded[1], DueDateTask)
        assert loaded[1].due_date.strftime("%Y-%m-%d") == "2026-11-20"
        assert loaded[1].completed is True

        assert isinstance(loaded[2], PriorityTask)
        assert loaded[2].priority == "High"

    def test_missing_file_returns_empty_list(self, tmp_path):
        json_file = str(tmp_path / "nonexistent" / "tasks.json")
        dp = DataPersistence(json_file)
        loaded = dp.load_tasks()
        assert loaded == []

    def test_empty_file_returns_empty_list(self, tmp_path):
        json_file = tmp_path / "empty.json"
        json_file.write_text("", encoding="utf-8")
        dp = DataPersistence(str(json_file))
        assert dp.load_tasks() == []

    def test_backward_compatibility_missing_tags(self, tmp_path):
        json_file = tmp_path / "legacy.json"
        legacy_data = [
            {
                "id": 1,
                "description": "Old task without tags",
                "completed": False,
                "_type": "Task"
            },
            {
                "id": 2,
                "description": "Old due date task",
                "due_date": "2026-10-10",
                "completed": True,
                "_type": "DueDateTask"
            }
        ]
        json_file.write_text(json.dumps(legacy_data), encoding="utf-8")
        dp = DataPersistence(str(json_file))
        loaded = dp.load_tasks()
        assert len(loaded) == 2
        assert loaded[0].tags == []
        assert loaded[1].tags == []

    def test_corrupted_json_preserves_backup_and_returns_empty(self, tmp_path):
        json_file = tmp_path / "corrupted.json"
        json_file.write_text("{ this is not valid json :", encoding="utf-8")
        dp = DataPersistence(str(json_file))
        loaded = dp.load_tasks()
        assert loaded == []
        # Check backup file exists
        backup = tmp_path / "corrupted.json.corrupted.bak"
        assert backup.exists()

    def test_unknown_task_type_skipped(self, tmp_path):
        json_file = tmp_path / "tasks.json"
        data = [
            {"id": 1, "description": "Good task", "completed": False, "_type": "Task", "tags": []},
            {"id": 2, "description": "Unknown task", "completed": False, "_type": "FutureTask", "tags": []},
        ]
        json_file.write_text(json.dumps(data), encoding="utf-8")
        dp = DataPersistence(str(json_file))
        loaded = dp.load_tasks()
        assert len(loaded) == 1
        assert loaded[0].id == 1
