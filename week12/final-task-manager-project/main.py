"""
Enhanced Task Manager CLI Application
Main Entry Point.
"""

import sys
import os

# Ensure package and module imports work seamlessly whether executed as
# `python main.py` or imported as a package.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.task_manager import TaskManager
from src.cli_interface import CLIInterface


def main() -> None:
    """
    Main entry point for the Enhanced Task Manager application.
    Initializes TaskManager and CLIInterface, then starts the CLI loop.
    """
    try:
        manager = TaskManager()  # Initialize business logic manager with data persistence
        cli = CLIInterface(manager)  # Initialize user interface
        cli.run()  # Start the command-line interaction loop
    except Exception as e:
        print(f"A fatal error occurred while running Task Manager: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
