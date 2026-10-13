import unittest
import os
import sys
import tempfile
import shutil
import datetime

# Ensure src can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from task import Task, DueDateTask, PriorityTask
from data_persistence import DataPersistence
from task_manager import TaskManager


class TestTaskManagerDesign(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_json = os.path.join(self.test_dir, 'tasks.json')

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_task_models(self):
        # Normal Task
        t1 = Task(1, "Task 1", completed=False, tags=["work"])
        self.assertEqual(t1.id, 1)
        self.assertEqual(t1.description, "Task 1")
        self.assertFalse(t1.completed)
        self.assertIn("work", t1.tags)
        t1.mark_complete()
        self.assertTrue(t1.completed)
        t1.add_tag("urgent")
        self.assertIn("urgent", t1.tags)
        t1.remove_tag("work")
        self.assertNotIn("work", t1.tags)
        
        t1_dict = t1.to_dict()
        self.assertEqual(t1_dict["_type"], "Task")
        self.assertTrue(t1_dict["completed"])
        self.assertEqual(t1_dict["tags"], ["urgent"])
        self.assertIn("Completed", str(t1))
        self.assertIn("Task(", repr(t1))

        # DueDateTask
        t2 = DueDateTask(2, "Task 2", due_date="2026-12-31", tags=["home"])
        self.assertEqual(t2.due_date, datetime.date(2026, 12, 31))
        t2_dict = t2.to_dict()
        self.assertEqual(t2_dict["_type"], "DueDateTask")
        self.assertEqual(t2_dict["due_date"], "2026-12-31")
        self.assertIn("Due: 2026-12-31", str(t2))
        self.assertIn("DueDateTask(", repr(t2))

        # PriorityTask
        t3 = PriorityTask(3, "Task 3", priority="High", tags=["study"])
        self.assertEqual(t3.priority, "High")
        t3_dict = t3.to_dict()
        self.assertEqual(t3_dict["_type"], "PriorityTask")
        self.assertEqual(t3_dict["priority"], "High")
        self.assertIn("Priority: High", str(t3))
        self.assertIn("PriorityTask(", repr(t3))

    def test_persistence_and_manager(self):
        # Test TaskManager using custom data file
        # Relative path resolution from DataPersistence points to ../<data_file>
        # Let's test DataPersistence directly with isolated file
        persistence = DataPersistence()
        persistence._data_file_path = self.test_json

        t1 = Task(1, "Test 1", tags=["a"])
        t2 = DueDateTask(2, "Test 2", due_date="2025-05-01", tags=["b"])
        t3 = PriorityTask(3, "Test 3", priority="Medium", tags=["c"])

        persistence.save_tasks([t1, t2, t3])
        self.assertTrue(os.path.exists(self.test_json))

        loaded = persistence.load_tasks()
        self.assertEqual(len(loaded), 3)
        self.assertIsInstance(loaded[0], Task)
        self.assertIsInstance(loaded[1], DueDateTask)
        self.assertIsInstance(loaded[2], PriorityTask)
        self.assertEqual(loaded[1].due_date, datetime.date(2025, 5, 1))
        self.assertEqual(loaded[2].priority, "Medium")

    def test_task_manager_operations(self):
        mgr = TaskManager()
        mgr.persistence._data_file_path = self.test_json
        mgr.tasks = []
        mgr.next_id = 1

        # Add tasks
        task1 = mgr.add_normal_task("Normal task", tags=["daily"])
        self.assertEqual(task1.id, 1)
        self.assertEqual(len(mgr.tasks), 1)

        task2 = mgr.add_due_date_task("Due task", "2025-01-01", tags=["deadline"])
        self.assertEqual(task2.id, 2)
        self.assertEqual(len(mgr.tasks), 2)

        task3 = mgr.add_priority_task("Priority task", "High", tags=["important"])
        self.assertEqual(task3.id, 3)
        self.assertEqual(len(mgr.tasks), 3)

        # Complete task
        success, msg = mgr.complete_task(1)
        self.assertTrue(success)
        self.assertTrue(task1.completed)

        # Complete already completed task
        success, msg = mgr.complete_task(1)
        self.assertFalse(success)

        # Complete non-existent task
        success, msg = mgr.complete_task(99)
        self.assertFalse(success)

        # Delete task
        success, msg = mgr.delete_task(2)
        self.assertTrue(success)
        self.assertEqual(len(mgr.tasks), 2)

        # Delete non-existent task
        success, msg = mgr.delete_task(99)
        self.assertFalse(success)

        # Placeholder methods (should not crash)
        search_res = mgr.search_tasks("test")
        self.assertEqual(search_res, [])

        filter_res = mgr.filter_tasks()
        self.assertEqual(filter_res, [])

        sort_res = mgr.sort_tasks()
        self.assertEqual(len(sort_res), 2)


if __name__ == '__main__':
    unittest.main()
