"""
Unit and integration tests for CLIInterface in src/cli_interface.py.
Mocks user input and checks console outputs.
"""

from unittest.mock import patch
import pytest

from src.task_manager import TaskManager
from src.cli_interface import CLIInterface


class TestCLIInterface:
    @pytest.fixture
    def setup_cli(self, tmp_path):
        json_file = str(tmp_path / "cli_test_tasks.json")
        manager = TaskManager(data_file=json_file)
        cli = CLIInterface(manager)
        return cli, manager

    def test_add_normal_task_flow(self, setup_cli, capsys):
        cli, manager = setup_cli
        # Inputs: choice 1, description, tags, choice 0 (exit)
        inputs = ["1", "Write documentation", "docs, python", "0"]
        with patch("builtins.input", side_effect=inputs):
            cli.run()

        captured = capsys.readouterr().out
        assert "Normal Task 'Write documentation' added with ID 1." in captured
        tasks = manager.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0].tags == ["docs", "python"]

    def test_add_due_date_task_flow(self, setup_cli, capsys):
        cli, manager = setup_cli
        # Inputs: choice 2, description, due_date, tags, choice 0 (exit)
        inputs = ["2", "Submit project", "2026-11-30", "exam", "0"]
        with patch("builtins.input", side_effect=inputs):
            cli.run()

        captured = capsys.readouterr().out
        assert "Due Date Task 'Submit project' (Due: 2026-11-30) added with ID 1." in captured

    def test_add_priority_task_flow(self, setup_cli, capsys):
        cli, manager = setup_cli
        # Inputs: choice 3, description, priority, tags, choice 0 (exit)
        inputs = ["3", "Urgent bug fix", "high", "urgent", "0"]
        with patch("builtins.input", side_effect=inputs):
            cli.run()

        captured = capsys.readouterr().out
        assert "Priority Task 'Urgent bug fix' (Priority: High) added with ID 1." in captured

    def test_list_complete_and_delete_flow(self, setup_cli, capsys):
        cli, manager = setup_cli
        manager.add_normal_task("Sample Task")

        # Inputs: choice 4 (list), choice 5 (complete id 1), choice 6 (delete id 1), choice 0 (exit)
        inputs = ["4", "5", "1", "6", "1", "0"]
        with patch("builtins.input", side_effect=inputs):
            cli.run()

        captured = capsys.readouterr().out
        assert "--- Your Tasks ---" in captured
        assert "Task marked as completed." in captured
        assert "Task deleted successfully." in captured

    def test_search_tasks_flow(self, setup_cli, capsys):
        cli, manager = setup_cli
        manager.add_normal_task("Buy milk", tags=["grocery"])

        # Inputs: choice 7 (search), keyword "GROCERY", choice 0 (exit)
        inputs = ["7", "GROCERY", "0"]
        with patch("builtins.input", side_effect=inputs):
            cli.run()

        captured = capsys.readouterr().out
        assert "Search Results for 'GROCERY'" in captured
        assert "Buy milk" in captured

    def test_filter_and_sort_flow(self, setup_cli, capsys):
        cli, manager = setup_cli
        manager.add_normal_task("Pending Task", tags=["work"])
        t2 = manager.add_priority_task("Urgent Task", "High", tags=["work"])
        manager.complete_task(t2.id)

        # Filter: choice 8, status "yes", before "", after "", priority "", tags "work"
        # Sort: choice 9, criterion "id", reverse "no"
        # Exit: choice 0
        inputs = [
            "8", "yes", "", "", "", "work",
            "9", "id", "no",
            "0"
        ]
        with patch("builtins.input", side_effect=inputs):
            cli.run()

        captured = capsys.readouterr().out
        assert "Filtered Tasks" in captured
        assert "Urgent Task" in captured
        assert "Sorted Tasks by id (Ascending)" in captured

    def test_graceful_exit_and_invalid_choices(self, setup_cli, capsys):
        cli, manager = setup_cli
        # Invalid choice "99", then exit "0"
        inputs = ["99", "0"]
        with patch("builtins.input", side_effect=inputs):
            cli.run()

        captured = capsys.readouterr().out
        assert "Invalid choice. Please enter a number between 0 and 9." in captured
        assert "Exiting Task Manager. Goodbye!" in captured
