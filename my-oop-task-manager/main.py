import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.task_manager import TaskManager

def display_menu():
    print("\n--- OOP Task Manager Menu ---")
    print("1. Add Task")
    print("2. List Tasks")
    print("3. Complete Task")
    print("4. Delete Task")
    print("5. Exit")

def main():
    manager = TaskManager()
    while True:
        display_menu()
        choice = input("Enter your choice (1-5): ").strip()
        if choice == '1':
            desc = input("Enter task description: ").strip()
            if desc:
                manager.add_task(desc)
        elif choice == '2':
            manager.list_tasks()
        elif choice == '3':
            try:
                manager.complete_task(int(input("Enter ID of task to complete: ").strip()))
            except ValueError:
                print("Invalid input.")
        elif choice == '4':
            try:
                manager.delete_task(int(input("Enter ID of task to delete: ").strip()))
            except ValueError:
                print("Invalid input.")
        elif choice == '5':
            print("Exiting Task Manager.")
            break

if __name__ == "__main__":
    main()