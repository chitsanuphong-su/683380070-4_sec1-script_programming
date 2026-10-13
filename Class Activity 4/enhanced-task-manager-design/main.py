# enhanced-task-manager-design/main.py
import sys
import os

# Add the 'src' directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the main components of our application
from task_manager import TaskManager
from cli_interface import CLIInterface


def main():
    """
    Main entry point for the Enhanced Task Manager application.
    Initializes TaskManager and CLIInterface, then starts the CLI loop.
    """
    manager = TaskManager()  # Initialize the core logic manager
    cli = CLIInterface(manager)  # Initialize the CLI interface, passing the manager
    cli.run()  # Start the main command-line interaction loop


if __name__ == "__main__":
    main()
